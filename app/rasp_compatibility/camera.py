# coding: utf-8
from picamera.array import PiRGBArray
from picamera import PiCamera

# sensor modes as detailed in https://picamera.readthedocs.io/en/release-1.13/fov.html#sensor-modes
sensor_modes = [(1920,1080,30),(3280,2464,15),(3280,2464,15),(1640,1232,40),(1640,922,40),(1280,720,90),(640,480,90)]

RES_HD = 0
RES_FULL_HD = 1
RES_1232 = 3
RES_922 = 4
RES_720 = 5
RES_480 = 6

class RaspCamera():

    def __init__(self, sensor_mode, frame_rate=0):
        width, height, max_fps = sensor_modes[sensor_mode]
        if not frame_rate:
            frame_rate = int(2*max_fps/3)

        """initialize the camera and grab a reference to the raw camera capture and return a camera object"""
        self.cam = PiCamera(sensor_mode=sensor_mode + 1, resolution=(width, height), framerate=frame_rate)

    def read(self):
        """return a frame took by the camera in a numpy array format"""
        raw_capture = PiRGBArray(self.cam, size=self.cam.resolution)
        self.cam.capture(raw_capture, format="bgr")
        frame = raw_capture.array
        return frame is not None, frame
