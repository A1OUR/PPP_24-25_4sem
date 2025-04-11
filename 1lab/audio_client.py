# import socket
from common_stuff import *
    
def run_client():
    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostname = socket.gethostname()
        client.connect((hostname, PORT))
        message = input("Input a text: ")
        try:
            message = message.encode()
            size = struct.pack('!I', len(message))
            client.sendall(size)
            client.sendall(message)
            response = client.recv(1)
            response = struct.unpack('B',response)[0]
            size = client.recv(4)
            size = struct.unpack('!I', size)[0]
            received = 0
            actual_data = bytearray()
            while received < size:
                chunk = client.recv(min(4096, size - received))
                if not chunk:
                    break
                actual_data.extend(chunk)
                received += len(chunk)
            if response == 0:
                message = actual_data.decode('utf-8')
                print(f"Сообщение от сервера:{message}")
            else:
                f = open("out.mp3", 'wb')
                f.write(actual_data)
                f.close()
                print(f"Фрагмент получен")
            client.close()
        except ConnectionResetError:
            print("Сервер разорвал подключение, завершение работы...") 
            exit()