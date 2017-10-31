import unittest
try:
    from unittest.mock import MagicMock
    from unittest.mock import patch
except:
    from mock import MagicMock
    from mock import patch

import tests.obj_data
from bluezero import constants

from gi.repository.GLib import Variant

class TestDbusModuleCalls(unittest.TestCase):
    """
    Testing things that use the Dbus module
    """
    experimental = True
    bluetooth_service_experimental = b'\xe2\x97\x8f bluetooth.service - Bluetooth service\n   Loaded: loaded (/lib/systemd/system/bluetooth.service; enabled; vendor preset: enabled)\n   Active: active (running) since Fri 2017-10-13 21:48:58 UTC; 1 day 23h ago\n     Docs: man:bluetoothd(8)\n Main PID: 530 (bluetoothd)\n   Status: "Running"\n   CGroup: /system.slice/bluetooth.service\n           \xe2\x94\x94\xe2\x94\x80530 /usr/lib/bluetooth/bluetoothd --experimental\n\nOct 13 21:48:58 RPi3 systemd[1]: Starting Bluetooth service...\nOct 13 21:48:58 RPi3 bluetoothd[530]: Bluetooth daemon 5.43\nOct 13 21:48:58 RPi3 systemd[1]: Started Bluetooth service.\nOct 13 21:48:58 RPi3 bluetoothd[530]: Bluetooth management interface 1.14 initialized\nOct 13 21:48:58 RPi3 bluetoothd[530]: Failed to obtain handles for "Service Changed" characteristic\nOct 13 21:48:58 RPi3 bluetoothd[530]: Endpoint registered: sender=:1.10 path=/MediaEndpoint/A2DPSource\nOct 13 21:48:58 RPi3 bluetoothd[530]: Endpoint registered: sender=:1.10 path=/MediaEndpoint/A2DPSink\n'
    bluetooth_service_normal = b'\xe2\x97\x8f bluetooth.service - Bluetooth service\n   Loaded: loaded (/lib/systemd/system/bluetooth.service; enabled; vendor preset: enabled)\n   Active: active (running) since Fri 2017-10-13 21:48:58 UTC; 1 day 23h ago\n     Docs: man:bluetoothd(8)\n Main PID: 530 (bluetoothd)\n   Status: "Running"\n   CGroup: /system.slice/bluetooth.service\n           \xe2\x94\x94\xe2\x94\x80530 /usr/lib/bluetooth/bluetoothd\n\nOct 13 21:48:58 RPi3 systemd[1]: Starting Bluetooth service...\nOct 13 21:48:58 RPi3 bluetoothd[530]: Bluetooth daemon 5.43\nOct 13 21:48:58 RPi3 systemd[1]: Started Bluetooth service.\nOct 13 21:48:58 RPi3 bluetoothd[530]: Bluetooth management interface 1.14 initialized\nOct 13 21:48:58 RPi3 bluetoothd[530]: Failed to obtain handles for "Service Changed" characteristic\nOct 13 21:48:58 RPi3 bluetoothd[530]: Endpoint registered: sender=:1.10 path=/MediaEndpoint/A2DPSource\nOct 13 21:48:58 RPi3 bluetoothd[530]: Endpoint registered: sender=:1.10 path=/MediaEndpoint/A2DPSink\n'

    def get_bluetooth_service(self, cmd, shell):
        if TestDbusModuleCalls.experimental:
            return TestDbusModuleCalls.bluetooth_service_experimental
        else:
            return TestDbusModuleCalls.bluetooth_service_normal

    def setUp(self):
        """
        Patch the DBus module
        :return:
        """
        self.dbus_mock = MagicMock()
        self.mainloop_mock = MagicMock()
        self.gobject_mock = MagicMock()
        self.process_mock = MagicMock()

        modules = {
            'pydbus': self.dbus_mock,
            'pydbus.mainloop.glib': self.mainloop_mock,
            'gi.repository': self.gobject_mock,
            'subprocess': self.process_mock
        }
        self.dbus_mock.SystemBus.return_value.get.return_value.__getitem__.return_value.GetManagedObjects.return_value = tests.obj_data.full_ubits
        self.process_mock.check_output = self.get_bluetooth_service
        self.process_mock.Popen.return_value.communicate.return_value = (b'5.43\n', None)
        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from bluezero import dbus_tools
        self.module_under_test = dbus_tools

    def tearDown(self):
        self.module_patcher.stop()

    def test_uuid_path_gatt(self):
        dbus_full_path = self.module_under_test.get_dbus_path(\
                adapter='00:00:00:00:5A:AD',
                device='F7:17:E4:09:C0:C6',
                service='e95df2d8-251d-470a-a062-fa1922dfa9a8',
                characteristic='e95d9715-251d-470a-a062-fa1922dfa9a8',
                descriptor='00002902-0000-1000-8000-00805f9b34fb')
        expected_result = '/org/bluez/hci0/dev_F7_17_E4_09_C0_C6/service0031/char0035/desc0037'
        self.assertEqual(dbus_full_path, expected_result)

    def test_dev_paths(self):
        """ Test getting all device paths with the given device address """
        dbus_paths = self.module_under_test.get_dbus_paths(\
                device='E4:43:33:7E:54:B1' \
                )
        expected_result = [
                '/org/bluez/hci0/dev_E4_43_33_7E_54_B1']
        self.assertEqual(dbus_paths, expected_result)

    def test_service_paths(self):
        """ Test getting all service paths with the given service UUID """
        dbus_paths = self.module_under_test.get_dbus_paths(\
                service='e95df2d8-251d-470a-a062-fa1922dfa9a8'
                )
        expected_result = [
                '/org/bluez/hci0/dev_FD_6B_11_CD_4A_9B/service0031',
                '/org/bluez/hci0/dev_EB_F6_95_27_84_A0/service0031',
                '/org/bluez/hci0/dev_F7_17_E4_09_C0_C6/service0031',
                '/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service0031']
        self.assertEqual(dbus_paths, expected_result)

    def test_chrc_paths(self):
        """ Test getting all characteristic paths with the given char UUID """
        dbus_paths = self.module_under_test.get_dbus_paths(\
                characteristic='e95d9715-251d-470a-a062-fa1922dfa9a8' \
                )
        expected_result = [
                '/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service0031/char0035',
                '/org/bluez/hci0/dev_EB_F6_95_27_84_A0/service0031/char0035',
                '/org/bluez/hci0/dev_FD_6B_11_CD_4A_9B/service0031/char0035',
                '/org/bluez/hci0/dev_F7_17_E4_09_C0_C6/service0031/char0035']
        self.assertEqual(dbus_paths, expected_result)

    def test_serv_and_chrc_paths(self):
        """ Test getting all characteristic paths with the given char UUID """
        dbus_paths = self.module_under_test.get_dbus_paths(\
                service='e95df2d8-251d-470a-a062-fa1922dfa9a8', \
                characteristic='e95d9715-251d-470a-a062-fa1922dfa9a8' \
                )
        expected_result = [
                '/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service0031/char0035',
                '/org/bluez/hci0/dev_EB_F6_95_27_84_A0/service0031/char0035',
                '/org/bluez/hci0/dev_FD_6B_11_CD_4A_9B/service0031/char0035',
                '/org/bluez/hci0/dev_F7_17_E4_09_C0_C6/service0031/char0035']
        self.assertEqual(dbus_paths, expected_result)

    def test_dev_and_chrc_paths(self):
        """ Test getting all characteristic paths with the given device
        address and char UUID """
        dbus_paths = self.module_under_test.get_dbus_paths(\
                device='E4:43:33:7E:54:B1', \
                characteristic='0000FFF3-0000-1000-8000-00805F9B34FB' \
                )
        expected_result = [
                '/org/bluez/hci0/dev_E4_43_33_7E_54_B1/service0031/char0035']
        self.assertEqual(dbus_paths, expected_result)

    def test_chrc_and_desc_paths(self):
        """ Test getting all characteristic paths with the given device
        address and char UUID """
        dbus_paths = self.module_under_test.get_dbus_paths(\
                characteristic='00002a05-0000-1000-8000-00805f9b34fb',
                descriptor= '00002902-0000-1000-8000-00805f9b34fb'
                )
        expected_result = [\
                '/org/bluez/hci0/dev_FD_6B_11_CD_4A_9B/service0008/char0009/desc000b', \
                '/org/bluez/hci0/dev_F7_17_E4_09_C0_C6/service0008/char0009/desc000b', \
                '/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service0008/char0009/desc000b', \
                '/org/bluez/hci0/dev_EB_F6_95_27_84_A0/service0008/char0009/desc000b']

        self.assertEqual(dbus_paths, expected_result)

    def test_desc_paths(self):
        """ Test getting all descriptor paths with the given UUID """
        dbus_paths = self.module_under_test.get_dbus_paths(\
                descriptor= '00002902-0000-1000-8000-00805f9b34fb'
                )
        expected_result = [
                '/org/bluez/hci0/dev_FD_6B_11_CD_4A_9B/service0031/char0032/desc0034',
                '/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service0013/char0014/desc0016',
                '/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service0031/char0032/desc0034',
                '/org/bluez/hci0/dev_FD_6B_11_CD_4A_9B/service0008/char0009/desc000b',
                '/org/bluez/hci0/dev_F7_17_E4_09_C0_C6/service0020/char0027/desc0029',
                '/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service0020/char0027/desc0029',
                '/org/bluez/hci0/dev_F7_17_E4_09_C0_C6/service0019/char001a/desc001c',
                '/org/bluez/hci0/dev_F7_17_E4_09_C0_C6/service0031/char0035/desc0037',
                '/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service003a/char003b/desc003d',
                '/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service0031/char0035/desc0037',
                '/org/bluez/hci0/dev_EB_F6_95_27_84_A0/service0013/char0014/desc0016',
                '/org/bluez/hci0/dev_FD_6B_11_CD_4A_9B/service0031/char0035/desc0037',
                '/org/bluez/hci0/dev_FD_6B_11_CD_4A_9B/service0020/char0027/desc0029',
                '/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service0019/char001a/desc001c',
                '/org/bluez/hci0/dev_EB_F6_95_27_84_A0/service0019/char001a/desc001c',
                '/org/bluez/hci0/dev_EB_F6_95_27_84_A0/service0019/char001d/desc001f',
                '/org/bluez/hci0/dev_F7_17_E4_09_C0_C6/service003a/char003b/desc003d',
                '/org/bluez/hci0/dev_FD_6B_11_CD_4A_9B/service0019/char001a/desc001c',
                '/org/bluez/hci0/dev_EB_F6_95_27_84_A0/service0031/char0032/desc0034',
                '/org/bluez/hci0/dev_EB_F6_95_27_84_A0/service003a/char003b/desc003d',
                '/org/bluez/hci0/dev_F7_17_E4_09_C0_C6/service0008/char0009/desc000b',
                '/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service0008/char0009/desc000b',
                '/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service0019/char001d/desc001f',
                '/org/bluez/hci0/dev_FD_6B_11_CD_4A_9B/service0013/char0014/desc0016',
                '/org/bluez/hci0/dev_F7_17_E4_09_C0_C6/service0013/char0014/desc0016',
                '/org/bluez/hci0/dev_EB_F6_95_27_84_A0/service0020/char0027/desc0029',
                '/org/bluez/hci0/dev_EB_F6_95_27_84_A0/service0031/char0035/desc0037',
                '/org/bluez/hci0/dev_EB_F6_95_27_84_A0/service0008/char0009/desc000b',
                '/org/bluez/hci0/dev_FD_6B_11_CD_4A_9B/service0019/char001d/desc001f',
                '/org/bluez/hci0/dev_FD_6B_11_CD_4A_9B/service003a/char003b/desc003d',
                '/org/bluez/hci0/dev_F7_17_E4_09_C0_C6/service0019/char001d/desc001f',
                '/org/bluez/hci0/dev_F7_17_E4_09_C0_C6/service0031/char0032/desc0034']
        self.assertEqual(dbus_paths, expected_result)

    def test_bad_path(self):
        self.assertRaises(ValueError,
                          self.module_under_test.get_dbus_path,
                          adapter='00:00:00:00:5A:C6',
                          device='F7:17:E4:09:C0:XX',
                          service='e95df2d8-251d-470a-a062-fa1922dfa9a8')

    def test_get_iface_from_path(self):
        my_iface = self.module_under_test.get_iface(adapter='00:00:00:00:5A:AD',
                                                    device='F7:17:E4:09:C0:C6',
                                                    service='e95df2d8-251d-470a-a062-fa1922dfa9a8',
                                                    characteristic='e95d9715-251d-470a-a062-fa1922dfa9a8',
                                                    descriptor='00002902-0000-1000-8000-00805f9b34fb')
        self.assertEqual(constants.GATT_DESC_IFACE, my_iface)

    @unittest.skip('No profile information on database')
    def test_profile_path(self):
        my_iface = self.module_under_test.get_profile_path(adapter='00:00:00:00:5A:AD',
                                                           device='F7:17:E4:09:C0:C6',
                                                           profile='e95df2d8-251d-470a-a062-fa1922dfa9a8')
        self.assertEqual(None, my_iface)

    def test_bluez_version(self):
        bluez_ver = self.module_under_test.bluez_version()
        self.assertEqual('5.43', bluez_ver)

    def test_bluez_service_experimental(self):
        TestDbusModuleCalls.experimental = True
        bluez_exper = self.module_under_test.bluez_experimental_mode()
        self.assertTrue(bluez_exper)

    def test_bluez_service_normal(self):
        TestDbusModuleCalls.experimental = False
        bluez_exper = self.module_under_test.bluez_experimental_mode()
        self.assertFalse(bluez_exper)


if __name__ == '__main__':
    unittest.main(verbosity=2)
