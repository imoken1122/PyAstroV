import base64
import cv2
import numpy as np
import datetime
from pyastrov.camera.interface import ControlType, ImgType, ROIFormat ;

def to_ndarray(buf: list[int], img_type : ImgType):
    bit_t = np.uint8
    match img_type:
        case ImgType.RAW8:
            bit_t = np.uint8
        case ImgType.RAW16:
            bit_t = np.uint16
        case _:
            raise Exception("Invalid Image Type")
    return np.frombuffer(buf,dtype=bit_t)

def buf_to_img( buf : list, width : int , height : int,img_type : ImgType = ImgType.RAW8):
    arr = to_ndarray(buf,img_type).reshape(height,width)
    img = debayer(arr)
    return img
def get_img_for_flet( buf : list ,width : int , height : int,img_type:ImgType = ImgType.RAW8) -> str : 
    img = buf_to_img(buf, width, height)
    _, encoded = cv2.imencode(".png", img)
    return bytes_to_base64(encoded)

def save_img( path : str, array : np.array):
    ''' input image array must be BGR '''

    frame = cv2.imdecode(array,cv2.IMREAD_UNCHANGED)
    now = datetime.now()
    cv2.imwrite(f"{now.strftime('%Y%m%d_%H%M%S')}.png",frame)
def bytes_to_base64(buf:bytes):
    return base64.b64encode(buf).decode('ascii')

def base64_to_bytes( encoded:str):
    return base64.b64decode(encoded)

def debayer( array : np.array, pattern : str = "GR"):
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
