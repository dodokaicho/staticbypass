"""VBA compression per MS-OVBA specification (section 2.4.1).

Provides compress/decompress with roundtrip verification.
"""

import struct


# ---------------------------------------------------------------------------
# VBA compression (MS-OVBA 2.4.1)
# ---------------------------------------------------------------------------

def _offset_bits(pos: int) -> int:
    """Calculate the number of bits for the CopyToken offset field."""
    if pos <= 1:
        return 4
    return max(4, (pos - 1).bit_length())


def _compress_chunk(data: bytes) -> bytearray:
    """Compress a single VBA chunk (up to 4096 bytes)."""
    out = bytearray()
    pos = 0

    while pos < len(data):
        flag_pos = len(out)
        out.append(0)
        flag = 0

        for bit in range(8):
            if pos >= len(data):
                break

            ob = _offset_bits(pos)
            lb = 16 - ob
            max_match = (1 << lb) + 2
            max_off = min(pos, 1 << ob)

            best_len, best_off = 0, 0
            for off in range(1, max_off + 1):
                length = 0
                while length < max_match and pos + length < len(data):
                    src = pos - off + (length % off if length >= off else length)
                    if data[src] != data[pos + length]:
                        break
                    length += 1
                if length >= 3 and length > best_len:
                    best_len = length
                    best_off = off
                    if length == max_match:
                        break

            if best_len >= 3:
                flag |= 1 << bit
                token = ((best_off - 1) << lb) | (best_len - 3)
                out += struct.pack('<H', token)
                pos += best_len
            else:
                out.append(data[pos])
                pos += 1

        out[flag_pos] = flag

    return out


def _vba_decompress(data: bytes) -> bytes:
    """Decompress VBA compressed data per MS-OVBA 2.4.1."""
    if not data or data[0] != 0x01:
        raise ValueError('Invalid VBA compressed signature')

    out = bytearray()
    pos = 1

    while pos < len(data):
        if pos + 2 > len(data):
            break
        header = struct.unpack_from('<H', data, pos)[0]
        pos += 2
        chunk_size = (header & 0x0FFF) + 1
        compressed = (header >> 15) & 1

        if not compressed:
            out += data[pos:pos + 4096]
            pos += chunk_size
        else:
            chunk_end = pos + chunk_size
            chunk_start_out = len(out)
            while pos < chunk_end:
                if pos >= len(data):
                    break
                flag_byte = data[pos]
                pos += 1
                for bit in range(8):
                    if pos >= chunk_end:
                        break
                    if flag_byte & (1 << bit):
                        if pos + 2 > len(data):
                            break
                        token = struct.unpack_from('<H', data, pos)[0]
                        pos += 2
                        ob = _offset_bits(len(out) - chunk_start_out)
                        lb = 16 - ob
                        length = (token & ((1 << lb) - 1)) + 3
                        offset = (token >> lb) + 1
                        for _ in range(length):
                            out.append(out[-offset])
                    else:
                        out.append(data[pos])
                        pos += 1

    return bytes(out)


def _vba_compress(data: bytes) -> bytes:
    """Compress data per MS-OVBA 2.4.1."""
    if not data:
        return b'\x01'

    result = bytearray(b'\x01')  # signature

    for i in range(0, len(data), 4096):
        chunk = data[i:i + 4096]
        compressed = _compress_chunk(chunk)

        if len(compressed) <= 4096:
            header = (len(compressed) - 1) | 0xB000  # sig=011, flag=1(compressed)
            result += struct.pack('<H', header)
            result += compressed
        else:
            result += struct.pack('<H', 0x3FFF)  # sig=011, flag=0(uncompressed)
            result += chunk.ljust(4096, b'\x00')

    return bytes(result)


def _vba_compress_verified(data: bytes) -> bytes:
    """Compress and verify roundtrip integrity."""
    compressed = _vba_compress(data)
    decompressed = _vba_decompress(compressed)
    decompressed_stripped = decompressed.rstrip(b'\x00')
    data_stripped = data.rstrip(b'\x00')
    if decompressed_stripped != data_stripped:
        mismatch = _find_mismatch(data, decompressed)
        raise RuntimeError(
            f'VBA compression roundtrip failed: '
            f'{len(data)} bytes in, {len(decompressed)} bytes out, '
            f'first mismatch at byte {mismatch}'
        )
    return compressed


def _find_mismatch(a: bytes, b: bytes) -> int:
    for i in range(min(len(a), len(b))):
        if a[i] != b[i]:
            return i
    return min(len(a), len(b))