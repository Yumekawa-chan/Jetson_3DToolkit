import socket
import datetime
import cv2
import io

def capture_image():
    cap = cv2.VideoCapture(2)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("Failed to capture image")
        return None, None

    color_image = frame
    depth_image = frame 

    mem_buffer_color = io.BytesIO()
    is_success_color, buffer_color = cv2.imencode(".png", color_image)
    mem_buffer_color.write(buffer_color)


    mem_buffer_depth = io.BytesIO()
    is_success_depth, buffer_depth = cv2.imencode(".png", depth_image)
    mem_buffer_depth.write(buffer_depth)

    return mem_buffer_color.getvalue(), mem_buffer_depth.getvalue()

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
