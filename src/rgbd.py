import socket
import pyrealsense2 as rs
import numpy as np
import cv2
import time

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

        return color_image, depth_image

    finally:
        pipeline.stop()

def send_image_to_server(image, image_name, server_ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_ip, port))

        # ファイル名を先に送信
        s.sendall(image_name.encode())

        # 画像データを送信
        is_success, buffer = cv2.imencode(".png", image)
        if is_success:
            s.sendall(buffer.tobytes())

def main():
    server_ip = '192.168.10.117'  # WindowsマシンのIPアドレス
    port = 12345                     # サーバーのポート番号

    while True:
        color_image, depth_image = capture_images()
        if color_image is not None and depth_image is not None:
            timestamp = int(time.time())

            # カラー画像を送信
            send_image_to_server(color_image, f"color/{timestamp}.png", server_ip, port)

            # 深度画像を送信
            send_image_to_server(depth_image, f"depth/{timestamp}.png", server_ip, port)


if __name__ == "__main__":
    main()
