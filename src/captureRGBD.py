import os
import cv2
import numpy as np
import pyrealsense2 as rs
from datetime import datetime


class RealSenseCapture:
    DEPTH_MIN = 150
    DEPTH_MAX = 15000

    def __init__(self):
        self.pipeline = rs.pipeline()
        self.configure_pipeline()
        self.pc = rs.pointcloud()
        self.initialize_directories()

    def configure_pipeline(self):
        config = rs.config()
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        self.pipeline.start(config)

    def initialize_directories(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        folder_name = datetime.now().strftime("%Y%m%d")
        self.pointclouds_dir = os.path.join(
            base_dir, '..', 'data', 'pointclouds', folder_name)
        self.depths_dir = os.path.join(
            base_dir, '..', 'data', 'depths', folder_name)
        self.colors_dir = os.path.join(
            base_dir, '..', 'data', 'colors', folder_name)
        os.makedirs(self.pointclouds_dir, exist_ok=True)

    def process_frame(self):
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        depth_image = self.process_depth_frame(depth_frame)
        return depth_frame, color_frame, depth_image

    def process_depth_frame(self, depth_frame):
        depth_image = np.asanyarray(depth_frame.get_data())
        depth_image[(depth_image < self.DEPTH_MIN) |
                    (depth_image > self.DEPTH_MAX)] = 0
        depth_colormap = cv2.normalize(
            depth_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        depth_colormap = cv2.medianBlur(depth_colormap, 5)
        return depth_colormap

    def save_pointcloud(self, depth_frame, color_frame):
        timestamp = datetime.now().strftime("%H%M%S")
        self.pc.map_to(color_frame)
        pointcloud = self.pc.calculate(depth_frame)
        ply_file_path = os.path.join(self.pointclouds_dir, f'{timestamp}.ply')
        pointcloud.export_to_ply(ply_file_path, color_frame)
        print(f'Pointcloud saved at {ply_file_path}')

    def stop(self):
        self.pipeline.stop()


if __name__ == "__main__":
    capture = RealSenseCapture()
    try:
        while True:
            depth_frame, color_frame, depth_image = capture.process_frame()
            capture.save_pointcloud(depth_frame, color_frame)
    finally:
        capture.stop()
