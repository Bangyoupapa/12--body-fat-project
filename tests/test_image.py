import pytest
from utils.image import normalise_image_url


@pytest.mark.asyncio
async def test_non_heic_url_is_returned_unchanged():
    url = "https://cdn.discordapp.com/attachments/123/food.jpg"
    result = await normalise_image_url(url)
    assert result == url


@pytest.mark.asyncio
async def test_heic_url_is_converted_to_jpeg_data_url():
    url = "https://cdn.discordapp.com/attachments/123/IMG_1234.HEIC"
    fake_bytes = b"fake-heic-data"

    async def fake_fetch(u):
        assert u == url
        return fake_bytes

    def fake_convert(data):
        assert data == fake_bytes
        return "data:image/jpeg;base64,abc123"

    result = await normalise_image_url(url, fetch_fn=fake_fetch, convert_fn=fake_convert)
    assert result == "data:image/jpeg;base64,abc123"
