import subprocess

from .base_camera import CameraInfo, BaseCamera
from .gstreamer_capture import GStreamerCapture


class GazeboCamera(GStreamerCapture):
    def __init__(self, port=4000, topic_name: "str | None" = None, timeout=5, open=True,
                 info: "CameraInfo | BaseCamera | None" = None, open_error=None, timeout_error=None):
        self.topic_name = topic_name
        self.port = port
        super().__init__(
            f"udpsrc port={self.port} ! "
            "application/x-rtp, media=video, clock-rate=90000, encoding-name=H264 ! "
            "rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! "
            "appsink sync=false drop=true max-buffers=1",
            timeout=timeout, open=open, info=info,
            open_error=open_error or ValueError(f"Could not open Gazebo camera stream on port {self.port}"),
            timeout_error=timeout_error or TimeoutError(
                f"Could not open Gazebo camera stream on port {self.port} within {timeout} seconds")
        )

    def _open(self):
        if self.topic_name is not None:
            GazeboCamera.start_gz_stream(self.topic_name)
        super()._open()

    def enable(self):
        GazeboCamera.start_gz_stream(topic_name=self.topic_name)

    @staticmethod
    def start_gz_stream(topic_name):
        subprocess.run([
            "gz", "topic",
            "-t", f"/{topic_name}/image/enable_streaming",
            "-m", "gz.msgs.Boolean",
            "-p", "data: true"
        ])
