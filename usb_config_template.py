import os
import sys
import logging
#
# Template format: (type of the value, possible_choice_list)
# Type of the value : str, int, bool
# Choice list : List of possible value , None if no default value.
#

remote_terminal_template = {
    'type' : ("str", ['serial', 'adb', 'local'])
}

serial_template = {
    'name': ("str", []),
    'baudrate': ("int", [9600, 115200]),
    'parity': ("str", ['Odd', 'Even', 'None']),
    'stopbit': ("int", [1.5, 1, 2]),
    'bytesize': ("int", [8, 7, 6, 5]),
    'hfc': ("bool", [True, False]),
    'sfc': ("bool", [True, False]),
    'timeout' : ("int", [])
}

adb_template = {
    'name': ("str", [])
}

local_template = {
    'name' : ("str", [])
}

test_1_template = {
    'name': ("str", []),
    'type': ("str", []),
    'remote_cmd': ("str", []),
    'local_cmd': ("str", []),
    'remote_expected_result': ("str", []),
    'local_expected_result': ("str", []),
    'local_cmd_timeout': ("int", []),
    'remote_cmd_timeout': ("int", []),
}

config_template = {
    'remote_terminal' : remote_terminal_template,
    'serial' : serial_template,
    'adb'   : adb_template,
    'local'   : local_template,
    'test_1'    : test_1_template,
    'test_2': test_1_template,
    'test_3': test_1_template
}

if __name__ == "__main__":
    print config_template