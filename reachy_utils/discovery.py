from pypot.dynamixel import DxlIO, Dxl320IO
from reachy_utils.config import get_reachy_model
from serial import SerialException
from subprocess import run, PIPE
from typing import Dict


motor_ids_per_part = {
    "right_arm": [10, 11, 12, 13, 14, 15, 16, 17],
    "left_arm": [20, 21, 22, 23, 24, 25, 26, 27],
    "head": [40, 31, 32],
}

robot_config_to_parts = {
    "full_kit": ["right_arm", "left_arm", "head"],
    "starter_kit_left": ["left_arm", "head"],
    "starter_kit_right": ["right_arm", "head"],
}

motor_id_to_name = {
    10: "r_shoulder_pitch",
    11: "r_shoulder_roll",
    12: "r_arm_yaw",
    13: "r_elbow_pitch",
    14: "r_forearm_yaw",
    15: "r_wrist_pitch",
    16: "r_wrist_yaw",
    17: "r_gripper",
    20: "l_shoulder_pitch",
    21: "l_shoulder_roll",
    22: "l_arm_yaw",
    23: "l_elbow_pitch",
    24: "l_forearm_yaw",
    25: "l_wrist_pitch",
    26: "l_wrist_yaw",
    27: "l_gripper",
    30: "r_antenna",
    31: "l_antenna",
    40: "neck_orbita",
}


def get_missing_motors_arm(arm: str, missing_motors: Dict):
    try:
        dxl_io = DxlIO(port=f"/dev/usb2ax_{arm}")
    except SerialException:
        print(
            f"Port /dev/usb2ax_{arm} not found. Make sure that the udev rules is set and the usb2ax board plugged."
        )
        return

    scan = dxl_io.scan(range(40))
    for motor_id in motor_ids_per_part[arm]:
        if motor_id not in scan:
            missing_motors[motor_id] = motor_id_to_name[motor_id]

    return missing_motors


def get_missing_motors_head(missing_motors: Dict):
    try:
        dxl320_io = Dxl320IO(port="/dev/usb2ax_head")
    except SerialException:
        print(
            "Port /dev/usb2ax_head not found. Make sure that the udev rules is set and the usb2ax board plugged."
        )
        return

    scan_antennas = dxl320_io.scan([30, 31])
    for motor_id in [30, 31]:
        if motor_id not in scan_antennas:
            missing_motors[motor_id] = motor_id_to_name[motor_id]

    dxl320_io.close()

    dxl_io = DxlIO(port="/dev/usb2ax_head")
    scan_orbita = dxl_io.scan([40])
    if scan_orbita == []:
        missing_motors[40] = "orbita"

    return missing_motors


def get_missing_motors_reachy(reachy_model: str):
    missing_motors = {}

    for part in robot_config_to_parts[reachy_model]:
        if "arm" in part:
            missing_motors = get_missing_motors_arm(part, missing_motors)

        elif "head" in part:
            missing_motors = get_missing_motors_head(missing_motors)

    return missing_motors


def scan():
    reachy_model = get_reachy_model()
    print(f"Scanning if there are any missing motors for Reachy {reachy_model}...")

    pipe = run(
        ["systemctl --user is-active reachy_sdk_server.service"],
        stdout=PIPE,
        shell=True,
    )
    status = pipe.stdout.decode().split()

    if status[0] == "active":
        print("Disabling reachy_sdk_server.service to access the usb2ax boards.")
        run(
            ["systemctl --user stop reachy_sdk_server.service"], stdout=PIPE, shell=True
        )

    missing_motors = get_missing_motors_reachy(reachy_model)

    if missing_motors == {}:
        print(f"Found all motors for Reachy {reachy_model}!")
    else:
        print(f"Found missing motors for Reachy {reachy_model}: {missing_motors}")


if __name__ == "__main__":
    scan()
