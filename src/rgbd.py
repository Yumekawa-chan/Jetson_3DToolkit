import socket
import datetime
import numpy as np
import cv2
import pyrealsense2 as rs

def capture_images():
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
            return None, None

        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        return depth_image, color_image
    finally:
        pipeline.stop()

def connect_and_handle_server(jetson_id):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('192.168.10.117', 65432))
        print(f"Connected to server at 192.168.10.117:65432")

        # Send camera parameters
        pipeline = rs.pipeline()
        config = rs.config()
        pipeline.start(config)
        profile = pipeline.get_active_profile()
        depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
        intrinsics = depth_profile.get_intrinsics()
        params_data = np.array([intrinsics.width, intrinsics.height, intrinsics.fx, intrinsics.fy, intrinsics.ppx, intrinsics.ppy], dtype=np.float32).tobytes()
        params_size_info = f"{len(params_data)}\n".encode()
        client_socket.sendall(params_size_info + params_data)
        pipeline.stop()

        while True:
            data = client_socket.recv(1024)
            if data == b'capture':
                depth_image, color_image = capture_images()
                if depth_image is not None and color_image is not None:
                    # Send depth image
                    depth_filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{jetson_id}_depth.png"
                    client_socket.sendall(depth_filename.encode() + b'\n')
                    is_success, buffer = cv2.imencode(".png", depth_image)
                    client_socket.sendall(buffer.tobytes() + b'ENDOFIMAGE')

                    # Send color image
                    color_filename = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{jetson_id}_color.png"
                    client_socket.sendall(color_filename.encode() + b'\n')
                    is_success, buffer = cv2.imencode(".png", color_image)
                    client_socket.sendall(buffer.tobytes() + b'ENDOFIMAGE')

jetson_id = 1
connect_and_handle_server(jetson_id)
