import re
from flask_pymongo import PyMongo
import pymongo
import passlib
from passlib.context import CryptContext
from passlib.hash import argon2, bcrypt_sha256,argon2,ldap_salted_md5,md5_crypt
import time
import smtplib
import random


from flask import  Flask, request , json , render_template,redirect,jsonify , redirect , url_for , request, redirect,flash,session
import requests
from datetime import datetime
import flask_mpesa
import socket
import base64
from requests.auth import HTTPBasicAuth
from flask_mpesa import MpesaAPI
from functools import wraps


app = Flask(__name__)

#login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if "loged_in" in session:
            return f(*args,**kwargs,)
        else:
            time.sleep(2)
            return redirect(url_for('index'))
    return wrap


#log in session pop function
def pop_session(x):
    @wraps(x)
    def wrap(*args,**kwargs):
        if  not "loged_in" in session:
            return x(*args,**kwargs)
        else:
            session.pop('loged_in', None)
    return wrap

        

app.config['MONGO_DBNAME'] = 'main_db'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/main_db'
mongo = PyMongo(app)
#HASH sCHEMES
Hash_passcode = CryptContext(schemes="sha256_crypt",sha256_crypt__min_rounds=131072)
username_hash = CryptContext(schemes=["sha256_crypt","argon2"])
#databases
users = mongo.db.accounts
doctor_db = mongo.db.doctors
patient_db = mongo.db.patients
drug_db = mongo.db.drugs
nurse_db = mongo.db.nurses
chemist_db = mongo.db.chemists
patient_backup = mongo.db.patient_backup
article_db = mongo.db.articles
nots = mongo.db.notifications
que = mongo.db.patient_que
checked = mongo.db.check_in
invent = mongo.db.inventory
archives = mongo.db.archives



@app.route('/' , methods = ['POST' , 'GET'] )
def index():
    
    
    
    
    return render_template('index.html')

@app.route('/see_apointment/' , methods =['POST','GET'])
def see_apointment():
    
    checked_people  = list(checked.find({}))
    added_by_rec  = list(archives.find({}))

    
    return render_template('see_apointment.html' , ch = checked_people , ar = added_by_rec)





@app.route('/about/' , methods =['POST','GET'])
def about():
    

    
    return render_template('about.html')





@app.route('/contact/' , methods =['POST','GET'])
def contact():
    

    
    return render_template('contact.html')





@app.route('/donation/' , methods =['POST','GET'])
def donation():
    

    
    return render_template('donation.html')







@app.route('/opd/' , methods =['POST','GET'])
def opd():
    

    
    return render_template('opd.html')


@app.route('/patinet_care/' , methods =['POST','GET'])
def patient_care():
    

    
    return render_template('patient_care.html' )



@app.route('/thanks_for_donation/' , methods =['POST','GET'])
def thanks_for_donation():
    

    
    return render_template('thanks_for_donation.html' )




@app.route('/donation_succ/' , methods =['POST','GET'])
def donation_succ():
    

    
    return render_template('donation_succ.html')

@app.route('/specialist/' , methods =['POST','GET'])
def specialist():
    

    
    return render_template('specialist.html')

@app.route('/faq/' , methods =['POST','GET'])
def faq():
    

    
    return render_template('faq.html')



@app.route('/career/' , methods =['POST','GET'])
def career():
    

    
    return render_template('career.html')


@app.route('/Donate_Mpesa/' , methods =['POST','GET'])
def Donate_Mpesa():
    
    
    
    return render_template('bill.html')


if __name__ == '__main__':
    app.secret_key = 'private_tings'
    app.run(debug=True,port=5006)