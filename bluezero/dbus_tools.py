"""Utility functions for DBus use within Bluezero."""

# Standard libraries
import re
import subprocess
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

# D-Bus import
import pydbus as dbus
from gi.repository import GLib

# python-bluezero constants import
from bluezero import constants

GLib.MainLoop()

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.addHandler(NullHandler())


def bluez_version():
    """
    get the version of the BlueZ daemon being used on the system
    :return: String of BlueZ version
    """
    p = subprocess.Popen(['bluetoothctl', '-v'], stdout=subprocess.PIPE)
    ver = p.communicate()
    return str(ver[0].decode().rstrip())


def bluez_experimental_mode():
    """
    Return True if the BlueZ daemon service is in experimental mode
    :return: True if experimental enabled
    """
    status = subprocess.check_output('service bluetooth status', shell=True)
    if re.search('--experimental', status.decode('utf-8')) is None:
        return False
    else:
        return True


def interfaces_added(path, interfaces):
    """
    Callback for when an interface is added
    :param path:
    :param interfaces:
    :return:
    """
    if constants.DEVICE_INTERFACE in interfaces:
        logger.debug('Device added at {}'.format(path))


def properties_changed(interface, changed, extra):
    """
    Callback for when properties are changed
    :param interface:
    :param changed:
    :param extra:
    :return:
    """
    if constants.DEVICE_INTERFACE in interface:
        for prop in changed:
            logger.debug(
                '{}: Property {} new value {}'.format(interface,
                                                        extra,
                                                        prop,
                                                        changed[prop]))


def get_dbus_obj(dbus_path):
    """
    Get the the DBus object for the given path
    :param dbus_path:
    :return:
    """
    bus = dbus.SystemBus()
    return bus.get(constants.BLUEZ_SERVICE_NAME, dbus_path)


def get_dbus_iface(iface, dbus_obj):
    """
    Return the DBus interface object for given interface and DBus object
    :param iface:
    :param dbus_obj:
    :return:
    """
    return dbus_obj[iface]


def get_managed_objects():
    """Return the objects currently managed by the DBus Object Manager."""
    bus = dbus.SystemBus()
    manager = bus.get(
            constants.BLUEZ_SERVICE_NAME, '/')[constants.DBUS_OM_IFACE]
    return manager.GetManagedObjects()


def _get_dbus_path2(objects, parent_path, iface_in, prop, value):
    """
    Find DBus path for given DBus interface with property of a given value.

    :param objects: Dictionary of objects to search
    :param parent_path: Parent path to include in search
    :param iface_in: The interface of interest
    :param prop: The property to search for
    :param value: The value of the property being searched for
    :return: Path of object searched for
    """
    for obj in objects:
        props = objects[obj]
        path = obj
        #print(" >Interface: {}".format(iface_in))
        #print(" >Properties: {}".format(props))
        #print(" >Path: {}".format(path))
        if props is None or iface_in not in props.keys():
            continue
        if props[iface_in][prop].lower() == value.lower() and \
                parent_path is not None and path.startswith(parent_path):
            return path
    raise ValueError('Bad combination of inputs: found nothing')


def get_dbus_path(adapter=None,
                  device=None,
                  service=None,
                  characteristic=None,
                  descriptor=None):
    """
    Return a DBus path for the given properties
    :param adapter: Adapter address
    :param device: Device address
    :param service: GATT Service UUID
    :param characteristic: GATT Characteristic UUID
    :param descriptor: GATT Descriptor UUID
    :return: DBus path
    """
    mngd_objs = get_managed_objects()
    #print(mngd_objs)

    _dbus_obj_path = None

    if adapter is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         '/org/bluez',
                                         constants.ADAPTER_INTERFACE,
                                         'Address',
                                         adapter)

    if device is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.DEVICE_INTERFACE,
                                         'Address',
                                         device)

    if service is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.GATT_SERVICE_IFACE,
                                         'UUID',
                                         service)

    if characteristic is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.GATT_CHRC_IFACE,
                                         'UUID',
                                         characteristic)

    if descriptor is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.GATT_DESC_IFACE,
                                         'UUID',
                                         descriptor)
    return _dbus_obj_path


def get_profile_path(adapter,
                     device,
                     profile):
    """
    Return a DBus path for the given properties
    :param adapter: Adapter address
    :param device: Device address
    :param profile:
    :return:
    """
    mngd_objs = get_managed_objects()

    _dbus_obj_path = None

    if adapter is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         '/org/bluez',
                                         constants.ADAPTER_INTERFACE,
                                         'Address',
                                         adapter)
    if device is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.DEVICE_INTERFACE,
                                         'Address',
                                         device)

    if profile is not None:
        _dbus_obj_path = _get_dbus_path2(mngd_objs,
                                         _dbus_obj_path,
                                         constants.GATT_PROFILE_IFACE,
                                         'UUID',
                                         profile)
    return _dbus_obj_path


def get_iface(adapter=None,
              device=None,
              service=None,
              characteristic=None,
              descriptor=None):
    """
    For the given list of properties return the deepest interface
    :param adapter: Adapter address
    :param device: Device address
    :param service: GATT Service UUID
    :param characteristic: GATT Characteristic UUID
    :param descriptor: GATT Descriptor UUID
    :return: DBus Interface
    """
    if adapter is not None:
        _iface = constants.ADAPTER_INTERFACE

    if device is not None:
        _iface = constants.DEVICE_INTERFACE

    if service is not None:
        _iface = constants.GATT_SERVICE_IFACE

    if characteristic is not None:
        _iface = constants.GATT_CHRC_IFACE

    if descriptor is not None:
        _iface = constants.GATT_DESC_IFACE

    return _iface


def get_methods(adapter=None,
                device=None,
                service=None,
                characteristic=None,
                descriptor=None):
    """
    Get methods available for the specified
    :param adapter: Adapter Address
    :param device: Device Address
    :param service: GATT Service UUID
    :param characteristic: GATT Characteristic UUID
    :param descriptor: GATT Descriptor UUID
    :return: Object of the DBus methods available
    """
    path_obj = get_dbus_path(adapter,
                             device,
                             service,
                             characteristic,
                             descriptor)

    iface = get_iface(adapter,
                      device,
                      service,
                      characteristic,
                      descriptor)

    return get_dbus_iface(iface, get_dbus_obj(path_obj))


def get_props(adapter=None,
              device=None,
              service=None,
              characteristic=None,
              descriptor=None):
    """
    Get properties for the specified object
    :param adapter: Adapter Address
    :param device:  Device Address
    :param service:  GATT Service UUID
    :param characteristic: GATT Characteristic UUID
    :param descriptor: GATT Descriptor UUID
    :return: Object of the DBus properties available
    """
    path_obj = get_dbus_path(adapter,
                             device,
                             service,
                             characteristic,
                             descriptor)

    return get_dbus_iface(constants.DBUS_OM_IFACE, get_dbus_obj(path_obj))

