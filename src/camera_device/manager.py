
from camera_device.mock import MockCamera, num_mock_camera
from camera_device.svbony import SVBCamera,get_num_svb_camera
import base64
from dataclasses import asdict
from mqtt.camera_cli.interface import ControlType, ImgType, ROIFormat
class CameraManager : 
    frame_buffer = []
    conected_camera : list[str]=[]
    devices = []
    is_captures = []
    def __init__ (self):
        self.num_camera = 0 
        self.conected_camera=[]
        self.is_captures = []

    def connect(self):
        n_svb = get_num_svb_camera()
        n_mock = num_mock_camera()
        if n_svb > 0:
            self.devices += [SVBCamera(i) for i in range(n_svb) ]
            self.is_captures.append(False)
            print("SVB Camera is conected")

        if n_mock > 0: 
            self.devices += [MockCamera(i) for i in range(n_mock) ]

            self.is_captures.append(False)
            print("Mock Camera is conected")
        else:
            raise Exception("No camera device found")

        self.num_camera = len(self.devices)



    def get_info_i(self,idx : int) -> dict:
        info = self.devices[idx].get_info()
        return info.to_dict()

    def get_roi_i(self,idx : int) -> dict:
        roi = self.devices[idx].roi
        imt = self.devices[idx].img_type
        roi_d = asdict(roi)
        roi_d["img_type"] = str(imt.name)
        return roi_d

    def set_roi_i(self,idx : int, contents : dict):
        contents["img_type"] = ImgType[contents["img_type"]]
        self.devices[idx].set_roi(**contents)

    def get_ctrl_value_i(self,idx : int, contents) -> dict:
        
        ctrl_type = ControlType[contents["ctrl_type"]]
        ctrl_value = self.devices[idx].get_control_value(ctrl_type)
        return asdict(ctrl_value)

    def set_ctrl_value_i(self,idx : int, contents):
        contents["ctrl_type"] = ControlType[contents["ctrl_type"]]
        self.devices[idx].set_control_value(**contents)

    def start_capture_i(self,idx : int):
        self.devices[idx].start_capture()

    def get_frame_i(self,idx : int):
        frame = self.devices[idx].get_frame()
        return {"frame" : self.to_base64(frame)}

    def to_base64(self,frame):
        return base64.b64encode(frame).decode("ascii")

    def stop_capture_i(self,idx : int):
        self.devices[idx].stop_capture()

    def store_to_buf(self,idx : int):
        pass