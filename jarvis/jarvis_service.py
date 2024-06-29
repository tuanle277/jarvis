import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import os
import sys
import logging

class JarvisService(win32serviceutil.ServiceFramework):
    _svc_name_ = "JarvisService"
    _svc_display_name_ = "Jarvis Voice Assistant Service"
    _svc_description_ = "A service that runs the Jarvis voice assistant."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_running = True

        logging.basicConfig(
            filename='jarvis_service.log',  # Ensure this path is correct
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, "")
        )

        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.main()

    def main(self):
        logging.info('Jarvis Service is starting.')
        while self.is_running:
            try:
                os.system(f'python {os.path.abspath("jarvis.py")}')
                win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            except Exception as e:
                logging.error(f'Error running jarvis.py: {e}')
                self.is_running = False

        logging.info('Jarvis Service is stopping.')

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(JarvisService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(JarvisService)
