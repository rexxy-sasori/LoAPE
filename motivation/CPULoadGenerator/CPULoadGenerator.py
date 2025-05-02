import multiprocessing
from twisted.python import usage

import sys
sys.path.insert(0, 'utils')

class Options(usage.Options):
    """
       Defines the default input parameters
    """
    optParameters = [
            ["cpuLoad", "l", 0.4, "Cpu Target Load", float],
            ["duration", "d", 20, "Duration", int],
            ["plot", "p" , 0, "Enable Plot", int],
            ["cpu_core", "c" , 0, "Select the CPU on which generate the load", int]
        ]

import time

class realTimePlot():
    """
        Plots the CPU load
    """
    def __init__(self, duration, cpu, target):
        plt.figure()
        plt.axis([0, duration, 0, 100])
        plt.ion()
        plt.show()
        plt.xlabel('Time(sec)')
        plt.ylabel('%')
        self.y_load = [0]
        self.cpuT = target;
        self.y_target = [0]
        self.xdata = [0]
        self.line_load, = plt.plot(self.y_load)
        self.line_target, = plt.plot(self.y_target)
        if target != 0:
            plt.legend([self.line_target, self.line_load], ["Target CPU", "CPU [%d] Load" % (cpu)], ncol=2)
        else:
            plt.legend([self.line_load], ["CPU [%d] Load" % (cpu)], ncol=1)
        plt.grid(True)
        self.ts_start = time.time()

    def plotSample(self, sample, target):
        p_x = time.time() - self.ts_start
        p_load = sample
        self.xdata.append(p_x)
        if target != 0:
            p_target = target
            self.y_target.append(p_target)
            self.line_target.set_xdata(self.xdata)
            self.line_target.set_ydata(self.y_target)
        self.y_load.append(p_load)
        self.line_load.set_xdata(self.xdata)
        self.line_load.set_ydata(self.y_load)
        plt.draw()

    def close(self):
        if self.cpuT != 0:
            name = "%d%%-Target-Load" % (self.cpuT*100)+ ".png"
            plt.savefig(name, dpi=100)
        plt.close();                    

class closedLoopActuator():
    """
        Generates CPU load by tuning the sleep time
    """

    def __init__(self, controller, monitor, duration, cpu_core, target, plot):
        self.controller = controller
        self.monitor = monitor
        self.duration = duration
        self.plot = plot
        self.target = target
        self.controller.setCpu(self.monitor.getCpuLoad())
        self.period = 0.05  # actuation period  in seconds
        self.last_plot_time = time.time()
        self.start_time = time.time()
        if self.plot:
            self.graph = realTimePlot(self.duration, cpu_core, target)

    def generate_load(self, sleep_time):
        interval = time.time() + self.cycle - sleep_time
        # generates some getCpuLoad for interval seconds
        while (time.time() < interval):
            pr = 213123  # generates some load
            pr * pr
            pr = pr + 1
        time.sleep(sleep_time)  # controller actuation

    def sendPlotSample(self):
        if self.plot:
            if (time.time() - self.last_plot_time) > 0.2:
                self.graph.plotSample(self.controller.getCpu(), self.controller.getCpuTarget() * 100)
                self.last_plot_time = time.time()

    def close(self):
        if self.plot:
            self.graph.close()

    def generate_load(self, sleep_time):
        interval = time.time() + self.period - sleep_time
        # generates some getCpuLoad for interval seconds
        while (time.time() < interval):
            pr = 213123  # generates some load
            pr * pr
            pr = pr + 1

        time.sleep(sleep_time)

    def run(self):
        while (time.time() - self.start_time) <= self.duration:
            self.controller.setCpu(self.monitor.getCpuLoad())
            sleep_time = self.controller.getSleepTime()
            self.generate_load(sleep_time)
            self.sendPlotSample()
                                                                                                                                                                                                            1,1           Top

