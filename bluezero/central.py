"""Classes that represent the GATT features of a remote device."""

from time import sleep

import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

from bluezero import adapter
from bluezero import device
from bluezero import GATT

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.addHandler(NullHandler())


class Central:
    """Create a BLE instance taking the Central role."""

    def __init__(self, device_addr, adapter_addr=None):
        if adapter_addr is None:
            self.dongle = adapter.Adapter()
            logger.debug('Adapter is: {}'.format(self.dongle.address))
        else:
            self.dongle = adapter.Adapter(adapter_addr)
        if not self.dongle.powered:
            self.dongle.powered = True
            logger.debug('Adapter was off, now powered on')

        if device_addr is not None:
            self.add_device(device_addr)

        self._characteristics = []

    def add_device(self, device_addr):
        """
        Add remote device of interest to device dictionary
        :param device_addr: Remote device's 48-bit address
        :return:
        """
        self.rmt_device = device.Device(self.dongle.address, device_addr)
        self._devices[device_addr] = self.rmt_device

    def add_characteristic(self, srv_uuid, chrc_uuid, device_addr=None):
        """
        Specify a characteristic of interest on the remote device by using
        the GATT Service UUID and Characteristic UUID
        :param srv_uuid: 128 bit UUID
        :param chrc_uuid: 128 bit UUID
        :param device_addr: Optional remote device address (if more than one)
        :return:
        """
        # If no argument given, select last device from devices list
        if device_addr is not None:
            rmt_device = _devices[-1]
        else:
            for dev in _devices:
                if dev.address == device_addr:
                    rmt_device = dev

        chrc_hndl = GATT.Characteristic(self.dongle.address,
                                        rmt_device.address,
                                        srv_uuid,
                                        chrc_uuid)
        self._characteristics.append(chrc_hndl)
        return chrc_hndl

    def load_gatt(self):
        """
        Once the remote device has been connected to and the GATT database
        has been resolved then it needs to be loaded.
        :return:
        """
        for chrc in self._characteristics:
            chrc.resolve_gatt()

    @property
    def services_resolved(self):
        return self.rmt_device.services_resolved

    @property
    def connected(self):
        """Indicate whether the remote device is currently connected."""
        return self.rmt_device.connected

    def connect(self, profile=None):
        """
        Initiate a connection to the remote device and load
        GATT database once resolved

        :param profile: (optional) profile to use for the connection.
        """
        if profile is None:
            self.rmt_device.connect()
        else:
            self.rmt_device.connect(profile)
        while not self.rmt_device.services_resolved:
            sleep(0.5)
        self.load_gatt()

    def disconnect(self):
        """Disconnect from the remote device."""
        self.rmt_device.disconnect()

    def run(self):
        self.dongle.run()

    def quit(self):
        self.dongle.quit()
