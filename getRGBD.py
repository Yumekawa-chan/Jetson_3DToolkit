import socket
import pyrealsense2 as rs
import numpy as np
import cv2
import os
from datetime import datetime

jet_id = 1

def capture_images():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    pipeline.start(config)

    try:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()

        if not depth_frame or not color_frame:
            return

        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        cv2.imwrite(f'image/color_{timestamp}_{jet_id}.png', color_image)
        cv2.imwrite(f'image/depth_{timestamp}_{jet_id}.png', depth_image)

    finally:
        pipeline.stop()

host = '192.168.10.125'
port = 65432

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client_socket.connect((host, port))
    print("Connected to server")

    while True:
        data = client_socket.recv(1024).decode()

        if data == 'capture':
            capture_images()
        elif data == 'exit':
            break

finally:
    client_socket.close()
    print("Connection closed")
