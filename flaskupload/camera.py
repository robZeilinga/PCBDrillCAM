
import cv2

class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture(0)
        self.video.set(3,320)
        self.video.set(4,240)
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        width = int(self.video.get(3))
        height = int(self.video.get(4))

        w2 = int(width/2)
        h2 = int(height/2)

        image = cv2.line(image, (w2,0), (w2,height), (0,255,255), 1)
        image = cv2.line(image, (0, h2), (width, h2), (0,255,255), 1)
        

        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        ret, jpeg = cv2.imencode('.jpg', image)
        #print("width : " + self.video.get(3))
        return jpeg.tobytes()