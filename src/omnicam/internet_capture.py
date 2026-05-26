from typing import Union

from .base_camera import CameraInfo, BaseCamera
from .cv_camera_base import CVCameraBase


class InternetCapture(CVCameraBase):
    def __init__(self, url: str, timeout=5, open=True, info: Union[CameraInfo, BaseCamera] = None, args: list = None,
                 open_error=None, timeout_error=None):
        if not url.startswith("http://") and not url.startswith("https://") and not url.startswith("rtsp://"):
            url = "http://" + url
        domain = url.split("//")[1].split("/")[0]
        if ":" not in domain:
            url = url.replace(domain, domain + ":8080")
        if "/" not in url.split("//")[1]:
            url += "/video"
        super().__init__(
            [url, *(args or [])], timeout=timeout, open=open, info=info,
            open_error=open_error or ValueError(f"Could not open video stream from URL {url}"),
            timeout_error=timeout_error or TimeoutError(
                f"Could not open video stream from URL {url} within {timeout} seconds")
        )
