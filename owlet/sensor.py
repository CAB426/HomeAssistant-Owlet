"""Support for Owlet sensors."""
import logging
from datetime import timedelta

from custom_components.owlet import DOMAIN as OWLET_DOMAIN
from homeassistant.helpers.entity import Entity
from homeassistant.util import dt as dt_util

from .const import SENSOR_HEART_RATE, SENSOR_OXYGEN_LEVEL, SENSOR_BATTERY_LEVEL, SENSOR_SOCK_CONNECTION

SCAN_INTERVAL = timedelta(seconds=30)

SENSOR_CONDITIONS = {
    SENSOR_OXYGEN_LEVEL: {
        'name': 'Oxygen Level',
        'device_class': None
    },
    SENSOR_HEART_RATE: {
        'name': 'Heart Rate',
        'device_class': None
    },
    SENSOR_BATTERY_LEVEL: {
        'name': 'Battery Level',
        'device_class': 'battery'
    },
    SENSOR_SOCK_CONNECTION: {
        'name': 'Sock Connection',
        'device_class': None
    }
}

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up owlet binary sensor."""
    if discovery_info is None:
        return

    device = hass.data[OWLET_DOMAIN]

    entities = []
    for condition in SENSOR_CONDITIONS:
        if condition in device.monitor:
            entities.append(OwletSensor(device, condition))

    add_entities(entities, True)


class OwletSensor(Entity):
    """Representation of Owlet sensor."""

    def __init__(self, device, condition):
        """Init owlet binary sensor."""
        self._device = device
        self._condition = condition
        self._state = None
        self._prop_expiration = None
        self.is_charging = None
        self.battery_level = None
        self.sock_off = None
        self.sock_connection = None
        self._movement = None

    @property
    def name(self):
        """Return sensor name."""
        return '{} {}'.format(self._device.name,
                              SENSOR_CONDITIONS[self._condition]['name'])

    @property
    def state(self):
        """Return current state of sensor."""
        return self._state

    @property
    def device_class(self):
        """Return the device class."""
        return SENSOR_CONDITIONS[self._condition]['device_class']

    def update(self):
        """Update state of sensor."""
        try:
            self.is_charging = self._device.device.charge_status
            self.battery_level = self._device.device.batt_level
            self.sock_off = self._device.device.sock_off
            self.sock_connection = self._device.device.sock_connection
            self._movement = self._device.device.movement
            self._prop_expiration = self._device.device.prop_expire_time

            value = getattr(self._device.device, self._condition)

            if self._condition == 'batt_level':
                self._state = min(100, value)
                return

            if not self._device.device.base_station_on \
                    or self._device.device.charge_status > 0 \
                    or self._prop_expiration < dt_util.now().timestamp() \
                    or self._movement:
                value = 'off'

            self._state = value
        
        except Exception as e:
            _LOGGER.error(str(e))
        return False
