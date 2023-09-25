
from camera_device.mock import MockCamera, num_mock_camera
from camera_device.svbony import SVBCamera,get_num_svb_camera
import base64

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
        print(get_num_svb_camera())
        n_svb = get_num_svb_camera()
        n_mock = num_mock_camera()
        if n_svb > 0:
            for i in n_svb:
                self.devices.append(SVBCamera(i))
                self.is_captures.append(False)
            print("SVB Camera is conected")

        elif n_mock > 0: 
            self.devices.append(MockCamera())

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
        roi["img_type"] = imt
        return roi.to_dict()

    def set_roi_i(self,idx : int, contents : dict):
        self.devices[idx].set_roi(**contents)

    def get_ctrl_value_i(self,idx : int, contents) -> dict:
        
        ctrl_value = self.devices[idx].get_control_value(contents["ctrl_type"])
        return ctrl_value.to_dict()

    def set_ctrl_value_i(self,idx : int, contents):
        self.devices[idx].set_control_value(**contents)

    def start_capture_i(self,idx : int):
        self.devices[idx].start_capture()

    def get_frame_i(self,idx : int):
        frame = self.devices[idx].get_frame()
        return {"frame" : self.to_base64(frame)}

    def to_base64(self,frame):
        return base64.b64encode(frame).decode(ascii)

    def stop_capture_i(self,idx : int):
        self.devices[idx].stop_capture()

    def store_to_buf(self,idx : int):
        pass