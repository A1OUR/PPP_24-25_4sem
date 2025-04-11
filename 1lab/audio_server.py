from _thread import start_new_thread
from common_stuff import *

def update_metadata():
    metadata = {}
    
    for filename in os.listdir(FILES_PATH):
        filepath = os.path.join(FILES_PATH, filename)
        if os.path.isfile(filepath):
            try:
                info = mediainfo(filepath)
                metadata[filename] = {
                    'format': info.get('format_name', 'unknown'),
                    'duration': float(info.get('duration', 0)),
                    'size': os.path.getsize(filepath)
                }
            except Exception as e:
                
                print(f"Error processing {filename}: {e}")
    
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)
    
    # logging.info("Audio metadata updated")
    
def get_audio_list():
    update_metadata()
    with open(METADATA_FILE, 'r') as f:
        return json.load(f)

def parse_input(data):
    args = []
    data = data.replace('"',"'")
    if not " " in data:
        args.append(data)
    else:
        first_space = data.find(" ")
        args.append(data[:first_space])
        data_rest = data[first_space+1:]
        if data.count("'") < 2:
            return False
        else:
            if data_rest[0] != "'":
                return False
            else:
                args.append(data_rest[1:data_rest.rfind("'")])
                data_rest = data_rest[data_rest.rfind("'")+1:]
                if len(data_rest)==0:
                    return args
                elif data_rest[0] != " ":
                    return False
                for rest in data_rest[1:].split(" "):
                    args.append(rest)
    return args

def send_message(con,message):
    bit = 0
    response = struct.pack('B', bit)
    con.sendall(response)
    message = message.encode()
    size = struct.pack('!I', len(message))
    con.sendall(size)
    con.sendall(message)
    con.close()
    
def send_audio(con,file_name,file_extension,start=None,end=None):
    bit = 1
    response = struct.pack('B', bit)
    con.sendall(response)
    song = AudioSegment.from_file(file_name).export(format=file_extension[1:]).read()
    size = struct.pack('!I', len(song))
    con.sendall(size)
    con.sendall(song) 
    con.close()

def client_thread (con):
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
        print(data, "sendme", data=="sendme")
        args = parse_input(data)
        if args == False:
            message = "Неправильный формат запроса. Введите help для вывода всех команд"
            send_message(con,message)
        else:
            len_args=len(args)
            if args[0] == "sendme":
                if len_args>1:
                    file_name = FILES_PATH+args[1]
                    if os.path.isfile(file_name):
                        _, file_extension = os.path.splitext(file_name)
                        try:
                            AudioSegment.from_file(file_name, file_extension[1:])
                        except:
                            message = "Формат файла не поддерживается"
                            send_message(con,message)
                        else:
                            if len_args>2:
                                if args[2] == "part":
                                    message = "Функция пока не поддерживается"
                                    send_message(con,message)
                                elif args[2] == "full" and len_args == 3:
                                    aud_start = "start"
                                    aud_end = "end"
                                    send_audio(con, file_name, file_extension)
                                else:
                                    message = "Неправильный формат запроса. Введите help для вывода всех команд"
                                    send_message(con,message)
                            else:
                                send_audio(con,file_name)
                    else:
                        message = "Нет такого файла"
                        send_message(con,message)
                else:
                    message = "Неправильный формат запроса. Введите help для вывода всех команд"
                    send_message(con,message)
            elif args[0] == "listall" and len_args==1:
                message = json.dumps(get_audio_list(), ensure_ascii=False)
                send_message(con,message)
            else:
                message = "Неправильный формат запроса. Введите help для вывода всех команд"
                send_message(con,message)
    except ConnectionResetError:
        print("Клиент отключился")

def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hostname = socket.gethostname()
    server.bind((hostname, PORT))
    server.listen()
    print("Server running")
    while True:
        client, _ = server.accept()
        start_new_thread(client_thread, (client, ))