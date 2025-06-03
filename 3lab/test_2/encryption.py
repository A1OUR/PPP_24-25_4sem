import heapq
from collections import defaultdict
import base64
from typing import Dict, Tuple


class HuffmanNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(text: str) -> HuffmanNode:
    frequency = defaultdict(int)
    for char in text:
        frequency[char] += 1

    heap = []
    for char, freq in frequency.items():
        heapq.heappush(heap, HuffmanNode(char=char, freq=freq))

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, merged)

    return heapq.heappop(heap)


def build_huffman_codes(node: HuffmanNode, code="", codes=None) -> Dict[str, str]:
    if codes is None:
        codes = {}
    if node.char is not None:
        codes[node.char] = code
    else:
        build_huffman_codes(node.left, code + "0", codes)
        build_huffman_codes(node.right, code + "1", codes)
    return codes


def huffman_encode(text: str) -> Tuple[str, Dict[str, str], int]:
    if not text:
        return "", {}, 0

    root = build_huffman_tree(text)
    codes = build_huffman_codes(root)

    encoded_bits = ''.join([codes[char] for char in text])

    padding = (8 - len(encoded_bits) % 8) % 8
    encoded_bits += '0' * padding

    encoded_bytes = bytearray()
    for i in range(0, len(encoded_bits), 8):
        byte = encoded_bits[i:i + 8]
        encoded_bytes.append(int(byte, 2))

    encoded_str = base64.b64encode(encoded_bytes).decode('utf-8')
    return encoded_str, codes, padding


def huffman_decode(encoded_str: str, codes: Dict[str, str], padding: int) -> str:
    if not encoded_str:
        return ""

    encoded_bytes = base64.b64decode(encoded_str)
    encoded_bits = ''.join([f"{byte:08b}" for byte in encoded_bytes])

    if padding > 0:
        encoded_bits = encoded_bits[:-padding]

    reverse_codes = {v: k for k, v in codes.items()}

    current_code = ""
    decoded_text = []
    for bit in encoded_bits:
        current_code += bit
        if current_code in reverse_codes:
            decoded_text.append(reverse_codes[current_code])
            current_code = ""

    return ''.join(decoded_text)


def xor_encrypt(text: str, key: str) -> str:
    encrypted_bytes = []
    key_len = len(key)
    for i in range(len(text)):
        encrypted_bytes.append(ord(text[i]) ^ ord(key[i % key_len]))
    return base64.b64encode(bytes(encrypted_bytes)).decode('utf-8')


def xor_decrypt(encoded_text: str, key: str) -> str:
    encrypted_bytes = base64.b64decode(encoded_text)
    decrypted_chars = []
    key_len = len(key)
    for i in range(len(encrypted_bytes)):
        decrypted_chars.append(chr(encrypted_bytes[i] ^ ord(key[i % key_len])))
    return ''.join(decrypted_chars)