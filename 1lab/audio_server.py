from _thread import start_new_thread
from common_stuff import *
import json
from pydub import AudioSegment
METADATA_FILE = "audio_metadata.json"
FILES_PATH = os.getcwd()+"\\audio_files\\"

def update_metadata():
    metadata = {}

    for filename in os.listdir(FILES_PATH):
        filepath = os.path.join(FILES_PATH, filename)
        if os.path.isfile(filepath):
            try:
                ext = os.path.splitext(filepath)[1][1:]
                metadata[filename] = {
                    'Формат': ext,
                    'Длительность': f'{round(AudioSegment.from_file(filepath, ext).duration_seconds, 2)} s.',
                    'Размер': f'{round(os.path.getsize(filepath) / 1024, 2)} KB'
                }
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)


def get_audio_list():
    update_metadata()
    message = "\nСписок файлов на сервере:"
    with open(METADATA_FILE, 'r') as f:
        raw = json.load(f)
        for name, params in raw.items():
            message += f"\n'{name}':"
            for param_name, value in params.items():
                message += f' {param_name}:{value}'
    return message


def parse_input(data):
    args = []
    data = data.replace('"', "'")
    if not " " in data:
        args.append(data)
    else:
        first_space = data.find(" ")
        args.append(data[:first_space])
        data_rest = data[first_space + 1:]
        if data.count("'") < 2:
            return False
        else:
            if data_rest[0] != "'":
                return False
            else:
                args.append(data_rest[1:data_rest.rfind("'")])
                data_rest = data_rest[data_rest.rfind("'") + 1:]
                if len(data_rest) == 0:
                    return args
                elif data_rest[0] != " ":
                    return False
                for rest in data_rest[1:].split(" "):
                    args.append(rest)
    return args


def send_message(con, message):
    bit = 0
    response = struct.pack('B', bit)
    con.sendall(response)
    message = message.encode()
    size = struct.pack('!I', len(message))
    con.sendall(size)
    con.sendall(message)
    con.close()


def send_audio(con, file_name, file_extension, start=None, end=None):
    song = AudioSegment.from_file(file_name)

    if start is not None:
        try:
            duration = song.duration_seconds * 1000
            if start != 'start':
                start = float(start) * 1000
            else:
                start = 0
            if end != 'end':
                end = float(end) * 1000
            else:
                end = duration
            if 0 <= start <= duration and 0 <= end <= duration:
                song = song[start:end]
            else:
                message = "Неправильный временной отрезок"
                send_message(con, message)
                return
        except:
            message = "Неправильный временной отрезок"
            send_message(con, message)
            return
    song = song.export(format=file_extension[1:]).read()
    bit = 1
    response = struct.pack('B', bit)
    con.sendall(response)
    size = struct.pack('!I', len(song))
    con.sendall(size)
    con.sendall(song)
    con.close()


def client_thread(con):
    try:
        size = con.recv(4)
        size = struct.unpack('!I', size)[0]
        received = 0
        actual_data = bytearray()
        while received < size:
            chunk = con.recv(min(4096, size - received))
            if not chunk:
                break
            actual_data.extend(chunk)
            received += len(chunk)
        data = actual_data.decode('utf-8')
        print(data, "sendme", data == "sendme")
        args = parse_input(data)
        if not args:
            message = "Неправильный формат запроса. Введите help для вывода всех команд"
            send_message(con, message)
        else:
            len_args = len(args)
            if args[0] == "sendme":
                if len_args > 1:
                    file_name = FILES_PATH + args[1]
                    if os.path.isfile(file_name):
                        _, file_extension = os.path.splitext(file_name)
                        try:
                            AudioSegment.from_file(file_name, file_extension[1:])
                        except:
                            message = "Формат файла не поддерживается"
                            send_message(con, message)
                        else:
                            if len_args > 2:
                                if args[2] == "part":
                                    if len_args == 5:
                                        aud_start = args[3]
                                        aud_end = args[4]
                                        send_audio(con, file_name, file_extension, start=aud_start, end=aud_end)
                                    else:
                                        message = "Неправильный формат запроса. Введите help для вывода всех команд"
                                        send_message(con, message)
                                elif args[2] == "full" and len_args == 3:
                                    send_audio(con, file_name, file_extension)
                                else:
                                    message = "Неправильный формат запроса. Введите help для вывода всех команд"
                                    send_message(con, message)
                            else:
                                send_audio(con, file_name, file_extension)
                    else:
                        message = f"Нет такого файла '{args[1]}'"
                        send_message(con, message)
                else:
                    message = "Неправильный формат запроса. Введите help для вывода всех команд"
                    send_message(con, message)
            elif args[0] == "listall" and len_args == 1:
                message = get_audio_list()
                send_message(con, message)
            elif args[0] == "help" and len_args == 1:
                message = ("\n"
                           "Список доступных команд:\n"
                           "help - вывести список доступных команд\n"
                           "listall - вывести список файлов на сервере\n"
                           "sendme 'file.ext' full - отправить файл целиком\n"
                           "sendme 'file.ext' part s end - отправить файл с секунды s до конца\n"
                           "sendme 'file.ext' part start s - отправить файл с начала до секунды s\n"
                           "sendme 'file.ext' part s1 s2 - отправить файл с секунды s1 до секунды s2")
                send_message(con, message)
            else:
                message = "Неправильный формат запроса. Введите help для вывода всех команд"
                send_message(con, message)
    except ConnectionResetError:
        print("Клиент отключился")


def run_server():
    if not os.path.isdir(FILES_PATH):
        os.mkdir(FILES_PATH)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hostname = socket.gethostname()
    server.bind((hostname, PORT))
    server.listen()
    print("Server running")
    # print(get_audio_list())
    while True:
        client, _ = server.accept()
        start_new_thread(client_thread, (client,))
