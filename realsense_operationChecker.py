import pyrealsense2 as rs
import time

# pyrealsense2.context
ctx = rs.context()

# pyrealsense2.device_list
devices = ctx.query_devices()

for device in devices:  # pyrealsense2.device
    print("serial_number:", device.get_info(rs.camera_info.serial_number))
    print("asic_serial_number:", device.get_info(
        rs.camera_info.asic_serial_number))
    print("Realsense is correctly connected!")