class MonitorThread(threading.Thread):
    """
       Monitors the CPU status
    """
    def __init__(self, cpu_core, interval):
        self.sampling_interval = interval; # sample time interval
        self.sample = 0.5; # cpu load measurement sample
        self.cpu = 0.5; # cpu load filtered
        self.running = 1; # thread status
        self.alpha = 1; # filter coefficient
        self.sleepTimeTarget = 0.03
        self.sleepTime = 0.03
        self.cpuTarget = 0.5
        self.cpu_core = cpu_core
        self.dynamics = {"time":[], "cpu":[], "sleepTimeTarget":[], "cpuTarget":[],  "sleepTime":[],}
        super(MonitorThread, self).__init__()

    def getCpuLoad(self):
        return self.cpu

    def setSleepTimeTarget(self, sleepTimeTarget):
        self.sleepTimeTarget = sleepTimeTarget

    def setSleepTime(self, sleepTime):
        self.sleepTime = sleepTime

    def setCPUTarget(self, cpuTarget):
        self.cpuTarget = cpuTarget

    def getDynamics(self):
        return self.dynamics

    def run(self):
        start_time = time.time()
        p = psutil.Process(os.getpid())
        try:
            p.set_cpu_affinity([self.cpu_core]) #the process is forced to run only on the selected CPU
        except AttributeError:
            p.cpu_affinity([self.cpu_core])

        while self.running:
            try:
               self.sample = p.get_cpu_percent(self.sampling_interval)
            except AttributeError:
               self.sample = p.cpu_percent(self.sampling_interval)

            self.cpu = self.alpha * self.sample + (1 - self.alpha)*self.cpu # first order filter on the measurement samples
            #self.cpu_log.append(self.cpu)
            self.dynamics['time'].append(time.time() - start_time)
            self.dynamics['cpu'].append(self.cpu)
            self.dynamics['sleepTimeTarget'].append(self.sleepTimeTarget)
            self.dynamics['sleepTime'].append(self.sleepTime)
            self.dynamics['cpuTarget'].append(self.cpuTarget)

import threading
import time

class ControllerThread(threading.Thread):
    """
        Controls the CPU status
    """
    def __init__(self, interval, ki = None, kp = None):
        self.running = 1;  # thread status
        self.sampling_interval = interval
        self.period = 0.1 # actuation period  in seconds
        self.sleepTime = 0.02; # this is controller output: determines the sleep time to achieve the requested CPU load
        self.alpha = 0.2; # filter coefficient
        self.CT = 0.20;  # target CPU load should be provided as input
        self.cpu = 0;   # current CPU load returned from the Monitor thread
        self.cpuPeriod = 0.03;
        if ki is None:
          self.ki = 0.2   # integral constant of th PI regulator
        if kp is None:
          self.kp = 0.02  # proportional constant of th PI regulator
        self.int_err = 0;  # integral error
        self.last_ts = time.time();  # last sampled time
        super(ControllerThread, self).__init__()

    def getSleepTime(self):
        return self.sleepTime

    def cpu_model(self, cpu_period):
      sleepTime = self.period - cpu_period
      return sleepTime

    def getCpuTarget(self):
        return self.CT

    def setCpu(self, cpu):
       self.cpu = self.alpha * cpu + (1 - self.alpha)*self.cpu # first order filter on the measurement samples

    def getCpu(self):
       return self.cpu

    def setCpuTarget(self, CT):
       self.CT = CT

    def run(self):
        while self.running:
          # ControllerThread has to have the same sampling interval as MonitorThread
          time.sleep(self.sampling_interval)
          self.err = self.CT - self.cpu*0.01  # computes the proportional error
          ts = time.time()

          samp_int = ts - self.last_ts  # sample interval
          self.int_err = self.int_err + self.err*samp_int  # computes the integral error
          self.last_ts = ts
          self.cpuPeriod = self.kp*self.err  + self.ki*self.int_err

          #anti wind up control
          if self.cpuPeriod < 0:
            self.cpuPeriod = 0

if __name__ == "__main__":

    import sys
    options = Options()
    try:
        options.parseOptions()
    except Exception as e:
        print ('%s: %s' % (sys.argv[0], e))
        print ('%s: Try --help for usage details.' % (sys.argv[0]))
        sys.exit(1)
    else:
        if options['cpuLoad'] < 0 or options['cpuLoad'] > 1:
            print ("CPU target load out of the range [0,1]")
            sys.exit(1)
        if options['duration'] < 0:
            print ("Invalid duration")
            sys.exit(1)
        if options['plot'] != 0 and options['plot'] != 1:
            print ("plot can be enabled 1 or disabled 0")
            sys.exit(1)
        if options['cpu_core'] >= multiprocessing.cpu_count():
            print ("You have only %d cores on your machine" % (multiprocessing.cpu_count()))
            sys.exit(1)

    monitor = MonitorThread(options['cpu_core'], 0.1)
    monitor.start()

    control = ControllerThread(0.1)
    control.start()
    control.setCpuTarget(options['cpuLoad'])

    actuator = closedLoopActuator(control, monitor, options['duration'], options['cpu_core'], options['cpuLoad'], options['plot'])
    actuator.run()
    actuator.close()
