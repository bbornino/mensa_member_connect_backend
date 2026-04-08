import io
from PIL import Image, ImageOps


def compress_profile_photo_bytes(
    image_bytes: bytes,
    max_size: tuple[int, int] = (1024, 1024),
    quality: int = 78,
) -> bytes:
    """
    Compress user profile photos into a normalized JPEG.
    - Resizes to fit within max_size while preserving aspect ratio
    - Corrects EXIF orientation
    - Flattens transparency onto white background
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = ImageOps.exif_transpose(img)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Normalize to RGB JPEG output.
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            alpha = img.split()[-1]
            background.paste(img, mask=alpha)
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        output = io.BytesIO()
        img.save(output, format="JPEG", quality=quality, optimize=True, progressive=True)
        return output.getvalue()
