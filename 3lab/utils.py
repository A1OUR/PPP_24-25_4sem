import heapq
from collections import defaultdict
import base64
from typing import Tuple, Dict
from bitarray import bitarray


def huffman_encode(text: str) -> Tuple[bytes, Dict[str, str], int]:
    # Считаем частоты символов
    frequency = defaultdict(int)
    for char in text:
        frequency[char] += 1

    # Строим дерево Хаффмана
    heap = [[weight, [symbol, ""]] for symbol, weight in frequency.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

    # Получаем коды
    huffman_codes = {}
    for pair in heap[0][1:]:
        huffman_codes[pair[0]] = pair[1]

    # Кодируем текст
    encoded_bits = bitarray()
    for char in text:
        encoded_bits.extend(bitarray(huffman_codes[char]))

    # Добавляем padding если нужно
    padding = 8 - len(encoded_bits) % 8
    if padding != 8:
        encoded_bits.extend([0] * padding)

    # Преобразуем в байты
    encoded_bytes = encoded_bits.tobytes()

    return encoded_bytes, huffman_codes, padding


def huffman_decode(encoded_bytes: bytes, huffman_codes: Dict[str, str], padding: int) -> str:
    # Создаем обратный словарь кодов
    reverse_codes = {v: k for k, v in huffman_codes.items()}

    # Преобразуем байты в биты
    bits = bitarray()
    bits.frombytes(encoded_bytes)

    # Удаляем padding
    if padding != 8:
        del bits[-padding:]

    # Декодируем
    current_code = ""
    decoded_text = []

    for bit in bits:
        current_code += '1' if bit else '0'
        if current_code in reverse_codes:
            decoded_text.append(reverse_codes[current_code])
            current_code = ""

    return ''.join(decoded_text)


def xor_encrypt(data: bytes, key: str) -> bytes:
    key_bytes = key.encode('utf-8')
    key_length = len(key_bytes)
    return bytes([data[i] ^ key_bytes[i % key_length] for i in range(len(data))])


def xor_decrypt(data: bytes, key: str) -> bytes:
    return xor_encrypt(data, key)  # XOR обратим