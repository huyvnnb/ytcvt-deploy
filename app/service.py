import asyncio
import io
import subprocess
from typing import List

import yt_dlp
from fastapi import HTTPException
import validators
from yt_dlp import DownloadError

from app.exception import VideoNotFoundError, ConversionError, SetupError
from app.schema import VideoResponse, Resolution
from app.utils import run_in_threadpool, is_youtube_url


class YoutubeService:

    @staticmethod
    def _format_url(url: str) -> str:
        index = url.find("&list")
        return url[:index] if index != -1 else url

    def _get_video_info_sync(self, url: str):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except DownloadError as e:
            raise VideoNotFoundError("Video not found or access is denied.")
        except Exception as e:
            raise ConversionError("An unexpected error occurred with the video library.")

    async def get_video_info(self, url: str) -> VideoResponse:
        if not is_youtube_url(url):
            raise VideoNotFoundError("Invalid URL format.")
        formatted_url = self._format_url(url)
        video_info = await run_in_threadpool(self._get_video_info_sync, formatted_url)

        resolutions: List[Resolution] = []
        for f in video_info.get('formats', []):
            if f.get('vcodec') != 'none' and f.get('ext') == 'mp4':
                filesize_mb = f.get('filesize') or f.get('filesize_approx')
                if filesize_mb:
                    filesize_mb = round(filesize_mb / 1024 / 1024, 2)
                    resolution = Resolution(
                        id=f.get('format_id'),
                        resolution=f.get('resolution', 'audio-only'),
                        size=filesize_mb
                    )
                    resolutions.append(resolution)

        return VideoResponse(
            title=video_info.get('title'),
            thumbnail=video_info.get('thumbnail'),
            duration=video_info.get('duration_string'),
            resolutions=resolutions
        )


    def _convert_mp3_sync(self, url: str):
        # ffmpeg_location = r"D:\ffmpeg\bin"
        # user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        #               "Chrome/120.0.0.0 Safari/537.36")
        command = [
            "yt-dlp",
            "--ignore-config",
            # "--user-agent", user_agent,
            # "--ffmpeg-location", ffmpeg_location,
            "--limit-rate", "5M",
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "192K",
            self._format_url(url),
            "-o", "-"
        ]
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            stdout, stderr = process.communicate(timeout=300)

            if process.returncode != 0:
                error_message = stderr.decode('utf-8', errors='ignore')
                print(f"ERROR from yt-dlp (return code {process.returncode}): {error_message}")
                raise Exception(f"yt-dlp failed: {error_message}")

            return stdout
        except FileNotFoundError:
            raise SetupError("Server is not configured correctly to process videos.")
        except subprocess.TimeoutExpired:
            process.kill()
            raise ConversionError("The video conversion process took too long and was terminated.")
        except Exception as e:
            raise ConversionError("An unexpected error occurred during video conversion.")

    async def get_mp3_stream_buffer(self, url: str) -> io.BytesIO:
        if not is_youtube_url(url):
            raise VideoNotFoundError("Invalid URL format.")
        mp3_bytes = await run_in_threadpool(self._convert_mp3_sync, url)
        return io.BytesIO(mp3_bytes)

    # async def stream_audio_mp3(self, url: str):
    #     if not is_youtube_url(url):
    #         raise VideoNotFoundError("Invalid URL format.")
    #     formatted_url = self._format_url(url)
    #     command = [
    #         "yt-dlp",
    #         "-f", "bestaudio/best",
    #         "--extract-audio",
    #         "--audio-format", "mp3",
    #         "--audio-quality", "192K",
    #         formatted_url,
    #         "-o", "-"
    #     ]
    #
    #     process = await asyncio.create_subprocess_exec(
    #         *command,
    #         stdout=asyncio.subprocess.PIPE,
    #         stderr=asyncio.subprocess.PIPE
    #     )
    #
    #     while True:
    #         chunk = await process.stdout.read(8192)
    #         if not chunk:
    #             break
    #         yield chunk
    #
    #     await process.wait()
    #     if process.returncode != 0:
    #         error = await process.stderr.read()
    #         raise Exception(f"Failed to process and stream MP3. Error: {error.decode()}")


def get_youtube_service():
    return YoutubeService()