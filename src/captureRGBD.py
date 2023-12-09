import socket
import datetime
import pyrealsense2 as rs
import numpy as np
import cv2
import io

def capture_image():
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start the camera pipeline
    pipeline.start(config)

    try:
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if not depth_frame or not color_frame:
            print("Failed to capture images")
            return None, None

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Apply colormap on depth image
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Encode images
        mem_buffer_color = io.BytesIO()
        mem_buffer_depth = io.BytesIO()
        is_success_color, buffer_color = cv2.imencode(".png", color_image)
        is_success_depth, buffer_depth = cv2.imencode(".png", depth_colormap)
        mem_buffer_color.write(buffer_color)
        mem_buffer_depth.write(buffer_depth)

        return mem_buffer_color.getvalue(), mem_buffer_depth.getvalue()
    finally:
        pipeline.stop()

def connect_and_handle_server(jetson_id):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('192.168.10.117', 65432))
        print(f"Connected to server at 192.168.10.117:65432")

        while True:
            data = client_socket.recv(1024)
            if data == b'capture':
                color_image_data, depth_image_data = capture_image()
                if color_image_data and depth_image_data:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    color_filename = f"{timestamp}_{jetson_id}_color.png"
                    depth_filename = f"{timestamp}_{jetson_id}_depth.png"
                    client_socket.sendall(color_filename.encode() + b'\n')
                    client_socket.sendall(color_image_data)
                    client_socket.sendall(b'ENDOFIMAGE')
                    client_socket.sendall(depth_filename.encode() + b'\n')
                    client_socket.sendall(depth_image_data)
                    client_socket.sendall(b'ENDOFIMAGE')

jetson_id = 1
connect_and_handle_server(jetson_id)
