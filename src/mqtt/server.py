
import time
import numpy as np
import json
import base64
import threading
from mqtt_config import MQTTBase, CameraCmd, formatter,CameraTopics
from camera_device.manager import CameraManager

'''
msg = {
    "camera_idx" : 0,
    "method" : get/set,
    "contents" : {}
}
'''



class MQTTCameraServer(MQTTBase):
    def __init__(self):
        super().__init__()
        self.camera_manger = CameraManager()
        self.camera_manger.connect()
        self.thread_states = {}

    def on_message(self, mqttc, obj, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        pkt= json.loads(msg.payload.decode())
        camera_idx = pkt["camera_idx"]
        cmd = pkt["cmd"]
        contents=  json.loads(pkt["contents"])

        match cmd:
            case CameraCmd.GetStatus.value:
                #publish status
                return
            case CameraCmd.GetRoi.value:

                res = self.camera_manger.get_roi_i(camera_idx)

            case CameraCmd.SetRoi.value:
                self.camera_manger.set_roi_i(camera_idx, contents)
                return


            case CameraCmd.GetCtrlVal.value:
                res  = self.camera_manger.get_ctrl_value_i(camera_idx)

            case CameraCmd.SetCtrlVal.value:
                #　control type = exposure or gain の場合、露光中だったら start captureしなおす
                self.camera_manger.set_ctrl_value_i(camera_idx,contents)
                return
                
            case CameraCmd.StartCapture.value:
                def get_frame_thread(thread_stop_flag):
                    while not thread_stop_flag.is_set():
                        res = self.camera_manger.get_frame_i(camera_idx)
                        res = formatter(camera_idx, cmd, res)
                        self.publish_single(CameraTopics.Responce.value, res)


                self.camera_manger.start_capture_i(camera_idx)

                stop_flag_i = threading.Event()
                th_i = threading.Thread(target=get_frame_thread,args=(stop_flag_i, ))
                th_i.start()

                self.thread_states[camera_idx] = [th_i,stop_flag_i]
                return


            case CameraCmd.StopCapture.value:

                if camera_idx not in self.thread_states:
                    print(f"camera_idx : {camera_idx} not in thread_states")
                    return

                print(f"stop capture, {camera_idx} join thread")
                self.camera_manger.stop_capture_i(camera_idx)

                th_i,stop_flag_i = self.thread_states[camera_idx]
                stop_flag_i.set()
                th_i.join()

                return 


            case CameraCmd.GetInfo.value:

                res = self.camera_manger.get_info_i(camera_idx)

            case CameraCmd.GetProps.value:
                res = self.camera_manger.get_props_i(camera_idx)

            case _:
                pass


        res = formatter(camera_idx, cmd, res)
        self.publish_single(CameraTopics.Responce.value, res)

    def run(self):
        self.start_subscribe(CameraTopics.Instr.value)
        self.loop_forever()


if __name__ == "__main__":
    mqttc = MQTTCameraServer()
    mqttc.run()