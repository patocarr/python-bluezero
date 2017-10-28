"""
Tests for the Adapter.

This test class makes use of sample DBus data captured from a live device,
imported as ``tests.obj_data``.
"""
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


def mock_get_all(iface):
    """
    Mock the DBus ``GetAll()`` operation for an interface.

    :param string iface: DBus interface to ``GetAll()`` on
                         (e.g. ``'org.bluez.Adapter1'``)
    :return: DBus Interface Properties
    :rtype: Dictionary
    """
    return tests.obj_data.full_ubits['/org/bluez/hci0'][iface]


def mock_get(iface, prop):
    """
    Mock the DBus ``Get()`` operation for a property on an interface.

    :param string iface: DBus interface, e.g. ``'org.bluez.Adapter1'``
    :param string prop: DBus property name, e.g. ``'Name'``
    :return: DBus property
    :rtype: *property dependent*
    """
    print(mock_get_all(iface)[prop])
    return mock_get_all(iface)[prop]


def mock_set(iface, prop, value):
    """
    Mock the DBus ``Set()`` operation for a property on an interface.

    :param string iface: DBus interface, e.g. ``'org.bluez.Adapter1'``
    :param string prop: DBus property name, e.g. ``'Name'``
    :param value: Value to set the DBus property to
    :return: None
    """
    tests.obj_data.full_ubits['/org/bluez/hci0'][iface][prop] = value

def mock_callback():
    return True


class TestBluezeroAdapter(unittest.TestCase):
    """
    Mock a BLE Adapter.
    """

    def setUp(self):
        """
        Patch the DBus module using ``MagicMock`` from ``unittest.mock``

        :return: None

        Three modules are mocked and patched into the system:

        #. DBus

           * Calls to ``GetManagedObjects()``, ``Get()``, ``Set()``, and
             ``GetAll()`` are mocked using a captured DBus dictionary.
        #. DBus Mainloop
        #. GObject
        """
        self.dbus_mock = MagicMock()
        self.mainloop_mock = MagicMock()
        self.gobject_mock = MagicMock()

        modules = {
            'pydbus': self.dbus_mock,
            'pydbus.mainloop.glib': self.mainloop_mock,
            'gi.repository': self.gobject_mock,
        }

        self.dbus_mock.SystemBus.return_value.get.return_value.__getitem__.return_value.GetManagedObjects.return_value = tests.obj_data.full_ubits
        self.dbus_mock.SystemBus.return_value.get.return_value.__getitem__.return_value.InterfacesAdded.side_effect = mock_callback
        self.dbus_mock.SystemBus.return_value.get.return_value.__getitem__.return_value.Get = mock_get
        self.dbus_mock.SystemBus.return_value.get.return_value.__getitem__.return_value.Set = mock_set
        self.dbus_mock.SystemBus.return_value.get.return_value.__getitem__.return_value.GetAll = mock_get_all

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()

        from bluezero import adapter
        self.module_under_test = adapter
        # self.adapter_device = 'hci0'  # Currently unused
        self.adapter_name = 'linaro-alip'
        #self.path = '/org/bluez/hci0'  Adapter constructor doesn't take a path
        self.addr = '00:00:00:00:5A:AD' # but takes an address

    def tearDown(self):
        """
        Stop the module patching.
        """
        self.module_patcher.stop()

    def test_list_adapters(self):
        """
        Test ``Adapter.list_adapters()``
        """
        adapters = self.module_under_test.list_adapters()
        self.assertListEqual(['00:00:00:00:5A:AD'], adapters)

    def test_adapter_address(self):
        """
        Test the adapter ``address`` property.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        self.assertEqual(dongle.address, '00:00:00:00:5A:AD')

    def test_adapter_default(self):
        """
        Test the default ``Adapter()`` instantation gets the correct address.
        """
        dongle = self.module_under_test.Adapter()
        self.assertEqual(dongle.address, '00:00:00:00:5A:AD')

    def test_get_all(self):
        """
        Test the ``get_all()`` method for retrieving all the DBus properties.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        self.assertEqual(dongle.get_all(),
                         mock_get_all(constants.ADAPTER_INTERFACE))

    def test_adapter_name(self):
        """
        Test the adapter ``name`` property.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        # test
        self.assertEqual(dongle.name, self.adapter_name)

    def test_adapter_alias(self):
        """
        Test the adapter ``alias`` property.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        # test
        self.assertEqual(dongle.alias, self.adapter_name)

    def test_adapter_alias_write(self):
        """
        Test that an adapter ``alias`` can be set.
        """
        dev_name = 'my-test-dev'
        dongle = self.module_under_test.Adapter(self.addr)
        # test
        dongle.alias = dev_name
        self.assertEqual(dongle.alias, dev_name)

    def test_class(self):
        """
        Test the adapter ``bt_class`` property.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        # test
        self.assertEqual(dongle.bt_class, 4980736)

    def test_adapter_power(self):
        """
        Test the adapter ``powered`` property.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        # test
        self.assertEqual(dongle.powered, 1)

    def test_adapter_power_write(self):
        """
        Test that the adapter ``powered`` property can be set.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        # test
        dongle.powered = 0
        self.assertEqual(dongle.powered, False)

    def test_adapter_discoverable(self):
        """
        Test the adapter ``discoverable`` property.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        # test
        self.assertEqual(dongle.discoverable, False)

    def test_adapter_discoverable_write(self):
        """
        Test that the adapter ``discoverable`` property can be set.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        # test
        dongle.discoverable = 1
        self.assertEqual(dongle.discoverable, True)

    def test_adapter_pairable(self):
        """
        Test the adapter ``pairable`` property.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        # test
        self.assertEqual(dongle.pairable, 1)

    def test_adapter_pairable_write(self):
        """
        Test that the adapter ``pairable`` property can be set.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        # test
        dongle.pairable = 0
        self.assertEqual(dongle.pairable, 0)

    def test_adapter_pairabletimeout(self):
        """
        Test the adapter ``pairabletimeout`` property.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        # test
        self.assertEqual(dongle.pairabletimeout, 0)

    def test_adapter_pairabletimeout_write(self):
        """
        Test that the adapter ``pairabletimeout`` property can be set.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        # test
        dongle.pairabletimeout = 220
        self.assertEqual(dongle.pairabletimeout, 220)

    def test_adapter_discoverable_timeout(self):
        """
        Test the adapter ``discoverabletimeout`` property.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        # test
        self.assertEqual(dongle.discoverabletimeout, 180)

    def test_adapter_discoverabletimeout_write(self):
        """
        Test that the adapter ``discoverabletimeout`` property can be set.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        # test
        dongle.discoverabletimeout = 220
        self.assertEqual(dongle.discoverabletimeout, 220)

    def test_adapter_discovering(self):
        """
        Test the adapter ``discovering`` property.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        # test
        self.assertEqual(dongle.discovering, False)

    @unittest.skip('mock of discovery not implemented')
    def test_start_discovery(self):
        """
        Test the adapter ``nearby_discovering()`` method.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        # test
        dongle.nearby_discovery()
        self.assertEqual(dongle.discovering, 1)

    @unittest.skip('mock of signal callback not implemented')
    def test_interfacesadded_callback(self):
        """
        Test the adapter ``InterfacesAdded`` signal.
        """
        dongle = self.module_under_test.Adapter(self.addr)
        dongle.interfacesadded_signal(mock_callback)

if __name__ == '__main__':
    # avoid writing to stderr
    unittest.main(testRunner=unittest.TextTestRunner(stream=sys.stdout,
                                                     verbosity=2))
