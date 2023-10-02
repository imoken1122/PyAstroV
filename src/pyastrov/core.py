import flet as ft
from .camera.mqtt.api import MQTTCameraAPI
class AstroVCore:
    camera_api : MQTTCameraAPI
    # telescope_api : TelescopeAPI
    # stellarium_api : StellariumAPI
    def __init__(self, camera_api = MQTTCameraAPI):
        self.camera_api = camera_api 

