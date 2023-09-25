

import uvicorn

from fastapi import FastAPI, Request
from starlette.responses import StreamingResponse
from manager import CameraManager
import io
app = FastAPI()

cm =  CameraManager()
cm.conect_camera()

@app.get("/")
async def main():
    return {"message": "Hello World"}
@app.get("/stream_frame")
async def stream_frame_i(camera_idx : int = 0):
    #return StreamingResponse(get_frame(camera_idx),    media_type='multipart/x-mixed-replace; boundary=frame')
    return StreamingResponse(get_frame(camera_idx),   media_type='image/jpeg')

def get_frame(camera_idx : int = 0):
    camera = cm.devices[camera_idx]
    camera.start_capture()
    while True:
        encoded_frame = camera.get_frame().tobytes()
        print(type(encoded_frame))
        yield encoded_frame 


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)