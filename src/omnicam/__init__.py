from importlib.metadata import PackageNotFoundError, version

from .base_camera import BaseCamera, CameraInfo
from .cv_camera_base import CVCameraBase
from .file_capture import FileCapture
from .gazebo_camera import GazeboCamera
from .gstreamer_capture import GStreamerCapture
from .internet_capture import InternetCapture
from .pi_camera import PiCamera
from .readonly_camera import ReadonlyCamera
from .screen_capture import ScreenCapture
from .simple_camera import SimpleCamera

try:
    __version__ = version("omnicam")
except PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = [
    "BaseCamera",
    "CameraInfo",
    "CVCameraBase",
    "FileCapture",
    "GazeboCamera",
    "GStreamerCapture",
    "InternetCapture",
    "PiCamera",
    "ReadonlyCamera",
    "ScreenCapture",
    "SimpleCamera",
    "__version__",
]
