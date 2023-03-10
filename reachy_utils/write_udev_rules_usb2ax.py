"""Write udev rules for the USB2AX used in Reachy 2023.

Run this script with sudo.
"""

import glob
from subprocess import run, PIPE
import sys


def get_serial_number(port):
    """Get serial number for a gate on a given port."""
    pipe1 = run(
        [f'udevadm info -a -p $(udevadm info -q path -n /{port})'],
        stdout=PIPE,
        shell=True,
    )
    pipe2 = run(
        ['grep ATTRS{serial}'],
        input=pipe1.stdout,
        stdout=PIPE,
        shell=True,
    )
    out = pipe2.stdout.decode().split()
    serial_number = out[0].split('=')[-1]
    return serial_number


def get_rule_msg(port, robot_part):
    """Build a udev rule given a gate serial number."""
    serial_number = get_serial_number(port[0])
    rule = 'KERNEL=="ttyACM[0-9]", ATTRS{idVendor}=="16d0", ATTRS{product}=="USB2AX", '
    rule += f'ATTRS{{serial}}=={serial_number}, MODE="666", SYMLINK+="usb2ax_{robot_part}"\n'
    return rule


def write_udev_rules():
    """Run main function.

    For each gate on /dev/ttyUSB*, get its serial number, a udev rule associated
    and write it in the local udev file /etc/udev/rules.d/10-reachy-local.rules.
    If previous rules were written for the gates, they are deleted.
    """
    with open('/etc/udev/rules.d/10-reachy-local.rules', 'r') as f:
        contents = f.readlines()

    port = glob.glob('/dev/ttyACM*')

    if port == []:
        print('No usb2ax detected, make sure that one is connected.')
        return

    if len(port) != 1:
        print('Multiple usb2ax detected, make sure that only one is connected.')
        return

    robot_part = sys.argv[1]
    if robot_part not in ['left_arm', 'right_arm', 'head']:
        print("Robot part should be in ['left_arm', 'right_arm', 'head'], got {robot_part}.")
        return

    with open('/etc/udev/rules.d/10-reachy-local.rules', 'w') as fa:
        rule = get_rule_msg(port, robot_part)
        fa.writelines(contents + [rule])
        fa.close()
        print(f'Wrote udev rule for {robot_part}!')


if __name__ == '__main__':
    write_udev_rules()
