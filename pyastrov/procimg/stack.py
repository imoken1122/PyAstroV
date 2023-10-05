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
        self.new_image_buffer = deque([], maxlen=50)
        self.stacked_buffer = Manager().list([])
        self.is_stacking = False
        self.threashold = 0.99
    async def run_stack(self):
        base_img = self.new_image_buffer.pop()
        #setting base image 
        self.add_base(base_img)
        # get base image shape and dtype
        shape = base_img.shape
        dtype = base_img.dtype
    
        # define to send variable to other process
        new_img_shm = shared_memory.SharedMemory(create=True, size=np.prod(shape))
        is_stacking =mp.Value('i', 1) 
        buf_event = mp.Event() 
        buf_event.clear()

        self.is_stacking = True

        # start stack process
        p = mp.Process(target=self.stack_process, args=(new_img_shm, buf_event,self.stacked_buffer,is_stacking),daemon=True)
        p.start()
        n = 0
        while is_stacking.value == 1:

            is_stacking.value = int(self.is_stacking)
            if len(self.new_image_buffer)>0:
                logger.info("try stacking number %s",n)
                logger.debug("new images : %d",len(self.new_image_buffer))
                logger.debug("stacked image : %d ", len(self.stacked_buffer))
                buf_event.clear()
                new_img_buf = np.ndarray(shape, dtype=dtype, buffer=new_img_shm.buf)
                new_img_buf[:] = self.new_image_buffer.pop()
                buf_event.set()
                #len new images
                logger.debug(np.array(self.stacked_buffer[0]).mean().mean())

            await asyncio.sleep(2)

        p.join()
        new_img_shm.close()
        new_img_shm.unlink()
        return 
    
    def stack_process(self, new_img_shm, shm_event,buffer, is_stackking ): 
        shape = buffer[0].shape
        dtype = buffer[0].dtype
        while True:
            if is_stackking.value == 0 : return 
            shm_event.wait()
            new_img = np.ndarray(shape, dtype=dtype , buffer=new_img_shm.buf)

            self.stack(buffer,new_img)
            shm_event.clear()

    def add_base(self,base_img: np.ndarray):
        self.stacked_buffer.append(base_img)

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
        logger.debug("new image shape %s and buffer shape %s", new_img.shape, buffer[0].shape) 
        base_img = buffer[0]
        try : 
            kp, des = self.get_keypoints(base_img)
            
            align = self.get_alignment_img(new_img, kp, des)
            logger.debug("align shape %s", align.shape)
            avg_image = cv2.addWeighted(base_img, 0.5, align, 0.5, 0)

            if len(buffer) >= self.stacked_maxlen:
                buffer.pop()
            buffer.insert(0,avg_image)
            logger.info("Stacking success")
            # now time filename 
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            image = buffer[0]
            cv2.imwrite(f"output/{now}.jpg",buffer[0])
            return
            
        except Exception as e:
            logger.error(f"Faild to stack images  : {e} ")
            return

    def get_latest_stacked(self):
        if len(self.buffer) ==0 : 
            logger.error("buffer is empty")
            return []
        return self.buffer[0]
  
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



import threading,time
import pathlib
import pprint
async def test_stack():
    def func(stacker):
    # read images dirctory and read images 
        p = pathlib.Path("images")
        for i in p.glob("*.jpg"):
            img = cv2.imread(str(i))
            img = utils.adjust_rgb(img)
            img = utils.adjust_gamma(img,0.3 ).astype(img.dtype)    
            print("add")
            stacker.new_image_buffer.appendleft(img)
            for i in range(100000000):
                pass
    # generate random image
    p = pathlib.Path("images")
    pprint.pprint(list(p.glob('*.jpg')))
    l = p.glob("*.jpg")
    base_img = cv2.imread(str(next(l)))
    base_img = utils.adjust_rgb(base_img)
    base_img = utils.adjust_gamma(base_img,0.3 ).astype(base_img.dtype)    
    stacker = ImageStacker()
    threading.Thread(target=func, args=(stacker,)).start()
    await stacker.run_stack(base_img)
      #  cv2.imwrite(f"output/{g}.jpg",img)
if __name__ == "__main__":
    asyncio.run(test_stack())
 



        

