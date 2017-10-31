"""Automated testing of GATT functionality using unittest.mock."""
import sys
import unittest
try:
    from unittest.mock import MagicMock
    from unittest.mock import patch
except:
    from mock import MagicMock
    from mock import patch
import tests.obj_data
from bluezero import constants
import pydbus


def mock_get(iface, prop):
    if iface == 'org.bluez.Device1':
        return tests.obj_data.full_ubits['/org/bluez/hci0/dev_EB_F6_95_27_84_A0'][iface][prop]
    else:
        return tests.obj_data.full_ubits['/org/bluez/hci0/dev_EB_F6_95_27_84_A0/service0031/char0032/desc0034'][iface][prop]

def mock_set(iface, prop, value):
    tests.obj_data.full_ubits['/org/bluez/hci0/dev_EB_F6_95_27_84_A0/service0031/char0032/desc0034'][iface][prop] = value


class TestBluezeroDescriptor(unittest.TestCase):
    """Test class to exercise (remote) GATT Descriptor Features."""

    def setUp(self):
        """Initialise the class for the tests."""
        self.dbus_mock = MagicMock()
        self.mainloop_mock = MagicMock()
        self.gobject_mock = MagicMock()

        modules = {
            'pydbus': self.dbus_mock,
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
        self.device_addr = 'EB:F6:95:27:84:A0'
        self.service_uuid = 'e95df2d8-251d-470a-a062-fa1922dfa9a8'
        self.chrc_uuid = 'e95d9715-251d-470a-a062-fa1922dfa9a8'
        self.desc_uuid = '00002902-0000-1000-8000-00805f9b34fb'
        self.test_device = device.Device(self.adapter_addr, self.device_addr)

    def tearDown(self):
        self.module_patcher.stop()

    def test_desc_uuid(self):
        """Test the descriptor UUID."""
        test_desc = self.module_under_test.Descriptor(\
                self.test_device, \
                self.service_uuid, \
                self.chrc_uuid, \
                self.desc_uuid)

        # Test for the UUID
        self.assertEqual(test_desc.UUID, '00002902-0000-1000-8000-00805f9b34fb')

    def test_desc_read_value(self):
        """Test reading the descriptor value."""
        test_desc = self.module_under_test.Descriptor(\
                self.test_device, \
                self.service_uuid, \
                self.chrc_uuid, \
                self.desc_uuid)

        # Test for the value
        self.assertEqual(test_desc.value, [])

    def test_desc_chrc(self):
        """Test the characteristic belonging to the descriptor."""
        test_desc = self.module_under_test.Descriptor(\
                self.test_device, \
                self.service_uuid, \
                self.chrc_uuid, \
                self.desc_uuid)

        # Test for the characteristic
        self.assertEqual(test_desc.characteristic, \
                '/org/bluez/hci0/dev_EB_F6_95_27_84_A0/service0031/char0032')

if __name__ == '__main__':
    # avoid writing to stderr
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout,
                                                     verbosity=2))

