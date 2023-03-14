"""Write udev rules for the USB2AX and the cameras used in Reachy 2023.

Run this script with sudo.
"""

import glob
from subprocess import run, PIPE


def _get_serial_number(port):
    """Get serial number for a gate or camera on a given port."""
    pipe1 = run(
        [f"udevadm info -a -p $(udevadm info -q path -n /{port})"],
        stdout=PIPE,
        shell=True,
    )
    pipe2 = run(
        ["grep ATTRS{serial}"],
        input=pipe1.stdout,
        stdout=PIPE,
        shell=True,
    )
    out = pipe2.stdout.decode().split()
    serial_number = out[0].split("=")[-1]
    return serial_number


def _get_usb2axhead_port(port_candidates):
    """Get usb port for the usb2ax inside Reachy's head.

    Because there are two usb devices in /dev/ttyACM* in Reachy' s head
    (one for the usb2ax board and the other for the zoom Kurokesu board),
    we need to identify which port is actually the one for the usb2ax board.
    """
    for port in port_candidates:
        pipe1 = run(
            [f"udevadm info -a -p $(udevadm info -q path -n /{port})"],
            stdout=PIPE,
            shell=True,
        )
        pipe2 = run(
            ["grep USB2AX"],
            input=pipe1.stdout,
            stdout=PIPE,
            shell=True,
        )
        if pipe2.stdout.decode().split() != []:
            head_port = port

    return [head_port]


def _get_camera_ports():
    """Each camera opens 4 video ports in /dev. We need to pick the correct one."""
    video_ports = glob.glob("/dev/video*")
    camera_ports = []

    for port in video_ports:
        pipe_udevadm = run(
            [f"udevadm info -a -p $(udevadm info -q path -n /{port})"],
            stdout=PIPE,
            shell=True,
        )
        pipe_index = run(
            ["grep ATTR{index}"],
            input=pipe_udevadm.stdout,
            stdout=PIPE,
            shell=True,
        )

        if pipe_index.stdout.decode().split()[0] == 'ATTR{index}=="0"':
            pipe_kurokesu = run(
                ["grep Kurokesu"],
                input=pipe_udevadm.stdout,
                stdout=PIPE,
                shell=True,
            )
            if pipe_kurokesu.stdout.decode().split() != []:
                camera_ports.append(port)

    return camera_ports


def _get_rule_msg_usb2ax(port, robot_part):
    """Build a udev rule given a gate serial number."""
    serial_number = _get_serial_number(port[0])
    rule = f"# Rules for the {robot_part} usb2ax board \n"
    rule += 'KERNEL=="ttyACM[0-9]", ATTRS{idVendor}=="16d0", ATTRS{product}=="USB2AX", '
    rule += f'ATTRS{{serial}}=={serial_number}, MODE="666", SYMLINK+="usb2ax_{robot_part}"\n'
    return rule


def _get_rule_msg_cameras(ports):
    """Build a udev rule for both cameras, assuming the first port is for the right camera."""
    serial_number_right = _get_serial_number(ports[0])
    rule = "# Rules for the Kurokesu cameras \n"
    rule += f'KERNEL=="video[0-9]", ATTR{{index}}=="0", ATTRS{{serial}}=={serial_number_right}, SYMLINK+="right_camera"\n'
    serial_number_left = _get_serial_number(ports[1])
    rule += f'KERNEL=="video[0-9]", ATTR{{index}}=="0", ATTRS{{serial}}=={serial_number_left}, SYMLINK+="left_camera"\n'
    return rule


def write_udev_rules_usb2ax(robot_part):
    """Write udev rule for a usb2ax board in Reachy.

    For each usb2axnboard on /dev/ttyACM*, get its serial number, a udev rule associated
    and write it in the local udev file /etc/udev/rules.d/10-reachy-local.rules.
    """
    if robot_part not in ["left_arm", "right_arm", "head"]:
        print(
            "Robot part should be in ['left_arm', 'right_arm', 'head'], got {robot_part}."
        )
        return

    with open("/etc/udev/rules.d/10-reachy-local.rules", "r") as f:
        contents = f.readlines()

    port = glob.glob("/dev/ttyACM*")

    if port == []:
        print("No usb2ax detected, make sure that one is connected.")
        return

    if len(port) != 1:
        if robot_part == "head":
            port = _get_usb2axhead_port(port)
        else:
            print("Multiple usb2ax detected, make sure that only one is connected.")
            return

    with open("/etc/udev/rules.d/10-reachy-local.rules", "w") as fa:
        rule = _get_rule_msg_usb2ax(port, robot_part)
        fa.writelines(contents + [rule])
        fa.close()
        print(f"Wrote udev rule for {robot_part}!")


def write_udev_rules_cameras():
    """Write udev rules for Reachy's cameras.

    Each Reachy's camera opens four video ports on /dev/video*.
    The goal is to get for each camera the video port with ATTR{index}==0, get the
    serial number of the camera, create a udev rule associated and write it in Reachy's
    udev rules file.
    We assume that the first video port found is for the right camera (it is often the case).
    We will be able to verify easily if the port assumed for the left camera is correct
    or not. If not, we will only have to invert the symlink for left_camera and right_camera
    in Reachy's udev rules file. This way we won't have to open Reachy's head to disconnect
    the cameras one by one to make sure we are writing the rule for the correct side. 
    """
    with open("/etc/udev/rules.d/10-reachy-local.rules", "r") as f:
        contents = f.readlines()

    ports = glob.glob("/dev/ttyACM*")

    if ports == [0]:
        print('No cameras detected.')
        return

    if len(ports) < 8:
        print('Unable to detect both cameras.')
        return

    with open("/etc/udev/rules.d/10-reachy-local.rules", "w") as fa:
        camera_ports = _get_camera_ports(ports)
        rules = _get_rule_msg_cameras(camera_ports)
        fa.writelines(contents + [rules])
        fa.close()
        print('Wrote udev rules for cameras!')

