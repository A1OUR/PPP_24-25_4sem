from common_stuff import *
DOWNLOAD_PATH = os.getcwd()+"\\downloads\\"


def parse_filename(message):
    result = message.replace('"', "'")
    name, ext = os.path.splitext(result[result.find("'") + 1:result.rfind("'")])
    result = DOWNLOAD_PATH + name + result[result.rfind("'") + 1:] + ext
    return result


def run_client():
    if not os.path.isdir(DOWNLOAD_PATH):
        os.mkdir(DOWNLOAD_PATH)
    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostname = socket.gethostname()
        client.connect((hostname, PORT))
        inputed_message = input("Введите запрос: ")
        try:
            message = inputed_message.encode()
            size = struct.pack('!I', len(message))
            client.sendall(size)
            client.sendall(message)
            response = client.recv(1)
            response = struct.unpack('B', response)[0]
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
                f = open(parse_filename(inputed_message), 'wb')
                f.write(actual_data)
                f.close()
                print(f"Фрагмент получен")
            client.close()
        except ConnectionResetError:
            print("Сервер разорвал подключение, завершение работы...")
            exit()
