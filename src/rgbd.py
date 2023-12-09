import socket
import pyrealsense2 as rs
import numpy as np
import cv2
import io
import datetime

def capture_image_and_params():
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
            return None, None, None

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        depth_intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
        params = np.array([depth_intrinsics.width, depth_intrinsics.height, depth_intrinsics.fx, depth_intrinsics.fy, depth_intrinsics.ppx, depth_intrinsics.ppy], dtype=np.float32)

        return depth_image, color_image, params
    finally:
        pipeline.stop()

def connect_and_handle_server(jetson_id, server_ip, server_port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_ip, server_port))
        print(f"Connected to server at {server_ip}:{server_port}")

        while True:
            data = client_socket.recv(1024)
            if data == b'capture':
                depth_image, color_image, params = capture_image_and_params()
                if depth_image is not None and color_image is not None:
                    # Send depth image
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    depth_filename = f"{timestamp}_{jetson_id}_depth.png"
                    client_socket.sendall(depth_filename.encode() + b'\n')
                    _, buffer = cv2.imencode(".png", depth_image)
                    client_socket.sendall(buffer.tobytes() + b'ENDOFIMAGE')

                    # Send color image
                    color_filename = f"{timestamp}_{jetson_id}_color.png"
                    client_socket.sendall(color_filename.encode() + b'\n')
                    _, buffer = cv2.imencode(".png", color_image)
                    client_socket.sendall(buffer.tobytes() + b'ENDOFIMAGE')

                    # Send parameters
                    param_filename = f"{timestamp}_{jetson_id}_params.npy"
                    client_socket.sendall(param_filename.encode() + b'\n')
                    client_socket.sendall(params.tobytes() + b'ENDOFPARAMS')

jetson_id = 1
server_ip = '192.168.10.117'  # Server IP address
server_port = 65432  # Server port
connect_and_handle_server(jetson_id, server_ip, server_port)
