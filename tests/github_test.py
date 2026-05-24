import sys
import types
from typing import Tuple

import numpy as np
import pytest

from omnicam.base_camera import BaseCamera, CameraInfo, resolutions
from omnicam.cv_camera_base import CVCameraBase
from omnicam.file_capture import FileCapture
from omnicam.gazebo_camera import GazeboCamera
from omnicam.gstreamer_capture import GStreamerCapture
from omnicam.internet_capture import InternetCapture
from omnicam.pi_camera import PiCamera
from omnicam.readonly_camera import ReadonlyCamera
from omnicam.simple_camera import SimpleCamera


def build_fake_cv2(
        *,
        opened=True,
        frame_size=(640, 480),
        read_return=(True, np.zeros((10, 10, 3), dtype=np.uint8)),
        tick_values=None,
):
    class FakeCapture:
        def __init__(self):
            self._opened = opened
            self.released = False

        def isOpened(self):
            return self._opened

        def read(self):
            return read_return

        def get(self, prop):
            if prop == fake_cv2.CAP_PROP_FRAME_WIDTH:
                return frame_size[0]
            if prop == fake_cv2.CAP_PROP_FRAME_HEIGHT:
                return frame_size[1]
            return 0

        def release(self):
            self.released = True

    tick_iter = iter(tick_values or [0, 0, 0])

    def getTickCount():
        return next(tick_iter)

    def getTickFrequency():
        return 1.0

    def VideoCapture(*_args, **_kwargs):
        return FakeCapture()

    fake_cv2 = types.SimpleNamespace(
        VideoCapture=VideoCapture,
        getTickCount=getTickCount,
        getTickFrequency=getTickFrequency,
        CAP_PROP_FRAME_WIDTH=3,
        CAP_PROP_FRAME_HEIGHT=4,
        CAP_GSTREAMER=100,
        CAP_DSHOW=200,
        CAP_V4L2=300,
    )
    return fake_cv2


class DummyCamera(BaseCamera):
    def __init__(self, frames, size=(640, 480), info=None):
        super().__init__(info=info)
        self._frames = list(frames)
        self._size_value = size
        self._open_called = False
        self._release_called = False
        self.focus_calls = []

    def _open(self):
        self._open_called = True

    def _read(self):
        if not self._frames:
            return None
        return self._frames.pop(0)

    def _release(self):
        self._release_called = True

    def _size(self):
        return self._size_value

    def _focus(self, rectangle: Tuple[int, int, int, int]):
        self.focus_calls.append(rectangle)


def test_camera_info_focal_length_scales():
    info = CameraInfo(
        name="Test",
        short_name="T",
        focal_length_mm=(4.0, 4.0),
        pixel_size_um=2.0,
        max_resolution=(200, 100),
        aperture_f=2.0,
        hfov_deg=60.0,
        focus_type="Manual",
        has_ir_filter=True,
    )
    fx, fy = info.focal_length((100, 50))
    assert fx == pytest.approx(info.base_focal_length[0] * 0.5)
    assert fy == pytest.approx(info.base_focal_length[1] * 0.5)


def test_camera_info_from_focal_length_roundtrip():
    info = CameraInfo.from_focal_length("Test", "T", (100.0, 200.0), resolution=(1000, 1000))
    assert info.focal_length((500, 500)) == pytest.approx((50.0, 100.0))


def test_base_camera_read_sets_closed_on_none():
    cam = DummyCamera([np.zeros((1, 1, 3), dtype=np.uint8), None])
    assert cam.read() is not None
    assert cam.closed is False
    assert cam.read() is None
    assert cam.closed is True
    with pytest.raises(PermissionError):
        cam.read()


def test_base_camera_frames_generator_stops():
    cam = DummyCamera([1, 2, None, 3])
    assert list(cam.frames()) == [1, 2]


def test_base_camera_focus_restrictions():
    info = CameraInfo(
        name="Fixed",
        short_name="F",
        focal_length_mm=(1.0, 1.0),
        pixel_size_um=1.0,
        max_resolution=(1, 1),
        aperture_f=1.0,
        hfov_deg=1.0,
        focus_type="Fixed",
        has_ir_filter=True,
    )
    cam = DummyCamera([None], info=info)
    with pytest.raises(ValueError):
        cam.focus((0, 0, 1, 1))


