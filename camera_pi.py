import io
import os
import time
import picamera
import picamera.array
from base_camera import BaseCamera

import time

import cv2
from time import sleep
import datetime

import numpy as np

class Camera(BaseCamera):
    video_source = 0
    config = None
    def __init__(self, config):
        Camera.config = config
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        with picamera.PiCamera() as camera:
            camera.vflip = True
            camera.hflip = True
            resX = Camera.config['input_shape'][1]
            resY = Camera.config['input_shape'][0]
            colors = Camera.config['input_shape'][2]
            image_np = np.empty(Camera.config['input_shape'], dtype=np.uint8)
            camera.resolution = (resX, resY)

            # 309 MS
            stream = io.BytesIO()
            for _ in camera.capture_continuous(stream, 'bgr',use_video_port=True):
                # return current frame
                stream.seek(0)

                image_np = np.frombuffer(stream.read(), dtype=np.uint8, count=resX*resY*colors).reshape(Camera.config['input_shape'])

                yield image_np
                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

