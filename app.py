# Importing essential libraries and modules

from flask import Flask, flash, redirect, render_template, request, session, url_for
import numpy as np
import pandas as pd
from markupsafe import Markup
#from utils.disease import disease_dic
from utils.fertilizer import fertilizer_dic
import requests
import config   
import pickle
import io
import torch
from torchvision import transforms
from PIL import Image
from utils.model import ResNet9
import mysql.connector 


# =========================================================================================

# Custom functions for calculations


# def weather_fetch(city_name):
#     """
#     Fetch and returns the temperature and humidity of a city
#     :params: city_name
#     :return: temperature, humidity
#     """
#     api_key = config.weather_api_key
#     base_url = "http://api.openweathermap.org/data/2.5/weather?"

#     complete_url = base_url + "appid=" + api_key + "&q=" + city_name
#     response = requests.get(complete_url)
#     x = response.json()

#     if x["cod"] != "404":
#         y = x["main"]

#         temperature = round((y["temp"] - 273.15), 2)
#         humidity = y["humidity"]
#         return temperature, humidity
#     else:
#         return None



# ===============================================================================================
# ------------------------------------ FLASK APP -------------------------------------------------


app = Flask(__name__)

app.secret_key = 'your_secret_key'
# database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Yash@1469",
    database="mydatabase"
)

# render home page
@app.route('/', methods=['GET', 'POST'])
def login():    
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']

    cursor = db.cursor()
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    if user:
        session['logged_in'] = True
        session['username'] = username
        return render_template('index.html')
    else:
        return "Login failed. Invalid credentials."

@ app.route('/home')
def home():
    title = 'AgriNexus - Home'
    return render_template('index.html', title=title)

# render fertilizer recommendation form page
@app.route('/logout')
def logout():
    
    if 'logged_in' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))
    
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))


@ app.route('/fertilizer')
def fertilizer_recommendation():
    title = 'AgriNexus - Fertilizer Suggestion'
    return render_template('fertilizer.html', title=title)

@app.route('/crop_recommend')
def crop_recommend():
    return render_template('crop_recommend.html')

@ app.route('/fertilizer-predict', methods=['POST'])
def fert_recommend():
    title = 'AgriNexus - Fertilizer Suggestion'

    crop_name = str(request.form['cropname'])
    N = int(request.form['nitrogen'])
    P = int(request.form['phosphorous'])
    K = int(request.form['pottasium'])
    # ph = float(request.form['ph'])

    df = pd.read_csv('Data/fertilizer.csv')

    if not crop_name:
        return render_template('fertilizer.html', title=title, message='Please choose a crop first.')
     
     # Check if the crop exists in the CSV file
    if crop_name not in df['Crop'].values:
        return render_template('fertilizer.html', title=title, message='Crop not found in the database. Please choose a valid crop.')

    nr = df[df['Crop'] == crop_name]['N'].iloc[0]
    pr = df[df['Crop'] == crop_name]['P'].iloc[0]
    kr = df[df['Crop'] == crop_name]['K'].iloc[0]

    n = nr - N
    p = pr - P
    k = kr - K
    temp = {abs(n): "N", abs(p): "P", abs(k): "K"}
    max_value = temp[max(temp.keys())]
    if max_value == "N":
        if n < 0:
            key = 'NHigh'
        else:
            key = "Nlow"
    elif max_value == "P":
        if p < 0:
            key = 'PHigh'
        else:
            key = "Plow"
    else:
        if k < 0:
            key = 'KHigh'
        else:
            key = "Klow"

    response = Markup(str(fertilizer_dic[key]))

    return render_template('fertilizer-result.html', recommendation=response, title=title)


if __name__ == '__main__':
    app.run(debug=True)