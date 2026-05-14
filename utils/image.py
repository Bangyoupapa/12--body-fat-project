import base64
import io
from typing import Callable, Optional


async def _default_fetch(url: str) -> bytes:
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.read()


def _default_convert(data: bytes) -> str:
    import pillow_heif
    from PIL import Image
    pillow_heif.register_heif_opener()
    img = Image.open(io.BytesIO(data))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/jpeg;base64,{b64}"


def _is_heic(url: str) -> bool:
    return url.lower().split("?")[0].endswith(".heic")


async def normalise_image_url(
    url: str,
    fetch_fn: Optional[Callable] = None,
    convert_fn: Optional[Callable] = None,
) -> str:
    if not _is_heic(url):
        return url
    fetch = fetch_fn or _default_fetch
    convert = convert_fn or _default_convert
    data = await fetch(url)
    return convert(data)
