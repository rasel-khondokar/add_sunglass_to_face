import cv2

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]
    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image
    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)
    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)
    # return the resized image
    return resized



class AddGlassToEye(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier('resources/haarcascade_frontalface_default.xml')
        self.eyes_cascade = cv2.CascadeClassifier('resources/frontalEyes35x16.xml')
        self.glasses = cv2.imread("resources/large_glass.png", -1)

    def __del__(self):
        self.video.release()

    def add_glass_to_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #https://www.bogotobogo.com/python/OpenCV_Python/python_opencv3_Image_Object_Detection_Face_Detection_Haar_Cascade_Classifiers.php
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y + h, x:x + h]
            roi_color = frame[y:y + h, x:x + h]

            eyes = self.eyes_cascade.detectMultiScale(roi_gray, scaleFactor=1.5, minNeighbors=5)
            for (ex, ey, ew, eh) in eyes:
                # cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 3)
                roi_eyes = roi_gray[ey: ey + eh, ex: ex + ew]
                glasses2 = image_resize(self.glasses.copy(), width=ew)

                gw, gh, gc = glasses2.shape
                for i in range(0, gw):
                    for j in range(0, gh):
                        # print(glasses[i, j]) #RGBA
                        if glasses2[i, j][3] != 0:  # alpha 0
                            roi_color[ey + i, ex + j] = glasses2[i, j]

        # Resulting frame
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        return frame


    def add_glass_to_image(self, path, file_name):
        frame = cv2.imread(path+file_name)
        frame = self.add_glass_to_frame(frame)
        frame = cv2.resize(frame, (1280, 980), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
        cv2.imwrite('static/processed/' +file_name, frame)

    def add_glass_to_video(self):
        # Capture frame-by-frame
        ret, frame = self.video.read()
        frame = self.add_glass_to_frame(frame)
        frame = cv2.resize(frame, (1280, 980), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

def gen(camera):
    while True:
        frame = camera.add_glass_to_video()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
