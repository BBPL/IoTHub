from flask import render_template,request
from app import app,db
from app.models import Satellite
import json
import pychromecast
from pychromecast.controllers.youtube import YouTubeController
import spotify_token
import spotipy
import spotipy.util as util

CHROMECASTS = pychromecast.get_chromecasts()
print("Done loading CCs")
CC_NAME = "TT"


@app.route("/")
def hello():
    return ("Hello world")


@app.route("/music/play", methods=['POST'])
def play():
    if not ccReady():
        return "Chromecast not found"

    mc, _ = getMediaController()
    
    json = request.json
    
    if 'url' not in json or not json['url'].endswith(".mp3"):
        return "You must provide url to an mp3 file"

    time = 0
    if 'time' in json:
        time = json['time']

    # current time must be set to be able to seek music later
    mc.play_media(json['url'], 'audio/mp3', current_time = time)
    
    return "success"

@app.route("/music/update", methods=['POST'])
def update():
    if not ccReady():
        return "Chromecast not found"

    mc, cast = getMediaController()

    json = request.json

    if 'time' in json:
        mc.seek(json['time'])

    if 'volume' in json:
        cast.set_volume(json['volume'])

    return "success"

@app.route("/music/pause", methods=['POST'])
def pause():
    if not ccReady():
        return ("Chromecast not found")

    mc, _ = getMediaController()

    mc.pause()

    return "success"

@app.route("/home/<string:name>", methods=['POST', 'GET'])
def home(name):
    s = Satellite.query.filter(Satellite.name == name)
    if not s.first():
        return render_template("home.html", name="fuck")
    return render_template("home.html", name=s.first().name)


@app.route("/connect/<string:ip>/<int:port>/<string:name>")
def connectSatellite(ip,port,name):
    s = Satellite.query.filter(Satellite.ip == ip).filter(Satellite.port == port)
    if not s.first(): #if no results found
        satellite = Satellite(ip=ip,port=port,name=name)
        db.session.add(satellite)
        db.session.commit()
        return("added!")
    return("nope!")
        
@app.route("/connect",methods=['POST','GET'])
def connect():
    print(request.method)

    if request.method == 'POST':
        return connectPOST(request)
    elif request.method == 'GET':
        return connectGET(request)
    else:
        return render_template('home.html',name="marek")

def connectPOST(request):
    if not request.json:
        return "wrong"
    print(request.json)
    return json.dumps(request.json)
def connectGET(request):
    return request.method

def ccReady():
    if len(CHROMECASTS) == 0:
        return False
    casts = [cc for cc in CHROMECASTS if cc.device.friendly_name == CC_NAME]
    if len(casts) == 0:
        return False
    return True

def getMediaController():
    cast = next(cc for cc in CHROMECASTS if cc.device.friendly_name == CC_NAME)
    cast.wait()
    return cast.media_controller, cast
