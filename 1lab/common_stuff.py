import struct
import math
import socket
import os
import json
from pydub import AudioSegment
from pydub.utils import mediainfo


PORT = 55234
MSG_SIZE = 16
DATA_SIZE = MSG_SIZE - struct.calcsize('II')
DATA_TEMPLATE = f'II{DATA_SIZE}s'
FILES_PATH = os.getcwd()+"\\audio_files\\"
METADATA_FILE = "audio_metadata.json"