def test_base_camera_open_on_closed_raises():
    cam = DummyCamera([])
    cam.closed = True
    with pytest.raises(PermissionError):
        cam.open()


def test_readonly_camera_delegates_calls():
    cam = DummyCamera(["frame"])
    readonly = ReadonlyCamera(cam)
    readonly.open()
    assert cam._open_called is True
    assert readonly.read() == "frame"
    assert readonly.size() == (640, 480)
    readonly.focus((1, 2, 3, 4))
    assert cam.focus_calls == [(1, 2, 3, 4)]
    readonly.release()
    assert cam._release_called is False


def test_cv_camera_base_open_sets_frame_size(monkeypatch):
    fake_cv2 = build_fake_cv2()
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)
    cam = CVCameraBase([0])
    cam.open()
    assert cam.size() == (640, 480)
    frame = cam.read()
    assert isinstance(frame, np.ndarray)
    cam.release()


def test_cv_camera_base_open_error(monkeypatch):
    fake_cv2 = build_fake_cv2(opened=False)
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)
    cam = CVCameraBase([0])
    with pytest.raises(RuntimeError):
        cam.open()


def test_cv_camera_base_timeout_error(monkeypatch):
    fake_cv2 = build_fake_cv2(opened=False, tick_values=[0, 10])
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)
    cam = CVCameraBase([0], timeout=1)
    with pytest.raises(TimeoutError):
        cam.open()


def test_internet_capture_url_normalization(monkeypatch):
    fake_cv2 = build_fake_cv2()
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)
    cam = InternetCapture("example.com")
    assert cam.cv_args[0] == "http://example.com:8080/video"
    cam = InternetCapture("https://example.com:9090/stream")
    assert cam.cv_args[0] == "https://example.com:9090/stream"


def test_file_capture_missing_path_raises(tmp_path):
    missing = tmp_path / "missing.mp4"
    with pytest.raises(ValueError):
        FileCapture(str(missing))


def test_file_capture_existing_path_sets_args(monkeypatch, tmp_path):
    fake_cv2 = build_fake_cv2()
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)
    path = tmp_path / "video.mp4"
    path.write_bytes(b"not-a-real-video")
    cam = FileCapture(str(path))
    assert cam.cv_args == [str(path)]


def test_gstreamer_pipeline_str():
    pipeline = (
        GStreamerCapture.GstPipeline()
        .add("v4l2src", device="/dev/video0")
        .add_caps("video/x-raw")
        .add("appsink")
    )
    assert str(pipeline) == "v4l2src device=/dev/video0 ! video/x-raw ! appsink"


def test_gazebo_camera_start_gz_stream(monkeypatch):
    calls = []

    def fake_run(args, **_kwargs):
        calls.append(args)

    monkeypatch.setattr("subprocess.run", fake_run)
    GazeboCamera.start_gz_stream("my_cam")
    assert calls == [[
        "gz",
        "topic",
        "-t",
        "/my_cam/image/enable_streaming",
        "-m",
        "gz.msgs.Boolean",
        "-p",
        "data: true",
    ]]


def test_pi_camera_resolution_validation():
    with pytest.raises(ValueError):
        PiCamera("IMX219", resolution="bad")
    cam = PiCamera("IMX219", resolution="720p")
    assert cam.resolution == resolutions["720p"]


def test_simple_camera_uses_platform_capture_flag(monkeypatch):
    fake_cv2 = build_fake_cv2()
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)

    monkeypatch.setattr("platform.system", lambda: "Windows")
    cam = SimpleCamera(index=2)
    assert cam.cv_args == [2, fake_cv2.CAP_DSHOW]

    monkeypatch.setattr("platform.system", lambda: "Linux")
    cam = SimpleCamera(index=3)
    assert cam.cv_args == [3, fake_cv2.CAP_V4L2]


def test_context_manager_opens_and_releases():
    cam = DummyCamera(["frame"])
    with cam as opened:
        assert opened._open_called is True
        assert opened.read() == "frame"
    assert cam._release_called is True
