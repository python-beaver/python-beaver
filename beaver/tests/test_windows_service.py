'''
Testcase for verifying windows service
'''
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import os
import win32service
import win32serviceutil
import beaver.win_installer as installer
from beaver.beaver_windows import BeaverWindowsService as bws


if os.name == 'nt':
    skip = False
else:
    skip = True


@unittest.skipIf(skip, 'Not a Windows OS')
class WindowsServiceTest(unittest.TestCase):

    def test_service_running(self):
        if installer.stop_delete_service("Beaver Service"):
            installer.install_start_service(bws, self.service_name, self.service_name, True)
        scvType, svcState, svcControls, err, svcErr, svcCP, svcWH = \
            win32serviceutil.QueryServiceStatus("Beaver Service")
        self.assertEqual(svcState, win32service.SERVICE_RUNNING)

    def test_service_stopped(self):
        scvType, svcState, svcControls, err, svcErr, svcCP, svcWH = \
            win32serviceutil.QueryServiceStatus("Beaver Service")
        if svcState ==  win32service.SERVICE_RUNNING:
            installer.stop_delete_service("Beaver Service")
        scvType, svcState, svcControls, err, svcErr, svcCP, svcWH = \
            win32serviceutil.QueryServiceStatus("Beaver Service")
        self.assertNotEqual(svcState, win32service.SERVICE_RUNNING)
