from .base_camera import CameraInfo
from .cv_camera_base import CVCameraBase


class GStreamerCapture(CVCameraBase):
    class GstPipeline:
        def __init__(self):
            self.elements = []

        def add(self, element_name, **properties):
            if not properties:
                self.elements.append(element_name)
                return self
            props_str = " ".join(f"{k}={v}" for k, v in properties.items())
            element = f"{element_name} {props_str}".strip()
            self.elements.append(element)
            return self

        def add_caps(self, caps: str):
            self.elements.append(caps)
            return self

        def __str__(self):
            return " ! ".join(self.elements)

    def __init__(self, gstreamer_string: "GstPipeline | str", timeout=5, open=True, info: CameraInfo = None,
                 open_error=None,
                 timeout_error=None):
        try:
            import cv2
        except Exception as exc:
            raise ImportError(
                "OpenCV is required for this feature. Install with 'pip install omnicam[opencv]'."
            ) from exc
        gstreamer_string = str(gstreamer_string)
        self.gstreamer_string = gstreamer_string
        super().__init__(
            [gstreamer_string, cv2.CAP_GSTREAMER],
            timeout=timeout, open=open, info=info,
            open_error=open_error or RuntimeError(f"Could not open GStreamer stream with \"{gstreamer_string}\""),
            timeout_error=timeout_error or TimeoutError(
                f"Could not open GStreamer stream with \"{gstreamer_string}\" within {timeout} seconds")
        )
