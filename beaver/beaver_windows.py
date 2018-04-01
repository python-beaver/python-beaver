'''
Python service wrapper for Beaver Service.

'''
import win32service
import win32serviceutil
import win32event
import servicemanager
import subprocess
import profile
import time
import sys
import os
from win32process import DETACHED_PROCESS


class BeaverWindowsService(win32serviceutil.ServiceFramework):

    _svc_name_ = "Beaver Service"
    _svc_display_name_ = "Beaver Service"
    _svc_description_ = "Beaver Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.proc = None
        self.timeout = 5000
        self.DETACHED_PROCESS = 8
        exe_path = sys.executable
        python_dir= exe_path.split("lib\\site-packages")[0]
        python_dir= python_dir.split("python.exe")[0]
        self.python_path = python_dir+"python.exe"
        self.beaver_bin_path = python_dir+"Scripts\\beaver"
        self.config_path = python_dir+ "etc\\beaver\\beaver.conf"

    def SvcStop(self):

        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.proc.kill()
        time.sleep(2)
        cmd = 'WMIC Process where "Caption like \'python.exe\' and Commandline like \'%--multiprocessing-fork%\'" get Processid'
        cmd_proc = subprocess.Popen(cmd,stdout=subprocess.PIPE)
        for line in cmd_proc.stdout:
            line = line.replace('\t','').replace('\n','').replace(' ','',20)
            line = line[:-2]
            if line.isdigit():
                subprocess.call(['taskkill', '/F', '/T', '/PID', line])

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,servicemanager.PYS_SERVICE_STARTED,(self._svc_name_, ''))
        rc = None
        self.proc = subprocess.Popen([self.python_path, "-m", "profile", self.beaver_bin_path, "-c", self.config_path],creationflags=self.DETACHED_PROCESS)
        time.sleep(5)
        while self.proc.poll() == None:
            # Wait for service stop signal, if I timeout, loop again
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
            # Check to see if self.hWaitStop happened
            if rc == win32event.WAIT_OBJECT_0:
                self.SvcStop()
                break
        else:
            self.SvcStop()
        f.close()

