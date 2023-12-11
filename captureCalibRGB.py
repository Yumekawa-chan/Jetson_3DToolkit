import socket
import datetime
import cv2
import os

def capture_image(jetson_id):
    cap = cv2.VideoCapture(2)
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"image/{timestamp}_{jetson_id}.png"

    if not os.path.exists('image'):
        os.makedirs('image')

    cv2.imwrite(filename, frame)
    print(f"Image saved as {filename}")

    cap.release()

def connect_and_handle_server(jetson_id):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('192.168.10.125', 65432))
        print(f"Connected to server")

        while True:
            data = client_socket.recv(1024)
            if data == b'capture':
                capture_image(jetson_id)

jetson_id = 1 
connect_and_handle_server(jetson_id)
