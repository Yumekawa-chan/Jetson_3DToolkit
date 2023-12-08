import socket
import datetime
import cv2
import threading
import io

def capture_image():
    # カメラの初期化
    cap = cv2.VideoCapture(0)  # 0はデフォルトのカメラを指します
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        return None

    # メモリバッファに画像を保存
    mem_buffer = io.BytesIO()
    is_success, buffer = cv2.imencode(".png", frame)
    mem_buffer.write(buffer)

    # カメラのリリース
    cap.release()

    # バッファからバイトデータを取得
    return mem_buffer.getvalue()

def handle_client(client, jetson_id):
    while True:
        data = client.recv(1024)
        if data == b'capture':
            image_data = capture_image()
            if image_data:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{jetson_id}.png"
                client.sendall(filename.encode() + b'\n' + image_data)

def accept_clients():
    while True:
        client, addr = server.accept()
        jetson_id = len(clients) + 1  # JetsonデバイスのID
        clients.append(client)
        print(f'Connected by {addr}')
        threading.Thread(target=handle_client, args=(client, jetson_id), daemon=True).start()

clients = []
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 65432))
server.listen()

accept_clients()
