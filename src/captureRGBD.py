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

    # Start streaming
    pipeline.start(config)

    try:
        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if not depth_frame or not color_frame:
            print("Could not acquire depth or color frames.")
            return None, None

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Convert depth image to 8-bit for visualization
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # Encode the frames as jpeg to send over the network
        is_success_color, buffer_color = cv2.imencode(".png", color_image)
        is_success_depth, buffer_depth = cv2.imencode(".png", depth_colormap)

        if not is_success_color or not is_success_depth:
            print("Could not encode images.")
            return None, None

        return buffer_color.tobytes(), buffer_depth.tobytes()
    finally:
        # Stop streaming
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
                    client_socket.sendall(f"FILENAME:{color_filename}\n".encode())
                    client_socket.sendall(color_image_data)
                    client_socket.sendall(b'ENDOFIMAGE')
                    client_socket.recv(1024) 
                    client_socket.sendall(f"FILENAME:{depth_filename}\n".encode())
                    client_socket.sendall(depth_image_data)
                    client_socket.sendall(b'ENDOFIMAGE')
                    client_socket.recv(1024) 

jetson_id = 1
connect_and_handle_server(jetson_id)
