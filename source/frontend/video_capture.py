import cv2
import datetime


class VideoCapture(object):

    def __init__(self, env, video_device):
        try:
            self.CROPPED_IMAGE_WIDTH = env['CroppedImageWidth']
            self.CROPPED_IMAGE_HEIGHT = env['CroppedImageHeight']
        except KeyError:
            print('Invalid config file')
            raise

        print('video_device:', video_device)
        self.cap = cv2.VideoCapture(video_device)
        if not self.cap.isOpened():
            raise RuntimeError('Cannot open camera')
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

    def read(self):
        # clear buffer of VideoCapture
        for i in range(5):
            self.cap.grab()

        ret, frame = self.cap.read()
        if ret is False or frame is None:
            return None
        # crop
        cx = frame.shape[1] / 2
        cy = frame.shape[0] / 2
        frame_ = frame[int(cy-self.CROPPED_IMAGE_HEIGHT/2):int(cy+self.CROPPED_IMAGE_HEIGHT/2),
                       int(cx-self.CROPPED_IMAGE_WIDTH/2):int(cx+self.CROPPED_IMAGE_WIDTH/2)]
        return frame_

    def release(self):
        if self.cap is not None:
            self.cap.release()
