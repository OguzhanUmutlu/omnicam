from .base_camera import BaseCamera, CameraInfo


class CVCameraBase(BaseCamera):
    def __init__(self, args: list, timeout=None, open=True, info: CameraInfo = None, open_error=None,
                 timeout_error=None,
                 **kwargs):
        try:
            import cv2
        except Exception as exc:
            raise ImportError(
                "OpenCV is required for this feature. Install with 'pip install omnicam[opencv]'.") from exc
        self._cv2 = cv2
        super().__init__(open=open, info=info)
        self.open_error = open_error or RuntimeError(f"Camera could not be opened with args {args}")
        self.timeout_error = timeout_error or TimeoutError(
            f"Failed to open camera with args {args} within {timeout} seconds")
        self.cv_args = args
        self.cv_kwargs = kwargs
        self.cam = None
        self._frame_size = None
        self.timeout = timeout

    def _open(self):
        self.cam = self._cv2.VideoCapture(*self.cv_args, **self.cv_kwargs)
        if self.timeout is not None:
            start_time = self._cv2.getTickCount()
            while not self.cam.isOpened():
                elapsed_time = (self._cv2.getTickCount() - start_time) / self._cv2.getTickFrequency()
                if elapsed_time > self.timeout:
                    raise self.timeout_error
        elif not self.cam.isOpened():
            raise self.open_error
        self._frame_size = int(self.cam.get(self._cv2.CAP_PROP_FRAME_WIDTH)), int(
            self.cam.get(self._cv2.CAP_PROP_FRAME_HEIGHT))

    def _read(self):
        ret, frame = self.cam.read()
        return frame if ret else None

    def _release(self):
        self.cam.release()

    def _size(self):
        return self._frame_size
