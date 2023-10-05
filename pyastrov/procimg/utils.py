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
    _, encoded = cv2.imencode(".jpg", img)
    return bytes_to_base64(encoded)

def save_img(  array : np.array):
    ''' input image array must be BGR '''

    frame = cv2.imdecode(array,cv2.IMREAD_UNCHANGED)
    now = datetime.now()
    cv2.imwrite(f"./output/{now.strftime('%Y%m%d_%H%M%S')}.tiff",frame)
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
def cvt_color( array : np.array, color : str = "RGB"):
    if color == "RGB":
        return cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
    elif color == "BGR":
        return cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
    elif color == "GRAY":
        return cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)
    else:
        raise Exception("Invalid Color")


def exec_clahe(img):
    ''' img must be BGR'''

    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB) 
    lab_planes =list( cv2.split(lab)) 
    clahe = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
    lab_planes[0] = clahe.apply(lab_planes[0]) 
    lab = cv2.merge(lab_planes) 
    bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR) 
    return bgr
def adjust_rgb(image):
    avg_b = np.mean(image[:, :, 0])
    avg_g = np.mean(image[:, :, 1])
    avg_r = np.mean(image[:, :, 2])

    # 補正係数を計算
    k_b = avg_g / avg_b
    k_r = avg_g / avg_r

    # 各チャンネルに補正係数を適用
    corrected_image = np.zeros_like(image, dtype=np.float32)
    corrected_image[:, :, 0] = image[:, :, 0] * k_b
    corrected_image[:, :, 1] = image[:, :, 1]
    corrected_image[:, :, 2] = image[:, :, 2] * k_r

    # ピクセル値が255を超えないようにクリップ
    corrected_image = np.clip(corrected_image, 0, 255).astype(np.uint8)
    return corrected_image
def adjust_gamma(image,gamma=0.3):


    corrected_image = (image/255)**(1 / gamma) * 255
    

    return corrected_image