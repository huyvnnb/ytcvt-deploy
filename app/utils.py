import asyncio
import functools
from typing import Callable, Any
from urllib.parse import urlparse


async def run_in_threadpool(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    loop = asyncio.get_running_loop()
    pfunc = functools.partial(func, *args, **kwargs)
    return await loop.run_in_executor(None, pfunc)


def is_youtube_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        return domain in ["www.youtube.com", "youtube.com", "youtu.be"]
    except Exception:
        return False

class Tools:
    GET_VIDEO_INFO_SUCCESS = "Get video information successfully."
    DOWNLOAD_MP3_SUCCESS = "Download mp3 successfully."
