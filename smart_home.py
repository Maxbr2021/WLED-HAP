import logging
import signal

from pyhap.accessory import Accessory, Bridge
from pyhap.accessory_driver import AccessoryDriver

from Accessories.Light import Wled

logging.basicConfig(level=logging.INFO, format="[%(module)s] %(message)s")



def get_bridge(driver):
    bridge = Bridge(driver, 'Bridge')
    bridge.set_info_service(
            manufacturer='Max',
            model='Pybridge',
            firmware_revision='1.0',
            serial_number='12345678'
        )

    bridge.add_accessory(Wled('http://<WLED-IP>/json/state','/path/to/pyhap/Accessories/config.json',driver, 'WLED'))
    return bridge


driver = AccessoryDriver(port=51826, persist_file='smarthome.state')
driver.add_accessory(accessory=get_bridge(driver))
signal.signal(signal.SIGTERM, driver.signal_handler)
driver.start()
