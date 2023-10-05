from pyastrov.procimg import utils 
import numpy as np
from multiprocessing import Process, Manager, shared_memory
import multiprocessing as mp
class ImageProcessor : 
    def __init__(self,):
        pass

    def run(self, img : np.ndarray, params : dict) -> np.ndarray:
        shm = shared_memory.SharedMemory(create=True, size=np.prod(img.shape))
        event = mp.Event()
        event.clear()

        p = mp.Process(target=self.cvt_image, args=(shm, event, img, params),daemon=True)
        p.start()
        event.wait()
        img_buf = np.ndarray(img.shape, dtype=img.dtype, buffer=shm.buf)
        event.clear()
        p.join()
        shm.close()
        shm.unlink()
        return img_buf
    
    def cvt_image(self, shm, event,img : np.ndarray, params : dict) -> np.ndarray:

        img = utils.ctrl_gamma(img,params["gamma"]).astype(img.dtype)
        img= utils.ctrl_saturation(img,params["saturation"])
        img = utils.ctrl_rgb(img,params["r"],params["g"],params["b"])

        img_buf = np.ndarray(img.shape, dtype=img.dtype, buffer=shm.buf)
        event.clear()
        img_buf[:] = img
        event.set()

