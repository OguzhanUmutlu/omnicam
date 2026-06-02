from abc import abstractmethod, ABC
from collections.abc import Callable
from math import radians, cos, sin, sqrt, atan
from typing import Sequence, Optional

import numpy as np

resolutions = {
    # 16:9 (widescreen)
    "240p": (426, 240),
    "360p": (640, 360),
    "480p": (854, 480),
    "720p": (1280, 720),
    "HD": (1280, 720),
    "1080p": (1920, 1080),
    "HD+": (1920, 1080),
    "1440p": (2560, 1440),
    "2160p": (3840, 2160),

    # 4:3 (standard / photography)
    "VGA": (640, 480),
    "SVGA": (800, 600),
    "XGA": (1024, 768),
    "SXGA": (1280, 1024),
    "UXGA": (1600, 1200),
    "QXGA": (2048, 1536),

    # 1:1 (square)
    "SQ_480": (480, 480),
    "SQ_720": (720, 720),
    "SQ_1080": (1080, 1080),

    # 21:9 (ultrawide)
    "UW_1080": (2520, 1080),
    "UW_1440": (3360, 1440)
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


def _rot_matrix(roll, pitch, yaw):
    cr, sr = cos(roll), sin(roll)
    cp, sp = cos(pitch), sin(pitch)
    cy, sy = cos(yaw), sin(yaw)

    return np.array([
        [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
        [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
        [-sp, cp * sr, cp * cr]
    ], dtype=np.float64)


class CameraInfo:
    def __init__(
            self,
            name: str,
            short_name: str,
            focal_length_px: tuple[float, float],
            update_rate: "float | Callable[[BaseCamera], float]",
            aperture_f: float = 2.8,
            resolutions: "Sequence[tuple[int, int]] | tuple[range, range] | Callable[[tuple[int, int]] | bool]" = None,
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
        elif resolutions and isinstance(resolutions[0], range):
            self.max_resolution = (resolutions[0][-1], resolutions[1][-1])
        else:
            if not resolutions:
                raise ValueError("max_resolution must be provided when resolutions is empty or None")
            self.max_resolution = max(resolutions, key=lambda r: r[0] * r[1], default=(0, 0))
        self._max_resolution = max_resolution

    def is_valid_resolution(self, resolution: tuple[int, int]) -> bool:
        if self._resolutions is None:
            return True
        if isinstance(self._resolutions, Callable):
            return self._resolutions(resolution)
        if isinstance(self._resolutions[0], range):
            x_range, y_range = self._resolutions[0], self._resolutions[1]
            return (x_range.start <= resolution[0] < x_range.stop and
                    y_range.start <= resolution[1] < y_range.stop)
        return resolution in self._resolutions

    def focal_length(self, resolution: tuple[int, int]):
        scale = max(resolution[0] / self.max_resolution[0], resolution[1] / self.max_resolution[1])
        return (
            self.base_focal_length_px[0] * scale,
            self.base_focal_length_px[1] * scale
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
        self.offset = np.array([0.0, 0.0, 0.0], dtype=np.float64)  # x right, y down, z forward (optical)
        self.offset_roll = 0.0
        self.offset_pitch = 0.0
        self.offset_yaw = 0.0
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
        if not self.closed:
            raise PermissionError("Attempted to open an already open camera.")
        self.closed = False
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
    def update_rate(self):
        if self.info is None:
            raise ValueError("Camera info is not set, cannot determine update rate.")
        return self.info.update_rate(self)

    @property
    def horizontal_fov(self):
        if self.fx == 0:
            return 0.0
        return 2.0 * atan(self.width / (2.0 * self.fx))

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

    def project_pixel_to_ground(self, px, py, alt_m, roll, pitch, yaw):
        width, height = self.size
        fx, fy = self.focal_length

        x_cam = (px - (width / 2.0)) / fx
        y_cam = (py - (height / 2.0)) / fy
        z_cam = 1.0

        norm = sqrt(x_cam ** 2 + y_cam ** 2 + z_cam ** 2)
        ray_cam = np.array([x_cam / norm, y_cam / norm, z_cam / norm])

        ray_sensor = np.array([-ray_cam[1], ray_cam[0], ray_cam[2]])

        cam_roll = radians(self.offset_roll)
        cam_pitch = radians(self.offset_pitch)
        cam_yaw = radians(self.offset_yaw)

        cam_mount_body = _rot_matrix(cam_roll, cam_pitch, cam_yaw)
        body_to_ned = _rot_matrix(roll, pitch, yaw)

        ray_body = cam_mount_body @ ray_sensor
        ray_ned = body_to_ned @ ray_body

        if ray_ned[2] <= 1e-6:
            return None

        cam_offset_ned = body_to_ned @ self.offset

        cam_height = alt_m - cam_offset_ned[2]
        if cam_height <= 0:
            return None

        t = cam_height / ray_ned[2]
        if t <= 0:
            return None

        north_m = cam_offset_ned[0] + (ray_ned[0] * t)
        east_m = cam_offset_ned[1] + (ray_ned[1] * t)

        return north_m, east_m
