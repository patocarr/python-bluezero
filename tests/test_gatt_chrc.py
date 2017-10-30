"""Automated testing of GATT functionality using unittest.mock."""
import sys
import unittest
try:
    from unittest.mock import MagicMock
    from unittest.mock import Mock
    from unittest.mock import patch
except:
    from mock import MagicMock
    from mock import patch
import tests.obj_data
from bluezero import constants
import pydbus


def mock_get(iface, prop):
    if iface == 'org.bluez.Device1':
        return tests.obj_data.full_ubits['/org/bluez/hci0/dev_F7_17_E4_09_C0_C6'][iface][prop]
    else:
        return tests.obj_data.full_ubits['/org/bluez/hci0/dev_F7_17_E4_09_C0_C6/service0020/char0025'][iface][prop]

def mock_set(iface, prop, value):
    tests.obj_data.full_ubits['/org/bluez/hci0/dev_F7_17_E4_09_C0_C6/service0020/char0025'][iface][prop] = value


class TestBluezeroCharacteristic(unittest.TestCase):
    """Test class to exercise (remote) GATT Characteristic Features."""

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
        from bluezero import GATT
        from bluezero import device
        self.module_under_test = GATT
        self.adapter_path = '/org/bluez/hci0'
        self.dev_name = 'BBC micro:bit [zezet]'
        self.adapter_addr = '00:00:00:00:5A:AD'
        self.device_addr = 'F7:17:E4:09:C0:C6'
        self.service_uuid = 'e95d127b-251d-470a-a062-fa1922dfa9a8'
        self.chrc_uuid = 'e95dd822-251d-470a-a062-fa1922dfa9a8'
        self.test_device = device.Device(self.adapter_addr, self.device_addr)

    def tearDown(self):
        self.module_patcher.stop()

    def test_chrc_uuid(self):
        """Test the characteristic UUID."""
        # Invoke the bluez GATT library to access the mock GATT service
        test_chrc = self.module_under_test.Characteristic(\
                self.test_device, \
                self.service_uuid, \
                self.chrc_uuid)

        # Test for the UUID
        self.assertEqual(test_chrc.UUID, 'e95dd822-251d-470a-a062-fa1922dfa9a8')

    def test_chrc_flags(self):
        """Test the characteristic flags."""
        # Invoke the bluez GATT library to access the mock GATT service
        test_chrc = self.module_under_test.Characteristic(\
                self.test_device, \
                self.service_uuid, \
                self.chrc_uuid)

        # Test for the UUID
        self.assertEqual(test_chrc.flags, ['write'])

if __name__ == '__main__':
    # avoid writing to stderr
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout,
                                                     verbosity=2))

