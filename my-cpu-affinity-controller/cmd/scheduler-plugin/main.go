package main

import (
	"context"
	"flag"
	"os"
	"k8s.io/apimachinery/pkg/runtime"
	"k8s.io/kubernetes/cmd/kube-scheduler/app"
	"k8s.io/kubernetes/pkg/scheduler/framework"
	klog "k8s.io/klog/v2"

	// Import your custom plugin package
	"github.com/rexxy-sasori/my-cpu-affinity-controller/pkg/schedulerplugin"
)

func main() {
	// Define command line flags
	var namespace string
	flag.StringVar(&namespace, "namespace", "default", "Target namespace for the scheduler plugin")
	
	// Initialize klog flags
	klog.InitFlags(nil)
	
	// Parse all flags
	flag.Parse()
	
	klog.Infof("Using namespace: %s", namespace)

	// Create a plugin factory function that matches the expected signature
	pluginFactory := func(ctx context.Context, obj runtime.Object, handle framework.Handle) (framework.Plugin, error) {
		return schedulerplugin.New(obj, handle, namespace)
	}

	// Create a new scheduler command with the CPU affinity plugin
	command := app.NewSchedulerCommand(
		app.WithPlugin(schedulerplugin.PluginName, pluginFactory),
	)

	// Execute the scheduler command
	if err := command.Execute(); err != nil {
		klog.ErrorS(err, "Failed to run scheduler")
		os.Exit(1)
	}

	// Flush klog buffers before exiting
	klog.Flush()
}