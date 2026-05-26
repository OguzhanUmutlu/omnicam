from typing import Union, Tuple

from .base_camera import BaseCamera, resolutions, CameraInfo


class PiCamera(BaseCamera):
    rpi_camera_definitions = [
        CameraInfo(
            name="Camera Module 1", short_name="OV5647",
            focal_length_mm=(3.60, 3.60), pixel_size_um=1.40, max_resolution=(2592, 1944),
            aperture_f=2.9, hfov_deg=53.5, focus_type="Fixed", has_ir_filter=True
        ),
        CameraInfo(
            name="Camera Module 1 NoIR", short_name="OV5647 NoIR",
            focal_length_mm=(3.60, 3.60), pixel_size_um=1.40, max_resolution=(2592, 1944),
            aperture_f=2.9, hfov_deg=53.5, focus_type="Fixed", has_ir_filter=False
        ),
        CameraInfo(
            name="Camera Module 2", short_name="IMX219",
            focal_length_mm=(3.04, 3.04), pixel_size_um=1.12, max_resolution=(3280, 2464),
            aperture_f=2.0, hfov_deg=62.2, focus_type="Fixed", has_ir_filter=True
        ),
        CameraInfo(
            name="Camera Module 2 NoIR", short_name="IMX219 NoIR",
            focal_length_mm=(3.04, 3.04), pixel_size_um=1.12, max_resolution=(3280, 2464),
            aperture_f=2.0, hfov_deg=62.2, focus_type="Fixed", has_ir_filter=False
        ),
        CameraInfo(
            name="Camera Module 3 - Standard", short_name="IMX708 Standard",
            focal_length_mm=(4.74, 4.74), pixel_size_um=1.40, max_resolution=(4608, 2592),
            aperture_f=1.8, hfov_deg=66.0, focus_type="Autofocus", has_ir_filter=True
        ),
        CameraInfo(
            name="Camera Module 3 - Standard NoIR", short_name="IMX708 NoIR",
            focal_length_mm=(4.74, 4.74), pixel_size_um=1.40, max_resolution=(4608, 2592),
            aperture_f=1.8, hfov_deg=66.0, focus_type="Autofocus", has_ir_filter=False
        ),
        CameraInfo(
            name="Camera Module 3 - Wide", short_name="IMX708 Wide",
            focal_length_mm=(2.75, 2.75), pixel_size_um=1.40, max_resolution=(4608, 2592),
            aperture_f=2.2, hfov_deg=102.0, focus_type="Autofocus", has_ir_filter=True
        ),
        CameraInfo(
            name="Camera Module 3 - Wide NoIR", short_name="IMX708 Wide NoIR",
            focal_length_mm=(2.75, 2.75), pixel_size_um=1.40, max_resolution=(4608, 2592),
            aperture_f=2.2, hfov_deg=102.0, focus_type="Autofocus", has_ir_filter=False
        ),
        CameraInfo(
            name="High Quality Camera w/ 6mm Lens", short_name="IMX477 6mm",
            focal_length_mm=(6.00, 6.00), pixel_size_um=1.55, max_resolution=(4056, 3040),
            aperture_f=1.2, hfov_deg=55.0, focus_type="Manual", has_ir_filter=True
        ),
        CameraInfo(
            name="High Quality Camera w/ 16mm Lens", short_name="IMX477 16mm",
            focal_length_mm=(16.00, 16.00), pixel_size_um=1.55, max_resolution=(4056, 3040),
            aperture_f=1.4, hfov_deg=22.2, focus_type="Manual", has_ir_filter=True
        ),
        CameraInfo(
            name="High Quality Camera w/ 35mm Lens", short_name="IMX477 35mm",
            focal_length_mm=(35.00, 35.00), pixel_size_um=1.55, max_resolution=(4056, 3040),
            aperture_f=1.7, hfov_deg=10.1, focus_type="Manual", has_ir_filter=True
        ),
        CameraInfo(
            name="High Quality Camera w/ 8mm M12 Lens", short_name="IMX477 M12-8mm",
            focal_length_mm=(8.00, 8.00), pixel_size_um=1.55, max_resolution=(4056, 3040),
            aperture_f=1.8, hfov_deg=49.0, focus_type="Manual", has_ir_filter=True
        ),
        CameraInfo(
            name="High Quality Camera w/ 25mm M12 Lens", short_name="IMX477 M12-25mm",
            focal_length_mm=(25.00, 25.00), pixel_size_um=1.55, max_resolution=(4056, 3040),
            aperture_f=2.4, hfov_deg=14.4, focus_type="Manual", has_ir_filter=True
        ),
        CameraInfo(
            name="High Quality Camera w/ 2.7mm M12 Fisheye", short_name="IMX477 M12-Fish",
            focal_length_mm=(2.70, 2.70), pixel_size_um=1.55, max_resolution=(4056, 3040),
            aperture_f=2.5, hfov_deg=140.0, focus_type="Manual", has_ir_filter=True
        ),
        CameraInfo(
            name="Global Shutter Camera w/ 6mm Lens", short_name="IMX296 6mm",
            focal_length_mm=(6.00, 6.00), pixel_size_um=3.45, max_resolution=(1456, 1088),
            aperture_f=1.2, hfov_deg=45.0, focus_type="Manual", has_ir_filter=True
        ),
        CameraInfo(
            name="Global Shutter Camera w/ 16mm Lens", short_name="IMX296 16mm",
            focal_length_mm=(16.00, 16.00), pixel_size_um=3.45, max_resolution=(1456, 1088),
            aperture_f=1.4, hfov_deg=17.8, focus_type="Manual", has_ir_filter=True
        ),
        CameraInfo(
            name="Raspberry Pi AI Camera", short_name="IMX500",
            focal_length_mm=(4.74, 4.74), pixel_size_um=1.55, max_resolution=(4056, 3040),
            aperture_f=1.79, hfov_deg=66.3, focus_type="Manual", has_ir_filter=True
        )
    ]

    rpi_cameras = {}
    for cam_info in rpi_camera_definitions:
        rpi_cameras[cam_info.name] = cam_info
        rpi_cameras[cam_info.short_name] = cam_info

    def __init__(self, model: Union[str, CameraInfo], resolution: Union[Tuple[int, int], str] = "720p", open=True):
        super().__init__(open=open)
        if not isinstance(model, CameraInfo):
            if model not in PiCamera.rpi_cameras:
                raise ValueError(f"Unsupported: {model}. Supported models: {', '.join(PiCamera.rpi_cameras.keys())}")
            if isinstance(resolution, str) and resolution not in resolutions and resolution not in resolutions.values():
                raise ValueError(
                    f"Unsupported resolution: {resolution}. Supported resolutions: {', '.join(str(r) for r in resolutions.values())}")
            model = PiCamera.rpi_cameras[model]
        if isinstance(resolution, str):
            resolution = resolutions[resolution]
        self.resolution = resolution
        self.model = model

    def _open(self):
        try:
            from picamera2 import Picamera2
        except Exception as e:
            raise ImportError("PiCamera could not be initialized. Is picamera2 installed?") from e
        self.cam = Picamera2()
        self.cam.preview_configuration.main.format = "RGB888"
        self.cam.preview_configuration.main.size = self.resolution
        self.cam.configure("preview")
        self.cam.start()

    def _read(self):
        return self.cam.capture_array()

    def _release(self):
        if not self.closed:
            self.closed = True
            self.cam.stop()
            self.cam.close()

    def _size(self):
        return self.resolution

    def focal_length(self):
        return self.model.focal_length(self.size())
