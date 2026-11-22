
from __future__ import division, print_function

from pymongo import MongoClient
import sys
import os
import glob
import numpy as np

# Keras

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Flask utils
from flask import Flask, request, render_template,jsonify,json
from werkzeug.utils import secure_filename

os.environ["CUDA_VISIBLE_DEVICES"]="-1"
# Define a flask app


app = Flask(__name__)



client = MongoClient('mongodb+srv://mongodb.net/')
db = client['demo5']
collection = db['data5']
# initialize the app with the extension



# Model saved with Keras model.save()
MODEL_PATH = 'models/modelres50.h5'

#Load your trained model
model = load_model(MODEL_PATH)
#model._make_predict_function()          
print('Model loaded. Start serving...')



@app.route('/add_data', methods=['POST'])
def add_data():
    # Get data from request
    print(request.form.get("email"))
    em = {"first-name": request.form.get("first-name"),
          "last-name": request.form.get("last-name"),
          "email": request.form.get("email"),
          "password": request.form.get("password")       
          }
    json.dumps(em)
    # data = request.json
  
    # Insert data into MongoDB
    collection.insert_one(em)
  
    return render_template("index.html")


def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(200,200)) 

    # Preprocessing the image
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = img.astype('float32')/255
   
    preds = model.predict(img)

   
   
    pred = np.argmax(preds,axis = 1)
    return pred


@app.route('/', methods=['GET'])
def home():
    # Main page
    return render_template('home.html')


@app.route('/index', methods=['GET'])
def index():
    # Main page
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login():
    # Login Page
    return render_template('login.html')
    
@app.route('/auth', methods=['POST'])
def auth():
    uemail = request.form.get("email")
    upassword = request.form.get("password")
    email_found = collection.find_one({"email":uemail})
    

    if email_found:
        email_val = email_found['email']
        passwordcheck = email_found['password']
        if uemail == email_val and upassword == passwordcheck:
            return render_template("index.html")
        else:
            return render_template("register.html")
    else:
            return render_template("register.html")

    # if db.collection.find({"email":{uemail}}) and db.collection.find({"password":{upassword}}):
    #     return render_template("index.html")
    # else:
    #     return render_template("register.html")
    # return "hi"

@app.route('/register', methods=['GET'])
def register():
    # register page
    return render_template('register.html')


@app.route('/predict', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the file from post request
        f = request.files['file']

        # Save the file to ./uploads
        basepath = os.path.dirname(__file__)
        file_path = os.path.join(
            basepath, 'uploads', secure_filename(f.filename))
        f.save(file_path)

        # Make prediction
        pred = model_predict(file_path, model)
        os.remove(file_path)

        
        str0 = 'Glioma'
        str1 = 'Meningioma'
        str3 = 'pituitary'
        str2 = 'No Tumour'
        if pred[0] == 0:
            return str0
        elif pred[0] == 1:
            return str1
        elif pred[0]==3:
            return str3
        else:
            return str2
    return None

    
if __name__ == '__main__':
        app.run(debug=True, host="localhost", port=8080)
   
