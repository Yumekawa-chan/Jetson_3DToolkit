import socket
import datetime
import cv2
import io

def capture_image():
    cap = cv2.VideoCapture(2)
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        return None

    mem_buffer = io.BytesIO()
    is_success, buffer = cv2.imencode(".png", frame)
    mem_buffer.write(buffer)

    cap.release()

    return mem_buffer.getvalue()

def connect_and_handle_server(jetson_id):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('192.168.10.117', 65432))
        print(f"Connected to server at 192.168.10.117:65432")

        while True:
            data = client_socket.recv(1024)
            if data == b'capture':
                image_data = capture_image()
                if image_data:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{timestamp}_{jetson_id}.png"
                    client_socket.sendall(filename.encode() + b'\n')
                    client_socket.sendall(image_data)
                    client_socket.sendall(b'ENDOFIMAGE')

jetson_id = 1
connect_and_handle_server(jetson_id)
