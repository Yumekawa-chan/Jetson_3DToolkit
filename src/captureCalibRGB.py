import socket
import threading


def wait_for_key():
    input("Press Enter to send capture command...")
    for client in clients:
        client.sendall(b'capture')


def accept_clients():
    while True:
        client, addr = server.accept()
        clients.append(client)
        print(f'Connected by {addr}')


clients = []
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 65432))
server.listen()

threading.Thread(target=accept_clients).start()
wait_for_key()
