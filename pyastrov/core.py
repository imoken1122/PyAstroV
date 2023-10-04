import flet as ft
from .camera.mqtt.api import MQTTCameraAPI
from pyastrov.procimg.stack import ImageStacker


class StateManager:
    def __init__(self,):
        self.states = {}

    def set(self, var_name : str, value : any):
        self.states[var_name] = value

    def get(self,var_name : str):
        return self.states[var_name]
    def contains(self,var_name : str):
        return var_name in self.states.keys()
class AstroVCore:

    camera_api : MQTTCameraAPI
    state_manager : StateManager
    stacker : ImageStacker
    # telescope_api : TelescopeAPI
    # stellarium_api : StellariumAPI
    def __init__(self, camera_api = MQTTCameraAPI):
        self.camera_api = camera_api 
        self.state_manager = StateManager()
        self.stacker = ImageStacker()




