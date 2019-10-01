import os
from flask import Flask, flash, request, redirect, url_for, render_template, Response
from werkzeug.utils import secure_filename
import filerelated
from Hole import Hole
import io
import random   
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import datetime
from camera import VideoCamera
import json

import serial_rx_tx

serialPort = serial_rx_tx.SerialPort()

# serial data callback function
def OnReceiveSerialData(message):
    str_message = message.decode("utf-8")
    print("COM:%s"%(str_message))
    

# Register the callback above with the serial port object
serialPort.RegisterReceiveCallback(OnReceiveSerialData)

comport = "/dev/ttyACM1"
baudrate = "115200"
serialPort.Open(comport,baudrate)



ALLOWED_EXTENSIONS = set(['drl', 'txt', 'xln'])
global toolCollection
toolCollection = dict()
toolDict = dict()
tool = dict()
holes = []
holeCount = dict()
currentTool = -1

# min @ max for X & Y
global minX 
minX = 999
global maxX
maxX = -999
global minY
minY = 999
global maxY
maxY = -999

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
#UPLOAD_FOLDER = os.path.join(os.getcwd(), UPLOAD_FOLDER)
instancePath = os.path.dirname(app.instance_path)
print(" instance path : " + instancePath)

UPLOAD_FOLDER = instancePath +  '/uploads'

print("dest dir " + UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#set colours
colordict = { 1: "black", 2:"red", 3:"saddlebrown",
    4:"darkorange",5:"olivedrab",6:"green",
    7:"darkcyan",8:"dodgerblue",9:"blue",
    10:"darkviolet",11:"magenta",12:"crimson"}


def processFile(filepath):

    #locals
    percentageFound = False
    metricFound = False

    global holeNum
    holeNum = 0

    f=open(filepath, "r")
    if f.mode == 'r':
        contents = f.readlines()
        # get tools
        for l in contents:
            if(l.startswith("METRIC")):
                metricFound = True
            if(l.startswith("%")):
                percentageFound = True
            if(metricFound == True and percentageFound == False and l.startswith("T")):
                # get tool size
                parts = l[1:].split("C")
                toolDict[int(parts[0])] = float(parts[1])
            if(percentageFound == True and l.startswith("T")):
                #toolchange
                currentTool = int(l[1:])
            if(percentageFound == True and l.startswith("X")):
                # found a hole
                parts = l[1:].split("Y")
                xpart = float(parts[0])/1000
                ypart = float(parts[1])/1000
                filePoint = xpart, ypart
                holeNum = holeNum + 1
                holes.append(Hole(holeNum, filePoint, currentTool))
                if currentTool in holeCount:
                    holeCount[currentTool] = holeCount[currentTool] + 1
                else:
                    holeCount[currentTool] = 1
            if(percentageFound== True and l.startswith("M30")):
                break
        f.close()

        # create ToolCollection
        for t in toolDict:
            tool = dict()
            tool["toolNum"] = int(t)
            tool["size"] = float(toolDict[t])
            tool["holeCount"] = holeCount[int(t)]
            tool["color"] = colordict[int(t)]
            toolCollection[int(t)] = tool
            print(toolCollection[int(t)])

        #print(toolCollection)
        for c in toolCollection:
            #print(toolCollection[c])
            td = toolCollection[c]
            print("Tool %d : %3.3f, %d holes"% (c, td['size'], td['holeCount']) )
        
        print("--------------------------------")
        print(json.dumps(toolCollection))

        # get min & Max
        global minX 
        global maxX
        global minY
        global maxY
        for h in holes:

            if(h.filePoint[0] < minX):
                minX = h.filePoint[0]
            if(h.filePoint[0] > maxX):
                maxX = h.filePoint[0]
            if(h.filePoint[1] < minY):
                minY = h.filePoint[1]
            if(h.filePoint[1] > maxY):
                maxY = h.filePoint[1]
        print("Completed getting Min & Max")
        # flip & zero
        for h in holes:
            h.translateAndFlipHole(minY, maxY, minX )
        print("Holes translated & flipped")
        global maxDistance
        global h0
        global h1
        maxDistance = -999.999
        for ha in holes[:-1]:
            for hb in holes[1:]:
                # get distance between ha & hb 
                dist = ((hb.zeroedAndFlippedPoint[0]- ha.zeroedAndFlippedPoint[0])**2 + (hb.zeroedAndFlippedPoint[1]- ha.zeroedAndFlippedPoint[1])**2)**0.5
                if(dist > maxDistance):
                    maxDistance = dist
                    h0 = ha
                    h1 = hb


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            global filepath
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print("#######################################")
            print("FilePath : " + filepath)
            print("#######################################")
            try:
                os.remove(filepath)
            except:
                pass
            file.save(filepath)
            # read file 
            print("About to process file....")
            processFile(filepath)
            return redirect(url_for('uploaded_file', filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    
    '''


from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    for t in toolCollection:
        td = toolCollection[t]
        print(td)
    return render_template('index.html', toolCollection=toolCollection)

@app.route('/fill_table')
def fill_table():

    #retVal = "<table border=1 border-collapse=collapse><tr><th>#</th><th>size</th><th>count</th><th>colour</th></tr>"
    #for t in toolCollection:
    #    td = toolCollection[t]
    #    retVal += "<tr><td>%d</td><td>%3.3f</td><td>%d</td><td bgcolor='%s'>&nbsp</td></tr>"% (t, td["size"], td["holeCount"],td["color"])
    #retVal += "</table>"
    return render_template('index.html', toolCollection = toolCollection)

@app.route('/plot_png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    print("plotting")
    return Response(output.getvalue(), mimetype='image/png')

@app.route('/get_coms')
def get_coms():
    serialPort.Send("?")
    serialPort.Send("$J=G91 X10 Y10 F300")
    serialPort.Send("?")

    return "nothing"
def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

def create_figure():
    print("creating Figure.........")
    cnt = 0
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    #fig = plt.figure(figsize=(10,8))
    
    for h in holes:
        if(cnt < 260):
            px = h.zeroedAndFlippedPoint[0]
            py = h.zeroedAndFlippedPoint[1] 
            axis.plot(px, py, color=colordict[h.toolNum],markersize=toolDict[h.toolNum]*2 ,marker='o')
            cnt += 1
        else:
            break
        font = {'family': 'serif',
            'color':  'darkred',
            'weight': 'normal',
            'size': 16,
            }
    #axis.set_title("Max Distance : %3.3f "% (maxDistance))
    # plot max Line
    #axis.add_line(Line2D(line1_xs, line1_ys, linewidth=2, color='blue'))
    axis.plot( h0.zeroedAndFlippedPoint, h1.zeroedAndFlippedPoint, linewidth=2, color='red')

        #axis.text(x=20,y=20,text='Hello World Time is : ' + str(datetime.datetime.now()),s=1, color='black', font )
            
    #fig = Figure()
    #axis = fig.add_subplot(1, 1, 1)
    #xs = range(100)
    #ys = [random.randint(1, 50) for x in xs]
    #axis.plot(xs, ys)
    return fig