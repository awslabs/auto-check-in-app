import cv2


class Detector(object):
    PROTOTEXT = './assets/model/deploy.prototxt'
    CAFFEMODEL = './assets/model/res10_300x300_ssd_iter_140000.caffemodel'
    HAARLIKE = './assets/model/haarcascade_frontalface_alt2.xml'

    def __init__(self, env):
        try:
            self.FACE_AREA_THRESHOLD = env['FaceAreaThreshold']
            self.FACE_MARGIN_RATIO = env['FaceMarginRatio']
            self.USE_DEEP_LEANING_FOR_DETECTOR = env['UseDeepLeaningForDetector']

        except KeyError:
            print('Invalid config file')
            raise

        if self.USE_DEEP_LEANING_FOR_DETECTOR:
            print('Loading SSD model...')
            self.net = cv2.dnn.readNetFromCaffe(self.PROTOTEXT, self.CAFFEMODEL)
        else:
            print('Loading Haar-cascade classifier...')
            self.face_cascade = cv2.CascadeClassifier(self.HAARLIKE)
        print('Loaded!')

    def detect(self, frame):
        """
            Args:
                frame: input image
            Returns:
                face_exists
                face_image
        """

        cols = frame.shape[1]
        rows = frame.shape[0]
        if self.USE_DEEP_LEANING_FOR_DETECTOR:
            # Detect faces using OpenCV Face Detector (SSD)
            self.net.setInput(cv2.dnn.blobFromImage(
                frame, 1.0, (300, 300), (104.0, 177.0, 123.0), False, False))
            detections = self.net.forward()
            faces = []
            for i in range(detections.shape[2]):
                face_confidence_opencv = detections[0, 0, i, 2]
                if face_confidence_opencv > 0.8:
                    x = int(detections[0, 0, i, 3] * cols)
                    y = int(detections[0, 0, i, 4] * rows)
                    w = int(detections[0, 0, i, 5] * cols) - x
                    h = int(detections[0, 0, i, 6] * rows) - y
                    faces.append((x, y, w, h))
        else:
            # Detect faces using cv2.CascadeClassifier (light method)
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray_frame, 1.3, 5)

        # Find the largest face
        max_face_area = 0.
        max_face_idx = -1
        for i, (x, y, w, h) in enumerate(faces):
            area = w * h
            if area > max_face_area:
                max_face_area = area
                max_face_idx = i

        if max_face_idx != -1:
            x, y, w, h = faces[max_face_idx]

            margin_w = int(w / 2 * self.FACE_MARGIN_RATIO)
            margin_h = int(h / 2 * self.FACE_MARGIN_RATIO)
            x = int(max(0, x - margin_w))
            y = int(max(0, y - margin_h))
            w = w * (1 + self.FACE_MARGIN_RATIO)
            w = int(min(x + w, cols) - x)
            h = h * (1 + self.FACE_MARGIN_RATIO)
            h = int(min(y + h, rows) - y)

            if w < 0 or h < 0:
                return (False, None)

            # reject small faces
            area = w * h
            if area >= self.FACE_AREA_THRESHOLD and w > 80 and h > 80:
                face_image = frame[y:y+h, x:x+w]
                return (True, face_image)
            else:
                print('Small face (area={:,})'.format(area))

        return (False, None)
