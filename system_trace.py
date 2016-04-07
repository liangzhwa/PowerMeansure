import re
import fmbtandroid
import os
import PT_Wrap as wrap
#***********************************************************************************#

def topAppPID(d):
    s_top=d.topApp()
    if not s_top:
        return None

    app = s_top.split(r'/')[0]
    print "Search for topApp %s" % app
    ps_list = d.shell('ps')
    ps_list = ps_list.split('\n')
    pid_list=[]
    for i in ps_list:
        app_entry = re.search(app, i)
        if app_entry is None:
            continue
        print "Found app entry for topApp %s: %s" % (app, i)
        pid = i.split()[1]
        desc = i.split()[8]
        print "Found app PID for topApp %s: %s" %(app, pid)
        pid_list.append((desc, int(pid)))

    if not pid_list:
        print "ERROR: PID for topApp %s not found" % app
        return None
    print "Found topApp %s: %s" % (app, pid_list)
    return pid_list

def __test_topAppPID():
    d=fmbtandroid.Device()
    app_pid_list = topAppPID(d)
    for i in app_pid_list:
        print "app name=%s, app pid=%s" %(i[0],i[1])

#***********************************************************************************#
targetCasePath = '/data/local/tmp'
def_trace_file=targetCasePath + r'/mytrace.txt'

def DisableUXTune(dev, TraceFile=None):
    if TraceFile is None:
        TraceFile = def_trace_file
    mUXTuneCmdList_disable =[ \
            ##old version before kernel3.4
            #r'echo 0 > /sys/kernel/debug/tracing/set_event', \
            #r'echo 0 > /sys/kernel/debug/tracing/tracing_enabled', \
            #r'cat /sys/kernel/debug/tracing/trace > ' + TraceFile, \

            r'echo > /sys/kernel/debug/tracing/set_event', \
            r'echo 0 > /sys/kernel/debug/tracing/tracing_on', \
            r'cat /sys/kernel/debug/tracing/trace > ' + TraceFile, \
            ]

    for cmd in mUXTuneCmdList_disable:
        dev.shell(cmd)
    os.system("./UXTune2/timechart/script/uxtune-record.sh stop")
    return

def EnableUXTune(dev, TraceFile=None):
    if TraceFile is None:
        TraceFile = def_trace_file
    mUXTuneCmdList_enable =[ \
            ##old version before kernel3.4
            #r'rm ' + TraceFile, \
            #r'chmod 222 /sys/kernel/debug/tracing/trace_marker', \
            #r'echo 0 > /sys/kernel/debug/tracing/events/irq/enable', \
            #r'echo 0 > /sys/kernel/debug/tracing/events/timer/enable', \
            #r'echo 0 > /sys/kernel/debug/tracing/events/power/runtime_pm_usage/enable', \
            #r'mount -t debugfs none /sys/kernel/debug 2>/dev/null', \
            #r'echo 20000 > /sys/kernel/debug/tracing/buffer_size_kb', \
            #r'echo nop > /sys/kernel/debug/tracing/current_tracer', \
            #r'echo sched:sched_wakeup > /sys/kernel/debug/tracing/set_event', \
            #r'echo sched:sched_switch >> /sys/kernel/debug/tracing/set_event', \
            #r'echo timer:timer_init >> /sys/kernel/debug/tracing/set_event', \
            #r'echo timer:timer_start >> /sys/kernel/debug/tracing/set_event', \
            #r'echo timer:timer_expire_entry >> /sys/kernel/debug/tracing/set_event', \
            #r'echo timer:timer_expire_exit >> /sys/kernel/debug/tracing/set_event', \
            #r'echo timer:hrtimer_start >> /sys/kernel/debug/tracing/set_event', \
            #r'echo timer:hrtimer_expire_entry >> /sys/kernel/debug/tracing/set_event', \
            #r'echo timer:hrtimer_expire_exit >> /sys/kernel/debug/tracing/set_event', \
            #r'echo timer:itimer_expire >> /sys/kernel/debug/tracing/set_event', \
            #r'echo workqueue:workqueue_execution >> /sys/kernel/debug/tracing/set_event', \
            #r'echo workqueue:workqueue_execution_end >> /sys/kernel/debug/tracing/set_event', \
            #r'echo power:* >> /sys/kernel/debug/tracing/set_event', \
            #r'echo irq:* >> /sys/kernel/debug/tracing/set_event', \
            #r'echo drm:drm_vblank_event >> /sys/kernel/debug/tracing/set_event', \
            #r'echo 1 > /sys/kernel/debug/tracing/trace', \
            #r'echo 1 > /sys/kernel/debug/tracing/tracing_enabled', \

            r'rm ' + TraceFile, \
            r'mount -t debugfs none /sys/kernel/debug 2>/dev/null', \
            r'echo 12800 > /sys/kernel/debug/tracing/buffer_size_kb', \
            r'echo nop > /sys/kernel/debug/tracing/current_tracer', \
            r'echo noirq-info > /sys/kernel/debug/tracing/trace_options', \
            r'echo 1 > /sys/kernel/debug/tracing/events/sched/sched_wakeup/enable', \
            r'echo 1 > /sys/kernel/debug/tracing/events/sched/sched_switch/enable', \
            r'echo 1 > /sys/kernel/debug/tracing/events/power/enable', \
            r'echo 1 > /sys/kernel/debug/tracing/events/drm/drm_vblank_event/enable', \
            r'echo > /sys/kernel/debug/tracing/trace', \
            r'echo 1 > /sys/kernel/debug/tracing/tracing_on', \
            ]
    for cmd in mUXTuneCmdList_enable:
        dev.shell(cmd)
    print os.getcwd()
    os.system("./UXTune2/timechart/script/uxtune-record.sh init")
    os.system("./UXTune2/timechart/script/uxtune-record.sh start")
    return

def StartMeasurePower():
    wrap.MeansureStart()
    
def EndMeasurePower():
    tempReportPath = '/home/xueyunlong/tmp/tempPowerData.csv'
    wrap.MeansureEnd(0,tempReportPath)
    
def AnalyzeUXTune(dev, TraceFile=None):
    if TraceFile is None:
        TraceFile = def_trace_file
    os.system("python UXTune2/uxtune2.py UXTune2/trace.txt")
    ##TODO

