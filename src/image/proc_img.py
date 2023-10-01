import base64
import cv2
import numpy as np
from camera.interface import ControlType, ImgType, ROIFormat ;

class ImageProcessor : 
    def __init__(self) -> None:
        pass

    def to_ndarray(self,buf: list[int], img_type : ImgType):
        bit_t = np.uint8
        match img_type:
            case ImgType.RAW8:
                bit_t = np.uint8
            case ImgType.RAW16:
                bit_t = np.uint16
            case _:
                raise Exception("Invalid Image Type")
        return np.frombuffer(buf,dtype=bit_t)
    
    def buf_to_img(self, buf : list, width : int , height : int):
        arr = self.to_ndarray(buf).reshape(height,width)
        img = self.debayer(arr)
        return img
    def to_flet_img(self, buf : list ) -> str : 
        img = self.buf_to_img(buf)
        _, encoded = cv2.imencode(".png", img)
        return self.bytes_to_base64(encoded)

    def save_image(self, path : str, array : np.array):
        ''' input image array must be BGR '''
        cv2.imwrite(path, array)

    def bytes_to_base64(self,buf:bytes):
        return base64.b64encode(buf).decode('ascii')
    
    def base64_to_bytes(self, encoded:str):
        return base64.b64decode(encoded)

    def debayer(self, array : np.array, pattern : str = "GR"):
        if pattern == "RG":
            return cv2.cvtColor(array, cv2.COLOR_BayerRG2BGR)
        elif pattern == "GR":
            return cv2.cvtColor(array, cv2.COLOR_BayerGR2BGR)
        elif pattern == "GB":
            return cv2.cvtColor(array, cv2.COLOR_BayerGB2BGR)
        elif pattern == "BG":
            return cv2.cvtColor(array, cv2.COLOR_BayerBG2BGR)
        else:
            raise Exception("Invalid Bayer Pattern")
    