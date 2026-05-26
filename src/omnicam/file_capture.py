import os
from typing import Union

from . import BaseCamera
from .base_camera import CameraInfo
from .cv_camera_base import CVCameraBase


class FileCapture(CVCameraBase):
    def __init__(self, path: "os.PathLike | str", open=True, info: Union[CameraInfo, BaseCamera] = None, open_error=None):
        if not os.path.exists(path):
            raise ValueError(f"File {path} does not exist")
        super().__init__([str(path)], open=open, info=info,
                         open_error=open_error or ValueError(f"Could not open video file {path}"))
