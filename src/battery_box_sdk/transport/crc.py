"""CRC-16 Modbus calculation."""


def crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def append_crc(data: bytes) -> bytes:
    crc = crc16_modbus(data)
    return data + bytes([crc & 0xFF, (crc >> 8) & 0xFF])


def verify_crc(packet: bytes) -> bool:
    if len(packet) < 3:
        return False
    payload, expected_lo, expected_hi = packet[:-2], packet[-2], packet[-1]
    crc = crc16_modbus(payload)
    return (crc & 0xFF) == expected_lo and ((crc >> 8) & 0xFF) == expected_hi
