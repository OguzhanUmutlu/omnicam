import subprocess

from .base_camera import CameraInfo
from .gstreamer_capture import GStreamerCapture


class GazeboCamera(GStreamerCapture):
    def __init__(self, port=4000, topic_name: str = None, timeout=5, info: CameraInfo = None, open_error=None,
                 timeout_error=None):
        self.topic_name = topic_name
        self.port = port
        super().__init__(
            GStreamerCapture.GstPipeline()
            .add("udpsrc", port=self.port)
            .add_caps("application/x-rtp")
            .add("rtph264depay")
            .add("h264parse")
            .add("avdec_h264")
            .add("videoconvert")
            .add("appsink", sync="false"),
            timeout=timeout, info=info,
            open_error=open_error or ValueError(f"Could not open Gazebo camera stream on port {self.port}"),
            timeout_error=timeout_error or TimeoutError(
                f"Could not open Gazebo camera stream on port {self.port} within {timeout} seconds")
        )

    def _open(self):
        if self.topic_name is not None:
            GazeboCamera.start_gz_stream(self.topic_name)
        super()._open()

    @staticmethod
    def start_gz_stream(topic_name):
        subprocess.run([
            "gz", "topic",
            "-t", f"/{topic_name}/image/enable_streaming",
            "-m", "gz.msgs.Boolean",
            "-p", "data: true"
        ])
