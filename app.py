#%%
#!/usr/bin/env python
#
# sudo apt-get install libilmbase-dev
# sudo apt-get install libopenexr-dev
# sudo apt-get install libgstreamer1.0-dev
# sudo apt-get install python3-picamera

import os, sys, json, argparse, math
import cv2
import numpy as np
from flask import Flask, request, render_template, Response, jsonify
from camera_pi import Camera
import serial
sys.path.insert(0, os.path.abspath(''))

parser = argparse.ArgumentParser()

parser.add_argument('-debug', action='store_true',help='Debug server')
parser.add_argument('-image_size', type=json.loads, default='[144, 176]', help='Training crop size [height, width]/  [90, 160],[120, 160],[120, 160], [144, 176],[288, 352], [240, 432],[480, 640],[576,1024],[720, 960], [720,1280],[1080, 1920]')
parser.add_argument('-image_depth', type=int, default=3, help='Number of input colors.  1 for grayscale, 3 for RGB') 

FLAGS, unparsed = parser.parse_known_args()

config = {
      'input_shape': [FLAGS.image_size[0], FLAGS.image_size[1], FLAGS.image_depth],
      'area_filter_min': 250,
      'size_divisible': 32,
      'port':'/dev/ttyUSB0',
      }

app = Flask(__name__)
global ser
ser = {}

def GetPort(port_name='/dev/ttyUSB0'):
    try:
        port = serial.Serial(port_name)  # open serial port
    except:
        port = None
        print ('serial port {} unavailable'.format(port))
    return port

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def gen(camera):
    """Video streaming generator function."""

    while True:
        img = camera.get_frame()
        [height, width, depth] = img.shape

        # encode as a jpeg image and return it
        frame = cv2.imencode('.jpg', img)[1].tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/set',methods = ['POST'])
def set():
    global ser
    json_data = request.json
    #Moving forward code
    if 'speed' in json_data:
        writeString = '01{:04d}\n'.format(int(json_data['speed']))
        print(writeString)
        if not ser:
            ser = GetPort(config['port'])
        if ser:
            ser.write(writeString.encode())
        else:
            print("No serial port")
    if 'direction' in json_data:
        writeString = '02{:04d}\n'.format(int(json_data['direction']))
        print(writeString)
        if not ser:
            ser = GetPort(config['port'])
        if ser:
            ser.write(writeString.encode())
        else:
            print("No serial port")    
    return jsonify(isError= False,
                   message= "Success",
                   statusCode= 200,
                   data= 0), 200

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera(config)), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    FLAGS, unparsed = parser.parse_known_args()

    if FLAGS.debug:
        # https://code.visualstudio.com/docs/python/debugging#_remote-debugging
        # Launch applicaiton on remote computer: 
        # > python3 -m ptvsd --host 0.0.0.0 --port 3000 --wait predict_imdb.py
        import ptvsd
        # Allow other computers to attach to ptvsd at this IP address and port.
        ptvsd.enable_attach(address=('0.0.0.0', 3000), redirect_output=True)
        # Pause the program until a remote debugger is attached
        print("Wait for debugger attach")
        ptvsd.wait_for_attach()
        print("Debugger Attached")

    ser = GetPort(config['port'])
    app.run(host='0.0.0.0', threaded=True)
