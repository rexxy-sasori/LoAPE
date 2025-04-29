package main

import (
    "context"
    "flag"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "k8s.io/client-go/kubernetes"
    "k8s.io/client-go/rest"
    klog "k8s.io/klog/v2"

    "k8s.io/client-go/tools/cache"
    "github.com/prometheus/client_golang/prometheus/promhttp"
    "github.com/rexxy-sasori/my-cpu-affinity-controller/pkg/nodeagent"
)

func main() {
    klog.InitFlags(nil)
    var targetNamespace string
    var resyncPeriod time.Duration
    var deletionCostAdjustmentPeriod time.Duration
    var collectTrainingDataPeriod time.Duration
    var perfSamplePeriod string

    flag.StringVar(&targetNamespace, "namespace", "default", "The target namespace to operate on")
    flag.StringVar(&perfSamplePeriod, "perf-sample-period-ms", "2000", "sampling period for perf in millisecond")
    flag.DurationVar(&resyncPeriod, "resync-period", time.Minute*10, "Resync period for the informer factory")
    flag.DurationVar(&deletionCostAdjustmentPeriod, "adjust-deletion-cost-period", time.Minute*10, "Time period to update pod's deletion cost")
    flag.DurationVar(&collectTrainingDataPeriod, "collect-training-data-period", time.Minute*1, "Time period to enforce cpu cores to collect for training data")
    
    flag.Parse()

    // Use in-cluster configuration
    config, err := rest.InClusterConfig()
    if err != nil {
        klog.Fatalf("Error building in-cluster config: %v", err)
    }

    // Create Kubernetes clients
    clientset, err := kubernetes.NewForConfig(config)
    if err != nil {
        klog.Fatalf("Error building kubernetes clientset: %v", err)
    }

    // Get the node name from the environment
    nodeName := os.Getenv("NODE_NAME")
    if nodeName == "" {
        klog.Fatal("NODE_NAME environment variable must be set")
    }

    // Create the informer factory and node agent
    agent := nodeagent.NewAgent(clientset, nodeName, targetNamespace, perfSamplePeriod, resyncPeriod)

    // Create a context that cancels on SIGTERM or SIGINT
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()

    go agent.Run(ctx, deletionCostAdjustmentPeriod, collectTrainingDataPeriod)

    if !cache.WaitForCacheSync(ctx.Done(), agent.PodInformer.HasSynced, agent.NodeInformer.HasSynced) {
        klog.Fatalf("Failed to sync caches")
    }

    // Create an HTTP server for metrics
    server := &http.Server{
        Addr:    ":8080",
        Handler: promhttp.Handler(),
    }

    // Start the HTTP server in a goroutine
    go func() {
        klog.Info("Starting HTTP server on :8080")
        if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            klog.Fatalf("HTTP server error: %v", err)
        }
    }()

    // Set up signal handling for graceful shutdown
    stopChan := make(chan os.Signal, 1)
    signal.Notify(stopChan, syscall.SIGTERM, syscall.SIGINT)

    // Wait for a termination signal
    sig := <-stopChan
    klog.Infof("Received signal: %v. Shutting down gracefully...", sig)

    // Cancel the context to stop all background processes
    cancel()

    // Shut down the HTTP server gracefully
    shutdownCtx, shutdownCancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer shutdownCancel()

    if err := server.Shutdown(shutdownCtx); err != nil {
        klog.Errorf("Error shutting down HTTP server: %v", err)
    } else {
        klog.Info("HTTP server shut down gracefully")
    }

    // Wait for all resources to be cleaned up
    klog.Info("Shutdown complete. Exiting.")
}