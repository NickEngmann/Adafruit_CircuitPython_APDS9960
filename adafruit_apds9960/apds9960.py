# SPDX-FileCopyrightText: 2017 Michael McWethy for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`APDS9960`
====================================================

Driver class for the APDS9960 board.  Supports gesture, proximity, and color
detection.

* Author(s): Michael McWethy

Implementation Notes
--------------------

**Hardware:**

* Adafruit `APDS9960 Proximity, Light, RGB, and Gesture Sensor
  <https://www.adafruit.com/product/3595>`_ (Product ID: 3595)

* Adafruit `Adafruit CLUE
  <https://www.adafruit.com/product/4500>`_ (Product ID: 4500)

* Adafruit `Adafruit Feather nRF52840 Sense
  <https://www.adafruit.com/product/4516>`_ (Product ID: 4516)

* Adafruit `Adafruit Proximity Trinkey
  <https://www.adafruit.com/product/5022>`_ (Product ID: 5022)

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""
import time
from adafruit_bus_device.i2c_device import I2CDevice
from micropython import const

try:
    # Only used for typing
    from typing import Tuple
    from busio import I2C
except ImportError:
    pass

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_APDS9960.git"

# Only one address is possible for the APDS9960, no alternates are available
_ADDRESS = const(0x39)
_DEVICE_ID = const(0xAB)

# APDS9960_RAM        = const(0x00)
_APDS9960_ENABLE = const(0x80)
_APDS9960_ATIME = const(0x81)
# _APDS9960_WTIME      = const(0x83)
# _APDS9960_AILTIL     = const(0x84)
# _APDS9960_AILTH      = const(0x85)
# _APDS9960_AIHTL      = const(0x86)
# _APDS9960_AIHTH      = const(0x87)
_APDS9960_PILT = const(0x89)
_APDS9960_PIHT = const(0x8B)
_APDS9960_PERS = const(0x8C)
# _APDS9960_CONFIG1    = const(0x8D)
# _APDS9960_PPULSE = const(0x8E)
_APDS9960_CONTROL = const(0x8F)
# _APDS9960_CONFIG2 = const(0x90)
_APDS9960_ID = const(0x92)
_APDS9960_STATUS = const(0x93)
_APDS9960_CDATAL = const(0x94)
# _APDS9960_CDATAH     = const(0x95)
# _APDS9960_RDATAL     = const(0x96)
# _APDS9960_RDATAH     = const(0x97)
# _APDS9960_GDATAL     = const(0x98)
# _APDS9960_GDATAH     = const(0x99)
# _APDS9960_BDATAL     = const(0x9A)
# _APDS9960_BDATAH     = const(0x9B)
_APDS9960_PDATA = const(0x9C)
# _APDS9960_POFFSET_UR = const(0x9D)
# _APDS9960_POFFSET_DL = const(0x9E)
# _APDS9960_CONFIG3    = const(0x9F)
_APDS9960_GPENTH = const(0xA0)
_APDS9960_GEXTH = const(0xA1)
_APDS9960_GCONF1 = const(0xA2)
_APDS9960_GCONF2 = const(0xA3)
# _APDS9960_GOFFSET_U  = const(0xA4)
# _APDS9960_GOFFSET_D  = const(0xA5)
# _APDS9960_GOFFSET_L  = const(0xA7)
# _APDS9960_GOFFSET_R  = const(0xA9)
_APDS9960_GPULSE = const(0xA6)
# _APDS9960_GCONF3 = const(0xAA)
_APDS9960_GCONF4 = const(0xAB)
_APDS9960_GFLVL = const(0xAE)
_APDS9960_GSTATUS = const(0xAF)
# _APDS9960_IFORCE     = const(0xE4)
# _APDS9960_PICLEAR    = const(0xE5)
# _APDS9960_CICLEAR    = const(0xE6)
_APDS9960_AICLEAR = const(0xE7)
_APDS9960_GFIFO_U = const(0xFC)
# APDS9960_GFIFO_D    = const(0xFD)
# APDS9960_GFIFO_L    = const(0xFE)
# APDS9960_GFIFO_R    = const(0xFF)

