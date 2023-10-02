import flet as ft
from camera.mqtt.api import MQTTCameraAPI
from ui.app import run_ui 
class AstroVCore:
    camera_api : MQTTCameraAPI
    # telescope_api : TelescopeAPI
    # stellarium_api : StellariumAPI
    def __init__(self, camera_api : MQTTCameraAPI):
        self.camera_api = camera_api

        run_ui() 

    def init(self):
        self.camera_api.init()