import cv2
from collections import deque
import numpy as np  

from src.pyastrov.logger import setup_logger
from multiprocessing import Process, Manager
logger = setup_logger("stack")
class ImageStacker:
    def __init__(self,) : 
        self.buffer = Manager().list(deque([], maxlen=5) )
    def run(self,new_img) : 
        proc = Process(target=self.stack, args=(self.buffer,new_img,))
        proc.start()
        proc.join() 
    def stack(self, buffer,new_img: np.ndarray):
        if len(buffer) > 0 and new_img.dtype != buffer[0].dtype:
            logger.error("dtype is not the same %s != %s", new_img.dtype, buffer[0][0].dtype)
            return 
        if len(buffer) > 0 and new_img.shape != buffer[0].shape:
            logger.error("shape is not the same %s != %s", new_img.shape, buffer[0][0].shape)
            return

        if len(new_img.shape) == 4:
            new_img = new_img[:,:,:3]

        if len(buffer) == 0: 
            buffer.append(new_img)
            return
        base_img = buffer[0]
        try : 
            kp, des = self.get_keypoints(base_img)
            align = self.get_alignment_img(new_img, kp, des)

            avg_image = cv2.addWeighted(base_img, 0.7, align, 0.3, 0)
            #buffer.appendleft(avg_image)
            buffer.insert(0,avg_image)
        except Exception as e:
            logger.error(f"Faild to stack images  : {e} ")
            return

    def get_latest_stacked(self):
        return self.buffer[0]
  
    def get_keypoints(self,img, pt1=(0, 0), pt2=None):
        if pt2 is None:
            pt2 = (img.shape[1], img.shape[0])

        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        mask = cv2.rectangle(np.zeros_like(gray), pt1, pt2, color=1, thickness=-1)
        akaze = cv2.AKAZE_create()

        return akaze.detectAndCompute(gray, mask=mask)

    def get_matcher(self,img, kp2, des2):
        kp1, des1 = self.get_keypoints(img)

        if len(kp1) == 0 or len(kp2) == 0:
            return None

        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)

        good = [m for m, n in matches if m.distance < 0.8 * n.distance]

        if len(good) == 0:
            return None

        target_position = [[kp1[m.queryIdx].pt[0], kp1[m.queryIdx].pt[1]] for m in good]
        base_position = [[kp2[m.trainIdx].pt[0], kp2[m.trainIdx].pt[1]] for m in good]

        apt1 = np.array(target_position)
        apt2 = np.array(base_position)
        return apt1, apt2

    def get_alignment_img(self,img, kp2, des2):
        height, width = img.shape[:2]
        apt1, apt2 = self.get_matcher(img, kp2, des2)

        mtx = cv2.estimateAffinePartial2D(apt1, apt2)[0]

        if mtx is not None:
            return cv2.warpAffine(img, mtx, (width, height))
        else:
            return None

def test_stack():
    # generate random image
    base = np.random.randint(0,255, (1000,1000,3),dtype=np.uint8)
    frame = np.random.randint(0,255, (1000,1000,3),dtype=np.uint8)
    stacker = ImageStacker()
    stacker.run (base)

    print(len(stacker.buffer))
    stacker.run (frame)
    print(len(stacker.buffer))
    stacker.run (frame)
    stacker.run (frame)
    stacker.run (frame)
    print(len(stacker.buffer))


if __name__ == "__main__":
    test_stack()

        