_BIT_MASK_ENABLE_EN = const(0x01)
_BIT_MASK_ENABLE_COLOR = const(0x02)
_BIT_MASK_ENABLE_PROX = const(0x04)
_BIT_MASK_ENABLE_PROX_INT = const(0x20)
_BIT_MASK_ENABLE_GESTURE = const(0x40)

_BIT_MASK_GSTATUS_GVALID = const(0x01)

_BIT_MASK_GCONF4_GMODE = const(0x01)

_BIT_POSITON_PERS_PPERS = const(4)
_BIT_MASK_PERS_PPERS = const(0xF0)

# _BIT_POSITON_GCONF1_GFIFOTH = const(6)
# _BIT_MASK_GCONF1_GFIFOTH = const(0xC0)

# _BIT_POSITON_GCONF2_GGAIN = const(5)
# _BIT_MASK_GCONF2_GGAIN = const(0x60)

# _BIT_POSITON_CONTROL_AGAIN = const(0)
# _BIT_MASK_CONTROL_AGAIN = const(0x03)

# pylint: disable-msg=too-many-instance-attributes
class APDS9960:
    """
    APDS9900 provide basic driver services for the ASDS9960 breakout board

    :param ~busio.I2C i2c: The I2C bus the ASDS9960 is connected to
    :param int rotation: rotation of the device. Defaults to :const:`0`
    :param bool reset: If true, reset device on init. Defaults to :const:`True`
    :param bool set_defaults: If true, set sensible defaults on init. Defaults to :const:`True`


    **Quickstart: Importing and using the APDS9960**

        Here is an example of using the :class:`APDS9960` class.
        First you will need to import the libraries to use the sensor

        .. code-block:: python

            import board
            from adafruit_apds9960.apds9960 import APDS9960

        Once this is done you can define your `board.I2C` object and define your sensor object

        .. code-block:: python

            i2c = board.I2C()   # uses board.SCL and board.SDA
            apds = APDS9960(i2c)

        Now you have access to the :attr:`apds.proximity_enable` :attr:`apds.proximity` attributes

        .. code-block:: python

            apds.proximity_enable = True
            proximity = apds.proximity

    """

    def __init__(
        self,
        i2c: I2C,
        *,
        rotation: int = 0,
        reset: bool = True,
        set_defaults: bool = True
    ):
        
        self.rotation = rotation

        self.buf129 = None
        self.buf2 = bytearray(2)

        self.i2c_device = I2CDevice(i2c, _ADDRESS)

        if self._read8(_APDS9960_ID) != _DEVICE_ID:
            raise RuntimeError()

        if reset:
            self._write8(_APDS9960_ENABLE, 0) # Disable sensor and all functions/interrupts

            # Reset basic config registers to power-on defaults
            self._write8(_APDS9960_ATIME, 255)
            self._write8(_APDS9960_PIHT, 0)
            self._write8(_APDS9960_PERS, 0)
            self._write8(_APDS9960_CONTROL, 1)
            self._write8(_APDS9960_GPENTH, 0)
            self._write8(_APDS9960_GEXTH, 0)
            self._write8(_APDS9960_GCONF1, 0)
            self._write8(_APDS9960_GCONF2, 0)
            self._write8(_APDS9960_GPULSE, 0)

            # Clear all interrupts
            self.clear_interrupt()

            # Enable sensor and wait 10ms for the power on delay to finish
            self.enable = True
            time.sleep(0.010)

        if set_defaults:
            self.proximity_interrupt_threshold = (0, 5, 4) # Trigger PINT at >= 5, PPERS: 4 cycles
            self._write8(_APDS9960_GPENTH, 0x05) # Enter gesture engine at >= 5 counts
            self._write8(_APDS9960_GEXTH, 0x1E) # Exit gesture engine if all counts drop below 30
            self._write8(_APDS9960_GCONF1, 0x82) # GEXPERS: 1 (4 cycles), GFIFOTH: 2 (8 datasets)
            self._write8(_APDS9960_GCONF2, 0x21) # GWTIME: 1 (2.8ms), GLDRIVE: 100mA, GGAIN: 1 (2x) 
            self._write8(_APDS9960_GPULSE, 0x85) # GPULSE: 5 (6 pulses), GPLEN: 2 (16 us)
            self._write8(_APDS9960_ATIME, 0xB6) # ATIME: 182 (200ms color integration time)
            self._write8(_APDS9960_CONTROL, 0x01) # AGAIN: 1 (4x color gain), PGAIN: 0 (1x)
        
        self._reset_counts()

    ## BOARD
    @property
    def enable_gesture(self) -> bool:
        return self._get_bit(_APDS9960_ENABLE, _BIT_MASK_ENABLE_GESTURE)

    @enable_gesture.setter
    def enable_gesture(self, value: bool) -> None:
        self._set_bit(_APDS9960_ENABLE, _BIT_MASK_ENABLE_GESTURE, value)

    @property
    def _gesture_mode(self) -> bool:
        return self._get_bit(_APDS9960_GCONF4, _BIT_MASK_GCONF4_GMODE)

    @_gesture_mode.setter
    def _gesture_mode(self, value: bool) -> None:
        self._set_bit(_APDS9960_GCONF4, _BIT_MASK_GCONF4_GMODE, value)

    @property
    def _gesture_valid(self) -> bool:
        return self._get_bit(_APDS9960_GSTATUS, _BIT_MASK_GSTATUS_GVALID)

    @property
    def _proximity_persistence(self) -> int:
        self._get_bits(_APDS9960_PERS, _BIT_POSITON_PERS_PPERS, _BIT_MASK_PERS_PPERS)

    @_proximity_persistence.setter
    def _proximity_persistence(self, value: int) -> None:
        self._set_bits(_APDS9960_PERS, _BIT_POSITON_PERS_PPERS, _BIT_MASK_PERS_PPERS, value)

    @property
    def enable(self) -> bool:
        return self._get_bit(_APDS9960_ENABLE, _BIT_MASK_ENABLE_EN)

    @enable.setter
    def enable(self, value: bool) -> None:
        """Board enable.  True to enable, False to disable"""
        self._set_bit(_APDS9960_ENABLE, _BIT_MASK_ENABLE_EN, value)

    @property
    def enable_color(self) -> bool:
        return self._get_bit(_APDS9960_ENABLE, _BIT_MASK_ENABLE_COLOR)

    @enable_color.setter
    def enable_color(self, value: bool) -> None:
        """Color detection enable flag.
            True when color detection is enabled, else False"""
        self._set_bit(_APDS9960_ENABLE, _BIT_MASK_ENABLE_COLOR, value)

    @property
    def enable_proximity(self) -> bool:
        return self._get_bit(_APDS9960_ENABLE, _BIT_MASK_ENABLE_PROX)

    @enable_proximity.setter
    def enable_proximity(self, value: bool) -> None:
        """Enable of proximity mode"""
        self._set_bit(_APDS9960_ENABLE, _BIT_MASK_ENABLE_PROX, value)

    @property
    def enable_proximity_interrupt(self) -> bool:
        return self._get_bit(_APDS9960_ENABLE, _BIT_MASK_ENABLE_PROX_INT)

    @enable_proximity_interrupt.setter
    def enable_proximity_interrupt(self, value: bool) -> None:
        """Proximity interrupt enable flag.  True if enabled,
            False to disable"""
        self._set_bit(_APDS9960_ENABLE, _BIT_MASK_ENABLE_PROX_INT, value)

    ## GESTURE ROTATION
    @property
    def rotation(self) -> int:
        """Gesture rotation offset. Acceptable values are 0, 90, 180, 270."""
        return self._rotation

    @rotation.setter
    def rotation(self, new_rotation: int) -> None:
        if new_rotation in [0, 90, 180, 270]:
            self._rotation = new_rotation
        else:
            raise ValueError("Rotation value must be one of: 0, 90, 180, 270")

    ## GESTURE DETECTION
    def _reset_counts(self) -> None:
        """Gesture detection internal counts"""
        self._saw_down_start = 0
        self._saw_up_start = 0
        self._saw_left_start = 0
        self._saw_right_start = 0

    def gesture(self) -> int:  # pylint: disable-msg=too-many-branches
        """Returns gesture code if detected. =0 if no gesture detected
        =1 if an UP, =2 if a DOWN, =3 if an LEFT, =4 if a RIGHT
        """
        # buffer to read of contents of device FIFO buffer
        if not self.buf129:
            self.buf129 = bytearray(129)

        buffer = self.buf129
        buffer[0] = _APDS9960_GFIFO_U
        if not self._gesture_valid:
            return 0

        time_mark = 0.0
        gesture_received = 0
        while True:

            up_down_diff = 0
            left_right_diff = 0
            gesture_received = 0
            time.sleep(0.030)  # 30 ms

            n_recs = self._read8(_APDS9960_GFLVL)
            if n_recs:

                with self.i2c_device as i2c:
                    i2c.write_then_readinto(
                        buffer,
                        buffer,
                        out_end=1,
                        in_start=1,
                        in_end=min(129, 1 + n_recs * 4),
                    )
                upp, down, left, right = buffer[1:5]

                if abs(upp - down) > 13:
                    up_down_diff = upp - down

                if abs(left - right) > 13:
                    left_right_diff = left - right

                if up_down_diff != 0:
                    if up_down_diff < 0:
                        # either leading edge of down movement
                        # or trailing edge of up movement
                        if self._saw_up_start:
                            gesture_received = 0x01  # up
                        else:
                            self._saw_down_start += 1
                    elif up_down_diff > 0:
                        # either leading edge of up movement
                        # or trailing edge of down movement
                        if self._saw_down_start:
                            gesture_received = 0x02  # down
                        else:
                            self._saw_up_start += 1

                if left_right_diff != 0:
                    if left_right_diff < 0:
                        # either leading edge of right movement
                        # trailing edge of left movement
                        if self._saw_left_start:
                            gesture_received = 0x03  # left
                        else:
                            self._saw_right_start += 1
                    elif left_right_diff > 0:
                        # either leading edge of left movement
                        # trailing edge of right movement
                        if self._saw_right_start:
                            gesture_received = 0x04  # right
                        else:
                            self._saw_left_start += 1

                # saw a leading or trailing edge; start timer
                if up_down_diff or left_right_diff:
                    time_mark = time.monotonic()

            # finished when a gesture is detected or ran out of time (300ms)
            if gesture_received or time.monotonic() - time_mark > 0.300:
                self._reset_counts()
                break
        if gesture_received != 0:
            if self._rotation != 0:
                
                directions = [1, 4, 2, 3]
                new_index = (directions.index(gesture_received) + self._rotation // 90) % 4
                return directions[new_index]

        return gesture_received

    ## COLOR
    @property
    def color_data_ready(self) -> int:
        """Color data ready flag.  zero if not ready, 1 is ready"""
        return self._read8(_APDS9960_STATUS) & 0x01

    @property
    def color_data(self) -> Tuple[int, int, int, int]:
        """Tuple containing r, g, b, c values"""
        return (
            self._color_data16(_APDS9960_CDATAL + 2),
            self._color_data16(_APDS9960_CDATAL + 4),
            self._color_data16(_APDS9960_CDATAL + 6),
            self._color_data16(_APDS9960_CDATAL),
        )

    ## PROXIMITY
    @property
    def proximity_interrupt_threshold(self) -> Tuple[int, int, int]:
        """Tuple containing low and high threshold
        followed by the proximity interrupt persistence.
        When setting the proximity interrupt threshold values using a tuple of
        zero to three values: low threshold, high threshold, persistence.
        persistence defaults to 4 if not provided"""
        return (
            self._read8(_APDS9960_PILT),
            self._read8(_APDS9960_PIHT),
            self._proximity_persistence,
        )

    @proximity_interrupt_threshold.setter
    def proximity_interrupt_threshold(self, setting_tuple: Tuple[int, ...]) -> None:
        if setting_tuple:
            self._write8(_APDS9960_PILT, setting_tuple[0])
        if len(setting_tuple) > 1:
            self._write8(_APDS9960_PIHT, setting_tuple[1])
        persist = 4  # default 4
        if len(setting_tuple) > 2:
            persist = min(setting_tuple[2], 7)
        self._proximity_persistence = persist

    @property
    def proximity(self) -> int:
        """Proximity value: range 0-255"""
        return self._read8(_APDS9960_PDATA)

    def clear_interrupt(self) -> None:
        """Clear all interrupts"""
        self._writecmdonly(_APDS9960_AICLEAR)

    # method for reading and writing to I2C
    def _write8(self, command: int, abyte: int) -> None:
        """Write a command and 1 byte of data to the I2C device"""
        buf = self.buf2
        buf[0] = command
        buf[1] = abyte
        with self.i2c_device as i2c:
            i2c.write(buf)

    def _writecmdonly(self, command: int) -> None:
        """Writes a command and 0 bytes of data to the I2C device"""
        buf = self.buf2
        buf[0] = command
        with self.i2c_device as i2c:
            i2c.write(buf, end=1)

    def _read8(self, command: int) -> int:
        """Sends a command and reads 1 byte of data from the I2C device"""
        buf = self.buf2
        buf[0] = command
        with self.i2c_device as i2c:
            i2c.write_then_readinto(buf, buf, out_end=1, in_end=1)
        return buf[0]

    def _get_bit(self, register: int, bitmask: int) -> int:
        buf = self.buf2
        buf[0] = register
        with self.i2c_device as i2c:
            i2c.write_then_readinto(buf, buf, out_end=1, in_start=1)
        return bool(buf[1] & bitmask)

    def _set_bit(self, register: int, bitmask: int, value: bool) -> None:
        buf = self.buf2
        buf[0] = register
        with self.i2c_device as i2c:
            i2c.write_then_readinto(buf, buf, out_end=1, in_start=1)
        if value:
            buf[1] |= bitmask
        else:
            buf[1] &= ~bitmask
        with self.i2c_device as i2c:
            i2c.write(buf, end=2)

    def _get_bits(self, register: int, bit_position: int, bit_mask: int) -> int:
        buf = self.buf2
        buf[0] = register
        with self.i2c_device as i2c:
            i2c.write_then_readinto(buf, buf, out_end=1, in_start=1)
        return (buf[1] & bit_mask) >> bit_position

    def _set_bits(self, register: int, bit_position: int, bit_mask: int, value: int) -> None:
        buf = self.buf2
        buf[0] = register
        with self.i2c_device as i2c:
            i2c.write_then_readinto(buf, buf, out_end=1, in_start=1)
        buf[1] = (buf[1] & ~bit_mask) | (value << bit_position)
        with self.i2c_device as i2c:
            i2c.write(buf, end=2)
        
    def _color_data16(self, command: int) -> int:
        """Sends a command and reads 2 bytes of data from the I2C device
        The returned data is low byte first followed by high byte"""
        buf = self.buf2
        buf[0] = command
        with self.i2c_device as i2c:
            i2c.write_then_readinto(buf, buf, out_end=1)
        return buf[1] << 8 | buf[0]
