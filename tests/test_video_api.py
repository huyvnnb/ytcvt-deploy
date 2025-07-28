import requests
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

video_urls = [
    "https://www.youtube.com/watch?v=KH9vHrj475k",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=9bZkp7q19f0",  # Gangnam Style
    "https://www.youtube.com/watch?v=3JZ_D3ELwOQ",  # See You Again
]


def test_get_video_info_multiple_urls():
    for url in video_urls:
        response = requests.get("http://localhost:8000/tools/youtube/video-info", params={"url": url})
        assert response.status_code == 200
        json_data = response.json()
        assert json_data["success"] is True
        assert "title" in json_data["data"]
        assert "thumbnail" in json_data["data"]
        assert isinstance(json_data["data"]["resolutions"], list)
        assert len(json_data["data"]["resolutions"]) > 0


def test_get_video_info_invalid_url():
    url = "https://www.youtube.com/watch?v=invalid1234"
    response = requests.get("http://localhost:8000/tools/youtube/video-info", params={"url": url})
    assert response.status_code in (400, 404, 500)
    json_data = response.json()
    assert json_data["success"] is False


def test_get_video_info_missing_url():
    response = requests.get("http://localhost:8000/tools/youtube/video-info")
    assert response.status_code == 422 or response.status_code == 400


def test_get_video_info_structure():
    url = "https://www.youtube.com/watch?v=KH9vHrj475k"
    response = requests.get("http://localhost:8000/tools/youtube/video-info", params={"url": url})
    data = response.json()["data"]
    assert "title" in data
    assert "thumbnail" in data
    assert "duration" in data
    assert "resolutions" in data
    for item in data["resolutions"]:
        assert "id" in item
        assert "resolution" in item
        assert "size" in item
