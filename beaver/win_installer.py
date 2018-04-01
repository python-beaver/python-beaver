'''
Installs Beaver service in windows platform.

'''
from os.path import splitext, abspath
from sys import modules
import win32serviceutil
import win32service
import win32api
import win32event
import time
import winerror

def install_start_service(cls, name, display_name=None, stay_alive=True):
    ''' Install and  Start (auto) a Service
        cls : the class (derived from Service) that implement the Service
        name : Service name
        display_name : the name displayed in the service manager
        stay_alive : Service will stop on logout if False
    '''
    cls._svc_name_ = name
    cls._svc_display_name_ = display_name or name
    try:
        module_path=modules[cls.__module__].__file__
    except AttributeError:
        # maybe py2exe went by
        from sys import executable
        module_path=executable
    module_file = splitext(abspath(module_path))[0]
    cls._svc_reg_class_ = '%s.%s' % (module_file, cls.__name__)
    if stay_alive: win32api.SetConsoleCtrlHandler(lambda x: True, True)
    try:
        win32serviceutil.InstallService(
            cls._svc_reg_class_,
            cls._svc_name_,
            cls._svc_display_name_,
            startType = win32service.SERVICE_AUTO_START
        )

        win32serviceutil.StartService(
            cls._svc_name_
        )
    except Exception, mesg:
        print str(mesg)

def stop_delete_service(service_name):
    '''
    Checks if the service is installed as running.
    If it is running, it will stop it.
    If it is stopped, then it will delete it.
    '''

    hscm = win32service.OpenSCManager(None,None,win32service.SC_MANAGER_ALL_ACCESS)

    try:
        win32service.OpenService(hscm, service_name, win32service.SERVICE_ALL_ACCESS)
        # Already installed
        status = win32serviceutil.QueryServiceStatus(service_name)
        if status[1] == 4:
            # Stop the service
            win32serviceutil.StopService(service_name)
        time.sleep(3)
        #delete the service
        win32serviceutil.RemoveService(service_name)
        time.sleep(3)
        return True

    except win32api.error, details:
        if details[0] !=winerror.ERROR_SERVICE_DOES_NOT_EXIST:
            print service_name + "is not being installed properly but have other problem."
            return False
        else:
            # Service is not being installed and ready for fresh installtion
            return True

