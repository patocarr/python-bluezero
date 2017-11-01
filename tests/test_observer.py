"""Automated testing of GATT functionality using unittest.mock."""
import sys
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
import tests.obj_data
from bluezero import constants
import pydbus

adapter_props = tests.obj_data.full_ubits


def mock_get(iface, prop):
    if iface == 'org.bluez.Adapter1':
        return tests.obj_data.full_ubits['/org/bluez/hci0'][iface][prop]
    elif iface == 'org.bluez.Device1':
        return tests.obj_data.full_ubits['/org/bluez/hci0/dev_E4_43_33_7E_54_1C'][iface][prop]
    else:
        return tests.obj_data.full_ubits['/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service002a'][iface][prop]


def mock_set(iface, prop, value):
    tests.obj_data.full_ubits['/org/bluez/hci0/dev_E4_43_33_7E_54_1C/service002a'][iface][prop] = value


class TestBluezeroObserver(unittest.TestCase):
    """Test class to exercise Observer Features."""

    def setUp(self):
        """Initialise the class for the tests."""
        self.dbus_mock = MagicMock()
        self.mainloop_mock = MagicMock()
        self.gobject_mock = MagicMock()

        modules = {
            'pydbus': self.dbus_mock,
            'pydbus.mainloop.glib': self.mainloop_mock,
            'gi.repository': self.gobject_mock,
        }
        self.dbus_mock.SystemBus.return_value.get.return_value.__getitem__.return_value.GetManagedObjects.return_value = tests.obj_data.full_ubits
        self.dbus_mock.SystemBus.return_value.get.return_value.__getitem__.return_value.Get = mock_get
        self.dbus_mock.SystemBus.return_value.get.return_value.__getitem__.return_value.Set = mock_set
        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from examples import observer
        from bluezero import device
        self.module_under_test = observer
        self.path = '/org/bluez/hci0/dev_E4_43_33_7E_54_1C'
        self.path2 = '/org/bluez/hci0/dev_FD_6B_11_CD_4A_9B'
        self.adapter_path = '/org/bluez/hci0'
        self.dev_name = 'BBC micro:bit [zezet]'
        self.adapter_addr = '00:00:00:00:5A:AD'
        self.device_addr = 'E4:43:33:7E:54:1C'
        self.device2_addr = 'FD:6B:11:CD:4A:9B'
        self.service_uuid = 'e95dd91d-251d-470a-a062-fa1922dfa9a8'

    def tearDown(self):
        self.module_patcher.stop()

    def test_central_default(self):
        """Test the observer default instantiation."""
        test_central = self.module_under_test.Observer()
        test_central.add_device(self.device_addr)

        self.assertEqual(test_central.connected, True)

    def test_dev_connected(self):
        """Test the observer with explicit device address."""
        test_central = self.module_under_test.Observer(\
                device_addr=self.device_addr)

        self.assertEqual(test_central.connected, True)

    def test_intf_added(self):
        """Test adding an interface to the observer."""
        test_central = self.module_under_test.Observer(\
                device_addr=self.device_addr)
        test_central.intf_added(self.path, {})

        self.assertEqual(len(test_central._devices), 1)

    def test_one_intf_added(self):
        """Test adding an interface to the observer multiple times,
        emulating BlueZ sending all properties when pairing."""
        test_central = self.module_under_test.Observer(\
                device_addr=self.device_addr)
        test_central.intf_added(self.path, {})
        for prop in tests.obj_data.full_ubits:
            if prop.startswith(self.path):
                test_central.intf_added(self.path, tests.obj_data.full_ubits[prop])

        self.assertEqual(len(test_central._devices), 1)

    def test_two_intf_added(self):
        """Test adding two interfaces to the observer multiple times,
        emulating BlueZ sending all properties when pairing."""
        test_central = self.module_under_test.Observer(\
                device_addr=self.device_addr)
        test_central.intf_added(self.path, {})
        for prop in tests.obj_data.full_ubits:
            if prop.startswith(self.path):
                test_central.intf_added(self.path, tests.obj_data.full_ubits[prop])
            if prop.startswith(self.path2):
                test_central.intf_added(self.path2, tests.obj_data.full_ubits[prop])

        self.assertEqual(test_central.get_devices, [self.device_addr, self.device2_addr])


if __name__ == '__main__':
    # avoid writing to stderr
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout,
                                                            verbosity=2))

