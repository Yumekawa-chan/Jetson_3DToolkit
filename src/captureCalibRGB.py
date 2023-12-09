import socket
import datetime
import cv2
import io
import pyrealsense2 as rs
import numpy as np

def capture_depth_color_images():
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    pipeline.start(config)

    try:
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if not depth_frame or not color_frame:
            print("Could not acquire depth or color frames.")
            return None, None
        depth_image = np.asanyarray(depth_frame.get_data())

        color_image = np.asanyarray(color_frame.get_data())

        depth_buffer = io.BytesIO()
        color_buffer = io.BytesIO()
        cv2.imencode('.png', depth_image, depth_buffer)
        cv2.imencode('.png', color_image, color_buffer)

        return depth_buffer.getvalue(), color_buffer.getvalue()
    finally:
        pipeline.stop()

def connect_and_handle_server(jetson_id):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('192.168.10.117', 65432))
        print(f"Connected to server at 192.168.10.117:65432")

        while True:
            data = client_socket.recv(1024)
            if data == b'capture':
                depth_data, color_data = capture_depth_color_images()
                if depth_data and color_data:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    depth_filename = f"{timestamp}_{jetson_id}_depth.png"
                    color_filename = f"{timestamp}_{jetson_id}_color.png"

                    client_socket.sendall(depth_filename.encode() + b'\n')
                    client_socket.sendall(depth_data)
                    client_socket.sendall(b'ENDOFIMAGE')

                    client_socket.sendall(color_filename.encode() + b'\n')
                    client_socket.sendall(color_data)
                    client_socket.sendall(b'ENDOFIMAGE')

jetson_id = 1
connect_and_handle_server(jetson_id)
