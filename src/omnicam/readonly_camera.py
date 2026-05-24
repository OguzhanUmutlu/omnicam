from typing import Tuple

from .base_camera import BaseCamera


class ReadonlyCamera(BaseCamera):
    def __init__(self, cam: BaseCamera):
        super().__init__()
        self.cam = cam

    def _open(self):
        self.cam._open()

    def _read(self):
        return self.cam._read()

    def _release(self):
        pass

    def _size(self):
        return self.cam._size()

    def _focus(self, rectangle: Tuple[int, int, int, int]):
        self.cam._focus(rectangle)

    def focal_length(self):
        return self.cam.focal_length()
