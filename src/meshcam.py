from http.server import BaseHTTPRequestHandler, HTTPServer
import cv2
import os
import shutil
import subprocess
import tempfile
import time

host_name = ""
host_port = 80
source = 0
cv2cap = None

dir = tempfile.mkdtemp()
cap_file = os.path.join(dir, 'cam.jpg')

def get_picam_image(file):
    cmd = [ '/usr/bin/raspistill' ]
    cmd.append('-n')        # no ui
    cmd.append('-q')
    cmd.append('20')
    cmd.append('-rot')
    cmd.append('180')
    cmd.append('-t')
    cmd.append('1')
    cmd.append('-o')
    cmd.append(file)
    res = subprocess.run(cmd)
    return res.returncode == 0

def get_usbcam_image():
    ret, frame = cv2cap.read()
    if not ret:
        return None
    return cv2.imencode('.jpg', frame)[1].tobytes()

class MeshCam(BaseHTTPRequestHandler):
    def do_GET(self):
        image = None
        if source == None:
            if get_picam_image(cap_file):
                with open(cap_file, mode='rb') as file:
                    image = file.read()
                os.unlink(cap_file)
        else:
            image = get_usbcam_image()

        if image is not None:
            self.send_response(200)
            self.send_header("Content-type", 'image/jpg') # jpeg?
            self.end_headers()
            self.wfile.write(image)
        else:
            self.send_error(500)

if __name__ == '__main__':
    server = HTTPServer((host_name, host_port), MeshCam)
    print(time.asctime(), "Server Starts - %s:%s" % (host_name, host_port))
    if source is not None:
        cv2cap = cv2.VideoCapture(source)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    if cv2cap is not None:
        cv2cap.release()

    server.server_close()
    print(time.asctime(), "Server Stops - %s:%s" % (host_name, host_port))

