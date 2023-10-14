import cv2
from numba import jit
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
        self.new_image_buffer = deque([], maxlen=5)
        self.stacked_buffer = Manager().list([])
        self.is_stacking = False
        self.num_stacked = 0
        self.threashold = 0.99
    def start_stack(self):
        self.is_stacking = True
        
    async def run_stack(self):
        if len(self.stacked_buffer) == 0:
            base_img = self.new_image_buffer[0]
        else : 
            base_img = self.stacked_buffer[0]

        #setting base image 
        self.add_base(base_img)
        # get base image shape and dtype
        shape = base_img.shape
        dtype = base_img.dtype
    
        # define to send variable to other process
        new_img_shm = shared_memory.SharedMemory(create=True, size=np.prod(shape))
        is_stacking =mp.Value('i', 1) 
        is_ok=mp.Value('i', 1) 
        buf_event = mp.Event() 
        buf_event.clear()

        # start stack process
        p = mp.Process(target=self.stack_process, args=(new_img_shm, buf_event,self.stacked_buffer,is_stacking,is_ok),daemon=True)
        p.start()
        pre_num =  0
        while True:
            is_stacking.value = int(self.is_stacking)
            if is_stacking.value == 0 : 
                p.terminate()
                break
            #pre_numと現在のスタック数がおなじならスタックしない
            if is_ok.value == 0 :
                logger.debug(f"pre_num {pre_num} == num_stack {self.get_num_stack()}")
                logger.debug(f"Wating stackking process ")
                await asyncio.sleep(5)
                continue
            if len(self.new_image_buffer)>0:
                is_ok.value = 0
                logger.info("try stacking number %s",self.num_stacked+1)
                logger.debug("new images : %d",len(self.new_image_buffer))
                logger.debug("stacked image : %d ", len(self.stacked_buffer))
                buf_event.clear()
                new_img_buf = np.ndarray(shape, dtype=dtype, buffer=new_img_shm.buf)
                new_img_buf[:] = self.new_image_buffer.pop()
                buf_event.set()
                #len new images
                self.num_stacked = len(self.stacked_buffer)
                logger.debug(np.array(self.stacked_buffer[0]).mean().mean())


                # 
            print(is_ok.value)
            await asyncio.sleep(1)

        p.join()
        new_img_shm.close()
        new_img_shm.unlink()
        return
    def is_stackking(self):
        return self.is_stacking
    def get_num_stack(self):
        return len(self.stacked_buffer)
    def stack_process(self, new_img_shm, shm_event,buffer, is_stackking,is_ok ): 
        shape = buffer[0].shape
        dtype = buffer[0].dtype
        while True:
            if is_stackking.value == 0 : break
            shm_event.wait()
            new_img = np.ndarray(shape, dtype=dtype , buffer=new_img_shm.buf)
            shm_event.clear()

            self.stack(buffer,new_img)
            is_ok.value = 1



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

            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            cv2.imwrite(f"output/{now}.jpg",buffer[0])
            
        except Exception as e:
            logger.error(f"Faild to stack images  : {e} ")


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
            #logger.error("good is empty")
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

async def test_stack():
    import threading,time
    import pathlib
    import pprint
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
 



        

