
from abc import *
from dataclasses import dataclass
from enum import Enum

class ImgType(Enum):
    RAW8 =0,
    RAW16 =1,
    RGB24 =2 
class ControlType(Enum):
    GAIN = 0
    EXPOSURE = 1
    GAMMA = 2
    GAMMA_CONTRAST = 3
    WB_R = 4
    WB_G = 5
    WB_B = 6
    FLIP = 7
    FRAME_SPEED_MODE = 8
    CONTRAST = 9
    SHARPNESS = 10
    SATURATION = 11
    AUTO_TARGET_BRIGHTNESS = 12
    BLACK_LEVEL = 13
    COOLER_ENABLE = 14
    TARGET_TEMPERATURE = 15
    CURRENT_TEMPERATURE = 16
    COOLER_POWER = 17

   

@dataclass
class CameraInfo:
    name : str
    idx : int
    max_width : int
    max_height : int
    supported_img_type : list[ImgType] 
    supported_bins : list[int]
    is_coolable : bool


@dataclass
class ROIFormat:
    startx : int
    starty : int
    width : int
    height : int
    bin : int
    img_type : ImgType


@dataclass
class ControlCaps:
    '''Capability of each ControlType'''
    name: str
    max_value: int
    min_value: int
    default_value: int
    is_auto_supported: int
    is_writable: int
    control_type: int

@dataclass
class CameraAPI(metaclass=ABCMeta):
    ''' abstract class for Camera Interface'''
    @abstractmethod
    def get_num_camera(self) -> int:
        pass
    @abstractmethod
    def get_info_i(self,idx : int) -> CameraInfo:
        pass
    @abstractmethod
    def init(self):
        pass
    @abstractmethod
    def start_capture_i(self):
        pass
    @abstractmethod
    def stop_capture_i(self):
        pass
    @abstractmethod
    def get_roi_i(self) -> ROIFormat:
        pass
    @abstractmethod
    def set_roi_i(self,bin : int):
        pass
    @abstractmethod
    def get_ctrl_value_i(self,control_type : ControlType):
        pass
    @abstractmethod
    def set_ctrl_value_i(self,control_type : ControlType,value : int,is_auto : int):
        pass
    @abstractmethod
    def get_frame_i(self):
        pass
