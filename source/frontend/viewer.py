import cv2
import time
import platform

if platform.system() == 'Windows':
    import winsound
else:
    import subprocess


class Viewer(object):
    VIEWER_WINDOW_NAME = 'viewer'
    VIEW_FACE_WIDTH = 480
    VIEW_FACE_HEIGHT = 660
    VIEW_FACE_CY = 720
    VIEW_TEXT_CY = 280
    NEXT_IMAGE_PATH = "./assets/display/next.jpeg"
    CHECKING_IMAGE_PATH = "./assets/display/checking.jpeg"
    OK_IMAGE_PATH = "./assets/display/welcome.jpeg"
    OK_SOUND_PATH = "./assets/sound/ok.wav"

    def __init__(self, env):
        self.platform_system = platform.system()
        self.next_image = cv2.imread(self.NEXT_IMAGE_PATH)
        self.checking_image = cv2.imread(self.CHECKING_IMAGE_PATH)
        self.ok_image = cv2.imread(self.OK_IMAGE_PATH)
        if self.next_image is None or self.ok_image is None or self.checking_image is None:
            raise RuntimeError('Cannot load asset images')

        cv2.namedWindow(self.VIEWER_WINDOW_NAME,
                        cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)

    def show_welcome(self, face_image, name):
        image = self.ok_image.copy()
        image_width = image.shape[1]
        resized_face_image = cv2.resize(
            face_image, (self.VIEW_FACE_WIDTH, self.VIEW_FACE_HEIGHT))
        image[int(self.VIEW_FACE_CY - self.VIEW_FACE_HEIGHT/2):int(self.VIEW_FACE_CY + self.VIEW_FACE_HEIGHT/2),
              int(image_width/2 - self.VIEW_FACE_WIDTH/2):int(image_width/2 + self.VIEW_FACE_WIDTH/2)] = resized_face_image
        font = cv2.FONT_HERSHEY_SIMPLEX
        textsize = cv2.getTextSize(name, font, 5, 10)[0]
        text_x = int((image.shape[1] - textsize[0]) / 2)
        cv2.putText(image, '{}'.format(name), (text_x, self.VIEW_TEXT_CY),
                    cv2.FONT_HERSHEY_SIMPLEX, 5, (17, 114, 236), 10, cv2.LINE_AA)
        cv2.putText(image, '{}'.format(name), (text_x, self.VIEW_TEXT_CY),
                    cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 255, 255), 4, cv2.LINE_AA)
        cv2.imshow(self.VIEWER_WINDOW_NAME, image)
        cv2.waitKey(1)
        if self.platform_system == 'Windows':
            winsound.PlaySound(self.OK_SOUND_PATH, winsound.SND_FILENAME)
        elif self.platform_system == 'Linux':
            subprocess.call("aplay -q " + self.OK_SOUND_PATH, shell=True)
        else:
            subprocess.call("afplay " + self.OK_SOUND_PATH, shell=True)

    def show_checking(self, face_image):
        image = self.checking_image.copy()
        image_width = image.shape[1]
        resized_face_image = cv2.resize(
            face_image, (self.VIEW_FACE_WIDTH, self.VIEW_FACE_HEIGHT))
        resized_face_image = cv2.resize(
            face_image, (self.VIEW_FACE_WIDTH, self.VIEW_FACE_HEIGHT))
        image[int(self.VIEW_FACE_CY - self.VIEW_FACE_HEIGHT/2):int(self.VIEW_FACE_CY + self.VIEW_FACE_HEIGHT/2),
              int(image_width/2 - self.VIEW_FACE_WIDTH/2):int(image_width/2 + self.VIEW_FACE_WIDTH/2)] = resized_face_image
        cv2.imshow(self.VIEWER_WINDOW_NAME, image)
        cv2.waitKey(1)

    def show_next(self):
        cv2.imshow(self.VIEWER_WINDOW_NAME, self.next_image)
