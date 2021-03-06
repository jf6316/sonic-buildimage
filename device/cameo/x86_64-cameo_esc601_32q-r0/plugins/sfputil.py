#!/usr/bin/env python

try:
    import time
    from sonic_sfp.sfputilbase import SfpUtilBase 
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")

attr_path = '/sys/class/hwmon/hwmon2/device/'

class SfpUtil(SfpUtilBase):
    """Platform specific SfpUtill class"""

    _port_start = 0
    _port_end = 31
    _port_in_block =32
    _port_to_eeprom_mapping = {}
    _global_port_pres_dict = {}

    def __init__(self):
        eeprom_path = "/sys/bus/i2c/devices/{0}-0050/eeprom"
        for x in range(self._port_start, self._port_end + 1):
            port_eeprom_path = eeprom_path.format(x+9)
            self._port_to_eeprom_mapping[x] = port_eeprom_path

        self.init_global_port_presence()        
        SfpUtilBase.__init__(self)

    def reset(self, port_num):
        # Check for invalid port_num
        if port_num < self._port_start or port_num > self._port_end:
            return False

        path = attr_path+'ESC601_QSFP/QSFP_reset'
        try:
            reg_file = open(path, 'w')
        except IOError as e:
            print( "Error: unable to open file: %s" % str(e))
            return False

        #toggle reset
        #reg_file.seek(0)
        reg_file.write(str(port_num+1))
        #time.sleep(1)
        #reg_file.seek(0)
        #reg_file.write('0')
        reg_file.close()
        return True

    def set_low_power_mode(self, port_num, lpmode):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        path = attr_path+'ESC601_QSFP/QSFP_low_power_'+str(port_num+1)
        try:
            reg_file = open(path, 'w')
        except IOError as e:
            print( "Error: unable to open file: %s" % str(e))
            return False

        # the gpio pin is ACTIVE_HIGH
        if lpmode is True:
            val = "1"
        else:
            val = "0"

        # write value to gpio
        reg_file.seek(0)
        reg_file.write(val)
        reg_file.close()

        return True

    def get_low_power_mode(self, port_num):
        # Check for invalid port_num
        if port_num < self._port_start or port_num > self._port_end:
            return False

        path = attr_path+'ESC601_QSFP/QSFP_low_power_'+str(port_num+1)
        try:
          reg_file = open(path, 'r')
        except IOError as e:
            print( "Error: unable to open file: %s" % str(e))
            return False 
       
        text_lines = reg_file.readline()
        reg_file.close()
        if text_lines.find('OFF') < 0:
            return True

        return False
        
    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self._port_start or port_num > self._port_end:
            return False

        path = attr_path+'ESC601_QSFP/QSFP_present'
        try:
          reg_file = open(path, 'r')
        except IOError as e:
            print( "Error: unable to open file: %s" % str(e))
            return False
        text_lines = reg_file.readlines()
        reg_file.close()
        if text_lines[port_num].find('not') < 0:
            return True

        return False

    def init_global_port_presence(self):
        for port_num in range(self.port_start, (self.port_end + 1)):
            presence = self.get_presence(port_num)
            if(presence):
                self._global_port_pres_dict[port_num] = '1'
            else:
                self._global_port_pres_dict[port_num] = '0'  
 
    def get_transceiver_change_event(self, timeout=0):
        port_dict = {}
        while True:
            for port_num in range(self.port_start, (self.port_end + 1)):
                presence = self.get_presence(port_num)
                if(presence and self._global_port_pres_dict[port_num] == '0'):
                    self._global_port_pres_dict[port_num] = '1'
                    port_dict[port_num] = '1'
                elif(not presence and
                     self._global_port_pres_dict[port_num] == '1'):
                    self._global_port_pres_dict[port_num] = '0'
                    port_dict[port_num] = '0'

                if(len(port_dict) > 0):
                    return True, port_dict

            time.sleep(1)

    @property
    def port_start(self):
        return self._port_start

    @property
    def port_end(self):
        return self._port_end

    @property
    def qsfp_ports(self):
        return range(0, self._port_in_block + 1)

    @property 
    def port_to_eeprom_mapping(self):
         return self._port_to_eeprom_mapping
