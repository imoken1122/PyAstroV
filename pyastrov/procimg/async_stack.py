import cv2
from collections import deque
import numpy as np  
import asyncio
from pyastrov.logger import setup_logger
from multiprocessing import Process, Manager,shared_memory
import multiprocessing as mp
from collections import deque
from pyastrov.procimg import utils
from datetime import datetime
logger = setup_logger("stack")
class ImageStacker:
    def __init__(self,) : 
        self.stacked_maxlen = 10
        self.stacked_buffer =deque([], maxlen=10)
        self.is_stacking = False
        self.num_stacked = 0
        self.threashold = 0.99

     
    def get_num_stack(self):
        return len(self.stacked_buffer)
  
    def is_stackking(self):
        return self.is_stacking
    def add_base(self,base_img: np.ndarray):
        self.stacked_buffer.append(base_img)

    async def run_stack(self,new_img: np.ndarray):
        if len(new_img.shape) == 4:
            new_img = new_img[:,:,:3]

        if self.get_num_stack() == 0:
            self.stacked_buffer.append(new_img)
            logger.info("Set base image")
            return

        if len(self.stacked_buffer) > 0 and new_img.dtype != self.stacked_buffer[0].dtype:
            logger.error("dtype is not the same %s != %s", new_img.dtype, self.stacked_buffer[0].dtype)
            return 
        if len(self.stacked_buffer) > 0 and new_img.shape != self.stacked_buffer[0].shape:
            logger.error("shape is not the same %s != %s", new_img.shape, self.stacked_buffer[0].shape)
            return

        logger.debug("new image shape %s and buffer shape %s", new_img.shape, self.stacked_buffer[0].shape) 
        base_img = self.stacked_buffer[0]

        try : 
            kp, des = self.get_keypoints(base_img)
            await asyncio.sleep(0.1)
            align = self.get_alignment_img(new_img, kp, des)
            await asyncio.sleep(0.1)

            logger.debug("align shape %s", align.shape)
            avg_image = cv2.addWeighted(base_img, 0.5, align, 0.5, 0)

            self.stacked_buffer.appendleft(avg_image)
            logger.info("Stacking success")

            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            cv2.imwrite(f"output/{now}.jpg",self.stacked_buffer[0])
            return 
            
        except Exception as e:
            logger.error(f"Faild to stack images  : {e} ")
            return

    def get_latest_stacked(self):
        if len(self.stacked_buffer) ==0 : 
            logger.error("buffer is empty")
            return None
        return self.stacked_buffer[0]
  
    def get_keypoints(self,img, pt1=(0, 0), pt2=None):
        if pt2 is None:
            pt2 = (img.shape[1], img.shape[0])

        #img = utils.exec_clahe(img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        mask = cv2.rectangle(np.zeros_like(gray), pt1, pt2, color=1, thickness=-1)
        akaze = cv2.AKAZE_create()

        return akaze.detectAndCompute(gray, mask=mask)

    def get_matcher(self,img, kp2, des2):
        kp1, des1 = self.get_keypoints(img)

        if len(kp1) == 0 or len(kp2) == 0:
            logger.error("keypoints is empty")
            return None,None

        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)

        good = [m for m, n in matches if m.distance < self.threashold * n.distance]

        if len(good) == 0:
            logger.error("good is empty")
            return None,None

        target_position = [[kp1[m.queryIdx].pt[0], kp1[m.queryIdx].pt[1]] for m in good]
        base_position = [[kp2[m.trainIdx].pt[0], kp2[m.trainIdx].pt[1]] for m in good]

        apt1 = np.array(target_position)
        apt2 = np.array(base_position)
        return apt1, apt2

    def get_alignment_img(self,img, kp2, des2):
        height, width = img.shape[:2]
        apt1, apt2 = self.get_matcher(img, kp2, des2)
        if apt1 is None or apt2 is None:
            return None

        mtx = cv2.estimateAffinePartial2D(apt1, apt2,confidence=0.99)[0]

        if mtx is not None:
            logger.debug("Found affine matrix") 
            return cv2.warpAffine(img, mtx, (width, height))
        else:
            logger.debug("Not found affine matrix")
            return None
    def save_stacked(self,stack_i:  int, filename:str ):
        if len(self.stacked_buffer) == 0 : 
            logger.error("stacked buffer is empty")
            return
        img = self.stacked_buffer[stack_i]
        cv2.imwrite(filename,img)
        logger.info(f"Saved stacked image to {filename}")
    def is_stacking(self):
        return self.is_stacking
    def clear_buffer(self):
        if self.is_stacking:
            logger.error("Cannot remove stacked image while stacking")
            return
        self.stacked_buffer[:] = []
        self.num_stacked = 0
        logger.info("Removed all stacked images")
    def stop_stack(self):
        self.is_stacking = False
    def start_stack(self):
        self.is_stacking = True 