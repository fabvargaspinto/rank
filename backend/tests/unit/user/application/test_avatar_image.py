import struct
import zlib
from io import BytesIO

import pytest
from PIL import Image

from core.user.application.application_error import InvalidAvatarFileError
from core.user.application.avatar_image import MAX_AVATAR_PIXELS, recode_avatar

MAX_BYTES = 2 * 1024 * 1024


def _png_header(width: int, height: int) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        checksum = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", checksum)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IEND", b"")


def _png(width: int, height: int) -> bytes:
    output = BytesIO()
    Image.new("RGB", (width, height), "red").save(output, format="PNG")
    return output.getvalue()


def test_rejects_dimensions_over_the_pixel_limit_before_decoding():
    content = _png_header(4097, 4097)

    assert len(content) < 100
    assert 4097 * 4097 > MAX_AVATAR_PIXELS
    with pytest.raises(InvalidAvatarFileError, match="demasiado grande"):
        recode_avatar(content, MAX_BYTES)


def test_pixel_limit_allows_a_4096_square_header():
    content = _png_header(4096, 4096)

    with pytest.raises(InvalidAvatarFileError, match="inválida"):
        recode_avatar(content, MAX_BYTES)


def test_maps_a_decompression_bomb_to_an_invalid_file(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 1)

    with pytest.raises(InvalidAvatarFileError, match="inválida"):
        recode_avatar(_png(8, 8), MAX_BYTES)


def test_still_recodes_a_normal_png():
    encoded = recode_avatar(_png(32, 32), MAX_BYTES)

    assert encoded.startswith(b"RIFF")
