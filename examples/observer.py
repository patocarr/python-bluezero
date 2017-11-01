from bluezero import central
from bluezero import device
import logging
import re
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

class Observer(central.Central):

    def __init__(self, device_addr=None):
        central.Central.__init__(self, device_addr)

        # Set callback
        self.dongle.interfacesadded_signal(self.intf_added)
        self._periphs = []

    def intf_added(self, sender, obj):
        #print ("Sender: {} Obj: {}".format(sender, obj))
        addresses = [addr for addr in self._devices.keys()]
        sender_addr = path_to_addr(sender)
        if sender_addr is not None and sender_addr not in addresses:
            newdev = self.add_device(sender_addr)
            print ("Added device {}".format(sender_addr))
            #self.add_characteristic(self, srv_uuid, chrc_uuid, newdev)

    def add_peripheral(self, periph):
        self._periphs.append(periph)

    def run(self):
        self.dongle.run()


class Peripheral():
    """
    Describes a device with certain known service and characteristic
    that the central will know how to connect and decode.
    """

    def __init__(self, srv_uuid, chrc_uuid):
        self.srv_uuid = srv_uuid
        self.chrc_uuid = chrc_uuid

    def decode_chrc(self):
        pass


def path_to_addr(path):
    sre=re.search("dev_\S+?(?=\/|$)", path)
    addr = ''
    if sre is not None:
        dev=sre.group()
        addr=dev[4:].replace('_',':')
    return addr

def main():
    scanner = Observer()

    periph = Peripheral(srv_uuid='', chrc_uuid='')
    scanner.add_peripheral(periph)
    scanner.run()

if __name__ == '__main__':
    print(__name__)
    logger = logging.getLogger('adapter')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(NullHandler())
    main()

