from abc import abstractmethod, ABC
from math import radians
from typing import Literal, Tuple, Union

import numpy as np

resolutions = {
    "240p": (426, 240),
    "360p": (640, 360),
    "480p": (854, 480),
    "720p": (1280, 720),
    "HD": (1280, 720),
    "1080p": (1920, 1080),
    "HD+": (1920, 1080),
    "1440p": (2560, 1440),
    "2160p": (3840, 2160)
}


class CameraInfo:
    def __init__(
            self,
            name: str,
            short_name: str,
            focal_length_mm: Tuple[float, float],
            pixel_size_um: float,
            max_resolution: Tuple[int, int],
            aperture_f: float,
            hfov_deg: float,
            focus_type: Literal["Fixed", "Autofocus", "Manual", "Unknown"],
            has_ir_filter: bool
    ):
        self.name = name
        self.short_name = short_name
        self.focal_length_mm = focal_length_mm
        self.pixel_size_um = pixel_size_um
        self.max_resolution = max_resolution
        self.aperture_f = aperture_f
        self.hfov_deg = hfov_deg
        self.focus_type = focus_type
        self.has_ir_filter = has_ir_filter

        pixel_size_mm = self.pixel_size_um / 1000.0
        self.base_focal_length = (self.focal_length_mm[0] / pixel_size_mm, self.focal_length_mm[1] / pixel_size_mm)

    def focal_length(self, resolution: Tuple[int, int]):
        return (
            self.base_focal_length[0] * resolution[0] / self.max_resolution[0],
            self.base_focal_length[1] * resolution[1] / self.max_resolution[1]
        )

    @staticmethod
    def from_focal_length(name: str, short_name: str, focal_length: Tuple[float, float],
                          resolution: Tuple[int, int] = (9999, 9999)):
        pixel_size_mm = 0.001
        focal_length_mm = (focal_length[0] * pixel_size_mm, focal_length[1] * pixel_size_mm)
        return CameraInfo(
            name=name,
            short_name=short_name,
            focal_length_mm=focal_length_mm,
            pixel_size_um=pixel_size_mm * 1000,
            max_resolution=resolution,
            aperture_f=0.0,
            hfov_deg=0.0,
            focus_type="Unknown",
            has_ir_filter=False
        )


class BaseCamera(ABC):
    def __init__(self, info: Union[CameraInfo, "BaseCamera"] = None, open=True):
        self.closed = False
        self.roll_deg = 0.0
        self.pitch_deg = 0.0
        self.yaw_deg = 0.0
        self.offset = np.array([0.0, 0.0, -0.1], dtype=np.float64)
        if isinstance(info, BaseCamera):
            self.info: CameraInfo = info.info
        elif isinstance(info, CameraInfo):
            self.info: CameraInfo = info

        if open:
            self.open()

    @abstractmethod
    def _open(self):
        raise NotImplementedError("open method must be implemented by subclass")

    @abstractmethod
    def _read(self) -> "np.ndarray | None":
        raise NotImplementedError("read method must be implemented by subclass")

    @abstractmethod
    def _release(self):
        raise NotImplementedError("release method must be implemented by subclass")

    @abstractmethod
    def _size(self) -> Tuple[int, int]:
        raise NotImplementedError("size method must be implemented by subclass")

    def _focus(self, rectangle: Tuple[int, int, int, int]):
        raise NotImplementedError("focus method must be implemented by subclass")

    def open(self):
        if self.closed:
            raise PermissionError("Attempted to open a closed camera.")
        self._open()
        return self

    def size(self):
        return self._size()

    def focus(self, rectangle: Tuple[int, int, int, int]):
        if self.closed:
            raise PermissionError("Attempted to focus a closed camera.")
        if self.info is not None and self.info.focus_type in ("Fixed", "Unknown"):
            raise ValueError(f"This camera has a {self.info.focus_type} focus and cannot be adjusted.")
        self._focus(rectangle)
        return self

    def focal_length(self) -> Tuple[float, float]:
        if self.info is None:
            raise ValueError("CameraInfo must be provided to calculate focal length")
        return self.info.focal_length(self.size())

    @property
    def width(self):
        return self.size()[0]

    @property
    def height(self):
        return self.size()[1]

    @property
    def aspect_ratio(self):
        w, h = self.size()
        return w / h if h != 0 else 0.0

    @property
    def fx(self):
        return self.focal_length()[0]

    @property
    def fy(self):
        return self.focal_length()[1]

    @property
    def cx(self):
        return self.width / 2.0

    @property
    def cy(self):
        return self.height / 2.0

    @property
    def horizontal_fov(self):
        return radians(self.info.hfov_deg) if self.info is not None else 0.0

    def read(self):
        if self.closed:
            raise PermissionError("Attempted to read from a closed camera.")
        frame = self._read()
        if frame is None:
            self.closed = True
        return frame

    def release(self):
        if not self.closed:
            self.closed = True
            self._release()

    def frames(self):
        while True:
            frame = self.read()
            if frame is None:
                break
            yield frame

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def readonly(self):
        from .readonly_camera import ReadonlyCamera
        if isinstance(self, ReadonlyCamera):
            return self
        return ReadonlyCamera(self)
