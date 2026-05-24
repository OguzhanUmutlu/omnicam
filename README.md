# omnicam

A small, unified API for reading frames from USB cameras, IP streams, video files, screen capture, and Raspberry Pi
cameras.

## Features

- Unified `BaseCamera` interface across backends
- OpenCV-based capture for USB webcams, video files, RTSP/HTTP streams, and GStreamer pipelines
- Optional Raspberry Pi Camera support (Picamera2)
- Optional screen capture via `mss`

## Installation

```bash
pip install omnicam
```

Optional extras:

```bash
pip install omnicam[opencv]
pip install omnicam[screen]
pip install omnicam[pi]
```

## Quickstart

```python
from omnicam import SimpleCamera

with SimpleCamera(index=0) as cam:
    frame = cam.read()
    if frame is not None:
        print(frame.shape)
```

## Camera types

```python
from omnicam import FileCapture, InternetCapture, ScreenCapture

# Video file
cam = FileCapture("/path/to/video.mp4")

# IP camera or MJPEG stream
cam = InternetCapture("http://192.168.1.10:8080/video")

# Screen capture (requires omnicam[screen])
cam = ScreenCapture(index=1)
```

## Raspberry Pi camera

```python
from omnicam import PiCamera

cam = PiCamera(model="IMX219", resolution="720p")
```

## GStreamer and Gazebo

```python
from omnicam import GStreamerCapture, GazeboCamera

pipeline = (
    GStreamerCapture.GstPipeline()
    .add("v4l2src", device="/dev/video0")
    .add("videoconvert")
    .add("appsink")
)
cam = GStreamerCapture(pipeline)

# Gazebo (requires gz tools available on PATH)
cam = GazeboCamera(topic_name="my_camera")
```

## CameraInfo (advanced)

`CameraInfo` describes physical camera parameters and enables focal-length math
and focus validation. It is optional but useful when you need real-world camera
intrinsics.

Fields:
- `name`: Full model name.
- `short_name`: Short identifier (sensor/model code).
- `focal_length_mm`: `(fx_mm, fy_mm)` in millimeters.
- `pixel_size_um`: Pixel size in micrometers.
- `max_resolution`: `(width, height)` at sensor maximum.
- `aperture_f`: F-number (e.g., `2.0`).
- `hfov_deg`: Horizontal field of view in degrees.
- `focus_type`: `"Fixed" | "Autofocus" | "Manual" | "Unknown"`.
- `has_ir_filter`: `True` if the camera has an IR filter.

Usage example:

```python
from omnicam import SimpleCamera
from omnicam.base_camera import CameraInfo

info = CameraInfo(
    name="My Camera Model",
    short_name="MYCAM",
    focal_length_mm=(4.0, 4.0),
    pixel_size_um=1.4,
    max_resolution=(1920, 1080),
    aperture_f=2.0,
    hfov_deg=70.0,
    focus_type="Manual",
    has_ir_filter=True,
)

with SimpleCamera(index=0, info=info) as cam:
    fx, fy = cam.focal_length()  # focal length in pixels at current size
```

If you only know focal length in pixel units, use:

```python
from omnicam.base_camera import CameraInfo

info = CameraInfo.from_focal_length(
    name="Synthetic",
    short_name="SYN",
    focal_length=(800.0, 800.0),
    resolution=(1280, 720),
)
```

Default Raspberry Pi cameras (short name → full name):
- `OV5647` → `Camera Module 1`
- `OV5647 NoIR` → `Camera Module 1 NoIR`
- `IMX219` → `Camera Module 2`
- `IMX219 NoIR` → `Camera Module 2 NoIR`
- `IMX708 Standard` → `Camera Module 3 - Standard`
- `IMX708 NoIR` → `Camera Module 3 - Standard NoIR`
- `IMX708 Wide` → `Camera Module 3 - Wide`
- `IMX708 Wide NoIR` → `Camera Module 3 - Wide NoIR`
- `IMX477 6mm` → `High Quality Camera w/ 6mm Lens`
- `IMX477 16mm` → `High Quality Camera w/ 16mm Lens`
- `IMX477 35mm` → `High Quality Camera w/ 35mm Lens`
- `IMX477 M12-8mm` → `High Quality Camera w/ 8mm M12 Lens`
- `IMX477 M12-25mm` → `High Quality Camera w/ 25mm M12 Lens`
- `IMX477 M12-Fish` → `High Quality Camera w/ 2.7mm M12 Fisheye`
- `IMX296 6mm` → `Global Shutter Camera w/ 6mm Lens`
- `IMX296 16mm` → `Global Shutter Camera w/ 16mm Lens`
- `IMX500` → `Raspberry Pi AI Camera`

## Notes

- `numpy` is required. OpenCV-based backends need `omnicam[opencv]`.
- GStreamer and Gazebo features rely on system-level tooling.

## License

MIT. See `LICENSE`.
