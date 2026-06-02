from abc import abstractmethod, ABC
from collections.abc import Callable
from math import radians
from typing import Sequence, Optional

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


def calc_focal_length_mm(focal_length_px: "tuple[float, float] | float", pixel_size_um: float = 1.0) -> tuple[
    float, float]:
    if isinstance(focal_length_px, float):
        focal_length_px = (focal_length_px, focal_length_px)
    pixel_size_mm = pixel_size_um / 1000.0
    return focal_length_px[0] * pixel_size_mm, focal_length_px[1] * pixel_size_mm


def calc_focal_length_px(focal_length_mm: "tuple[float, float] | float", pixel_size_um: float = 1.0) -> tuple[
    float, float]:
    if isinstance(focal_length_mm, float):
        focal_length_mm = (focal_length_mm, focal_length_mm)
    pixel_size_mm = pixel_size_um / 1000.0
    return focal_length_mm[0] / pixel_size_mm, focal_length_mm[1] / pixel_size_mm


class CameraInfo:
    def __init__(
            self,
            name: str,
            short_name: str,
            aperture_f: float,
            focal_length_px: tuple[float, float],
            resolutions: "Sequence[tuple[int, int]] | tuple[range, range] | Callable[[tuple[int, int]] | bool]",
            update_rate: "float | Callable[[BaseCamera], float]",
            pixel_size_um: float = 1.0,
            hfov_deg: float = 90.0,
            focus_type: str = "Unknown",  # Literal["Fixed", "Autofocus", "Manual", "Unknown"]
            has_ir_filter: bool = False,
            max_resolution: Optional[tuple[int, int]] = None
    ):
        self.name = name
        self.short_name = short_name
        self.aperture_f = aperture_f
        self._resolutions = resolutions
        self._update_rate = update_rate
        self.pixel_size_um = pixel_size_um
        self.hfov_deg = hfov_deg
        self.focus_type = focus_type
        self.has_ir_filter = has_ir_filter
        self.base_focal_length_px = focal_length_px
        self.focal_length_mm = calc_focal_length_mm(focal_length_px, pixel_size_um)
        if max_resolution is not None:
            self.max_resolution = max_resolution
            if not resolutions:
                resolutions = [range(1, max_resolution[0] + 1), range(1, max_resolution[1] + 1)]
                self._resolutions = resolutions
        elif isinstance(resolutions, Callable):
            raise ValueError("max_resolution must be provided when using a Callable for resolutions")
        elif len(resolutions) > 0 and isinstance(resolutions[0], range):
            self.max_resolution = (resolutions[0][-1], resolutions[1][-1])
        else:
            self.max_resolution = max(resolutions, key=lambda r: r[0] * r[1], default=(0, 0))
        self._max_resolution = max_resolution

    def is_valid_resolution(self, resolution: tuple[int, int]) -> bool:
        if isinstance(self._resolutions, Callable):
            return self._resolutions(resolution)
        if isinstance(self._resolutions[0], range):
            x_range, y_range = self._resolutions[0], self._resolutions[1]
            return (x_range.start <= resolution[0] < x_range.stop and
                    y_range.start <= resolution[1] < y_range.stop)
        return resolution in self._resolutions

    def focal_length(self, resolution: tuple[int, int]):
        return (
            self.base_focal_length_px[0] * resolution[0] / self.max_resolution[0],
            self.base_focal_length_px[1] * resolution[1] / self.max_resolution[1]
        )

    def update_rate(self, camera: "BaseCamera | None" = None) -> float:
        if isinstance(self._update_rate, Callable):
            if camera is None:
                raise ValueError("Camera instance must be provided to calculate update rate")
            return self._update_rate(camera)
        return self._update_rate


class BaseCamera(ABC):
    def __init__(self, info: "CameraInfo | BaseCamera | None" = None, open=True):
        self.closed = True
        self.roll_deg = 0.0
        self.pitch_deg = 0.0
        self.yaw_deg = 0.0
        self.offset = np.array([0.0, 0.0, -0.1], dtype=np.float64)
        if isinstance(info, CameraInfo):
            self.info: "CameraInfo | None" = info
        elif isinstance(info, BaseCamera):
            self.info: "CameraInfo | None" = info.info
        else:
            self.info: "CameraInfo | None" = None

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
    def _size(self) -> tuple[int, int]:
        raise NotImplementedError("size method must be implemented by subclass")

    def _focus(self, rectangle: tuple[int, int, int, int]):
        raise NotImplementedError("focus method must be implemented by subclass")

    def _focal_length(self):
        if self.info is None:
            raise ValueError("Camera info is not set, cannot determine focal length.")
        return self.info.focal_length(self.size)

    def open(self):
        if self.closed:
            raise PermissionError("Attempted to open a closed camera.")
        self._open()
        return self

    @property
    def size(self):
        return self._size()

    def focus(self, rectangle: tuple[int, int, int, int]):
        if self.closed:
            raise PermissionError("Attempted to focus a closed camera.")
        if self.info is not None and self.info.focus_type in ("Fixed", "Unknown"):
            raise ValueError(f"This camera has a {self.info.focus_type} focus and cannot be adjusted.")
        self._focus(rectangle)
        return self

    @property
    def focal_length(self) -> tuple[float, float]:
        return self._focal_length()

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def aspect_ratio(self):
        w, h = self.size
        return w / h if h != 0 else 0.0

    @property
    def fx(self):
        return self.focal_length[0]

    @property
    def fy(self):
        return self.focal_length[1]

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
            self.release()
        return frame

    def release(self):
        if not self.closed:
            self.closed = True
            self._release()

    def frames(self):
        while (frame := self.read()) is not None:
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
