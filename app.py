from flask import Flask, redirect, render_template, request
#Import Libraries
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
#Import the local route for this application
import os
import requests
from geopy.geocoders import Nominatim

def ipInfo(addr=''):
    from urllib.request import urlopen
    from json import load
    if addr == '':
        url = 'https://ipinfo.io/json'
    else:
        url = 'https://ipinfo.io/' + addr + '/json'
    res = urlopen(url)
    #response from url(if res==None then check connection)
    data = load(res)
    try:
        return data["loc"]
    except:
        pass


def get_ip():
    response = requests.get('https://api64.ipify.org?format=json').json()
    return response["ip"]


def get_location():
    ip_address = get_ip()
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name")
    }
    return location_data["ip"]


#Configure App
app = Flask(__name__, template_folder="templates", static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    date = db.Column(db.DateTime, default = datetime.utcnow)
    title = db.Column(db.String(200), nullable = False)
    description = db.Column(db.String(400), nullable = False)
    name = db.Column(db.String(100), nullable = False)
    coords = db.Column(db.String)

    def __repr__(self):
        return '<Description %r>' %self.id

'''
Create Database
with app.app_context():
    db.create_all()
'''

@app.route('/', methods = ["POST", "GET"])
def index():
    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']
        name = request.form['name']
        ip = ipInfo(get_location())

        new_post = Location(title = title, description = content, name = name, coords = ip)
    
        db.session.add(new_post)
        db.session.commit()
        return redirect("/")

        
    else:
        locations = Location.query.order_by(Location.date.desc()).all()
        return render_template('index.html', locations = locations)

if __name__ == "__main__":
    app.run(debug=True)