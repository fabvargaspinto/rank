from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

from core.user.application.application_error import InvalidAvatarFileError

MAX_AVATAR_EDGE = 512
WEBP_QUALITY = 80
_ALLOWED_FORMATS = frozenset({"JPEG", "PNG", "WEBP"})


def recode_avatar(content: bytes, max_bytes: int) -> bytes:
    if not content:
        raise InvalidAvatarFileError("La imagen es inválida")
    if len(content) > max_bytes:
        raise InvalidAvatarFileError("La imagen no puede superar 2 MB")

    try:
        with Image.open(BytesIO(content)) as opened:
            if opened.format not in _ALLOWED_FORMATS:
                raise InvalidAvatarFileError(
                    "La imagen debe ser JPEG, PNG o WebP"
                )
            image: Image.Image = ImageOps.exif_transpose(opened) or opened
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
            image.thumbnail(
                (MAX_AVATAR_EDGE, MAX_AVATAR_EDGE),
                Image.Resampling.LANCZOS,
            )
            output = BytesIO()
            image.save(output, format="WEBP", quality=WEBP_QUALITY)
    except InvalidAvatarFileError:
        raise
    except (UnidentifiedImageError, OSError) as exc:
        raise InvalidAvatarFileError("La imagen es inválida") from exc

    encoded = output.getvalue()
    if len(encoded) > max_bytes:
        raise InvalidAvatarFileError("La imagen no puede superar 2 MB")
    return encoded
