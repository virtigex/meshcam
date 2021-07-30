from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import shutil
import subprocess
import tempfile
import time

hostName = ""
hostPort = 80

dir = tempfile.mkdtemp()
cap_file = os.path.join(dir, 'cam.jpg')


def get_image(file):
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

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        image = None
        if get_image(cap_file):
            with open(cap_file, mode='rb') as file:
                image = file.read()
            os.unlink(cap_file)

        if image is not None:
            self.send_response(200)
            self.send_header("Content-type", 'image/jpg') # jpeg?
            self.end_headers()
            self.wfile.write(image)
        else:
            self.send_error(500)

myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))

