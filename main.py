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


@app.route('/see_apointment/' , methods =['POST','GET'])
def see_apointment():
    checked_people  = list(checked.find({}))
    added_by_rec  = list(archives.find({}))
    return render_template('see_apointment.html' , ch = checked_people , ar = added_by_rec)

@app.route('/see_traf/')
def see_traf():
    
    
    
    return render_template('checked_in.html')
@app.route('/basic_data/' , methods = ['POST','GET'])
def basic_data():
    if request.method == "POST":
    
        name = request.form['name'].lower()
        home = request.form['town']
        id_no = request.form['id']
        height = request.form['height']
        weight = request.form['weight']
        tempa  = request.form['temps']
        now = datetime.now()
        now_c = now.strftime("Date  %Y:%m:%d: Time %H:%M:%S")
        archives.insert_one({"name" : name , "town" : home , "id_no" : id_no , "height" : height , 
                            "weight":weight , "Temparature" : tempa, "date" : now_c })
        
        return redirect(url_for('reception'))
    
    return render_template('basic_data.html')

@app.route('/reception/' , methods = ['POST','GET'])
def reception():
    posts = list(article_db.find({}))
    
    return render_template('reception.html' ,posts = posts)
@app.route('/patient', methods=['POST','GET'])
@login_required
def patient():
    posts = list(article_db.find({}))
    pat = session['loged_in']
    pats = users.find_one({'name' : pat})
    notifications = nots.find({}) 
    if request.method == 'POST':
        
        issued_patient = patient_backup.find_one({ 'name':pat})
        if issued_patient is not None:
            flash("Patient Found")
            drugs = issued_patient['Drugs_Prescribed']
            infecs = issued_patient['infections']
            timez = issued_patient['Time']
            id_no = issued_patient['id_no']

            return render_template('patient.html',ti = timez,d = drugs,name = pat,
            infects = infecs,ide = id_no,h1 = "   LOGGED IN AS",h2 = "DRUGS ISSUED",
            h3 = "TREATED INFECTIONS",h4 ="CONSOULTATION TIME : " , post = posts 
            , view = "Refresh Consultations" , notis = notifications )

    
    return render_template('patient.html' , post = posts , view = "View Former Consultations")
@app.route('/notifications/' , methods = ['POST','GET'])
@login_required
def notifications():
    logged = session['loged_in']
    user = users.find_one({"name" : logged})
    notifications = nots.find({})
    viewed = user["viewed"]
    notlist = list(notifications)
    for x in notlist:
        ids = x["not_id"]
        if ids in viewed:
            notlist.remove(x)
    if request.method == "POST":
            tar = request.form['rem']
            the_post  =  nots.find_one({"not_id" : tar})
            the_id = the_post["not_id"]
            the_arr = viewed
            if the_id in viewed:
                pass
            else: 
                the_arr.append(the_id)
            users.find_one_and_update({"name" : logged} ,{ '$set' :  {"viewed": the_arr}})
            return redirect(url_for('notifications'))
              
            
    
    return render_template('notifications.html' , nots = notlist)


@app.route('/doctor_dash/', methods=['POST','GET'])
@login_required
def doctor_dash():
    posts = list(article_db.find({}))
    
    
    return render_template('doctor_dash.html' , post = posts)

@app.route("/apo/" , methods = ["POST" , "GET"])
@login_required
def apo():
    logged = session['loged_in']
    user = users.find_one({"name" : logged})
    if request.method == 'POST':
        classif = request.form.get("dep")
        if classif == "1":
            car = "Minimal Sickness"
        if classif == "2":
            car = "Serious Sickness"
        if classif == "3":
            car = "Scheduled Clinic Visit"
        if classif == "4":
            car = "Injury"
        
        classif2 = request.form.get("de")
        if classif2 == "1":
            car2 = "Early Morning"
        if classif2 == "2":
            car2 = "Mid Morning"
        if classif2 == "3":
            car2 = "Noon"
        if classif2 == "4":
            car2 = "Evening"
        
     
        timein = time.asctime(time.localtime())
        check = mongo.db.check_in
        booked = check.find_one({"patient" : logged})
        if booked:
            return redirect(url_for('patient'))
        else:
            check.insert_one({'patient' : logged ,  'reason' : car , 'time_of_day' : car2 , 'time' :  timein })
    
        return redirect(url_for('checked_in'))
  
    return render_template('appoi.html')

    
    
@app.route("/checked_in/" , methods = ["POST" , "GET"])
def checked_in():
    def update_time():
        xy = time.localtime()
        ind = []
        for x in xy:
            ind.append(x)
        the_time = ind[3]
        if the_time == 0:
            today = int(ind[2])
            removal = list(checked.find({"day" : "Tommorrow"}))
            for v in removal:
                name = v['name']
                checked.find_one_and_update({"name":name} ,{ '$set' :  {"day":"Today"}})
            all_em = list(checked.find({}))
            for y in all_em:
                date = y['time']
                in_day = date[8:10]
                if in_day < today - 1: 
                    checked.find_one_and_delete({"time" : date})
        else:
            pass
    def llop():
        time.sleep(1)
        update_time()
    llop()
    checked_in = list(checked.find({}))
    maxno = 5
    no = checked.find({}).count()
    
    mo = checked.find({ "time_of_day" : "Early Morning"  }).count()
    
    mid = checked.find({ "time_of_day" : "Mid Morning"  }).count()
    
    noon = checked.find({ "time_of_day" : "Noon"  }).count()
    
    ev = checked.find({ "time_of_day" : "Evening"  }).count()
    #no = 129
   
    return render_template('checked_in.html' ,maxno = maxno , nos = no , ch = checked_in ,
                           mo = mo , mid = mid , noon = noon , ev = ev ,xy  = time.asctime(time.localtime()))

def update_time():
        xy = time.localtime()
        ind = []
        for x in xy:
            ind.append(x)
        the_time = ind[3]
        if the_time == 0:
            today = int(ind[2])
            removal = list(checked.find({"day" : "Tommorrow"}))
            for v in removal:
                name = v['name']
                checked.find_one_and_update({"name":name} ,{ '$set' :  {"day":"Today"}})
            all_em = list(checked.find({}))
            for y in all_em:
                date = y['time']
                in_day = date[8:10]
                if in_day < today - 1: 
                    checked.find_one_and_delete({"time" : date})
        else:
            pass
def llop():
    time.sleep(1)
    update_time()
llop()


@app.route('/add_a_patient/', methods=['POST','GET'])
@login_required
def add_a_patient():
    if request.method == 'POST':
        name = request.form['name']
        id_no = request.form['id']
        infec1 = request.form['infec1']
        infec2 = request.form['infec2']
        infec3 = request.form['infec3']
        drug_presc1 = request.form['drug_presc1']
        drug_presc2 = request.form['drug_presc2']
        drug_presc3 = request.form['drug_presc3']
        drug_presc4 = request.form['drug_presc4']
        que.insert_one({'name':name,'id_no':id_no,'infections':[infec1,infec2,infec3],
                        'Drug_Prescribed':[drug_presc1,drug_presc2,drug_presc3,drug_presc4]})
        if que.find_one({'name':name}):
            flash('Patient Information Updated')
            drug_arr = [drug_presc1,drug_presc2,drug_presc3,drug_presc4]
            prices = []
            for y in drug_arr:
                x  = invent.find_one({"name": y})
                if x:
                    dose = x['doses']
                    new_dose = dose - 1
                    invent.find_one_and_update({"name": y } ,{ '$set' :  {"doses":new_dose}}) 
                    price = int(x['cost'])
                    prices.append(price)
                    to = sum(prices)
   
            drug_db.insert_one({'name':name,'Drugs_Prescribed':[drug_presc1,drug_presc2,drug_presc3,drug_presc4] , "total" :to})
            login_time = time.asctime( time.localtime(time.time()) )
            patient_backup.insert_one({ 'Time':login_time,'name':name,'Drugs_Prescribed':[drug_presc1,
                                         drug_presc2,drug_presc3,drug_presc4], 
                                       'id_no':id_no,'infections':[infec1,infec2,infec3] })
            return redirect(url_for('doctor_dash'))
    return render_template('PatientInfo.html')
    
@app.route('/search_patient' ,methods = ['POST','GET'])
@login_required
def search_patient():
    sess = "Patient In Session"
    if request.method == "POST":
        name_in = request.form['patname']
        in_serach = drug_db.find_one({'name':name_in})
        if in_serach is None:
            return redirect(url_for('search_patient' ))
        else: 
            drug_arr= in_serach['Drugs_Prescribed']
            #infe_arr= in_serach['infections']
            return render_template('search_patient.html', sess = sess , drug_arr = drug_arr , name = name_in )
    return render_template('search_patient.html')

@app.route('/add_article' ,methods=['POST','GET'])
@login_required
def add_article():
    owner = session['loged_in']
    the_owner = users.find_one({'name' : owner})
    dep = the_owner['dep']  
    if request.method == "POST":       
        head = request.form['title']        
        
        title1 = request.form['subtitle_1']
        
        post1 = request.form['part1']
        
        title2 = request.form['subtitle_2']
        
        post2 = request.form['part2']
        
        title3 = request.form['subtitle_3']
        
        post3 = request.form['part3']
        
        title4 = request.form['subtitle_4']
        
        post4 = request.form['part4']
        
        title5 = request.form['subtitle_5']
        
        post5 = request.form['part5']
        
        
        existing = article_db.find_one({'name' :the_owner , "title" : head})
        if existing:
            try:
                if dep == "doctor":
                    return redirect(url_for('doctor_dash'))
            except pymongo.errors.ServerSelectionTimeoutError as err:
                print(err)
                redirect(url_for('db_err'))
            else:
                if dep == "chemist":
                    return redirect(url_for('chemist'))
        else:
            article_db.insert({"owner" : owner , "title" : head , "title1" : title1 , "post1" : post1 ,
                               "title2" : title2 ,  "post2" : post2 , 'title3' : title3 , "post3" : post3 ,
                               "title4" : title4 , "post4" : post4 ,"title5" : title5 , "post5" : post5  })
            try:
                if dep == "doctor":
                    return redirect(url_for('doctor_dash'))
            except pymongo.errors.ServerSelectionTimeoutError as err:
                print(err)
                redirect(url_for('db_err'))
            else:
                if dep == "chemist":
                    return redirect(url_for('chemist'))
    return render_template('add_article.html' , owner = owner)
@app.route('/chemist', methods=['POST','GET'])
@login_required
def chemist():
    posts = list(article_db.find({}))
    if request.method == 'POST':
        namein = request.form['patname']
        in_que = mongo.db.patient_que
        issued_patient = drug_db.find_one({ 'name':namein})
        if issued_patient is not None:
            drugs = issued_patient['Drugs_Prescribed']
            return render_template('chemist.html',d = drugs,name = namein,
                                   h1 = "PATIENT NAME : ",h2 = "DRUGS ISSUED" , post = posts)
        else:
            drugs = ["Patient Has No Drugs In Que" , "Please Check Name again"]
            return render_template('chemist.html' , d = drugs ,name = namein,
                                   h1 = "PATIENT NAME : ",h2 = "DRUGS ISSUED" , post = posts)
    return render_template('chemist.html' , post = posts )

@app.route('/dispense/' , methods=['POST' , 'GET'])
@login_required
def dispense():
    in_que = mongo.db.drugs
    patients  = list(in_que.find({}))
    if request.method == "POST":
        tar = request.form['rem']
        bill_method  =  request.form.get("de")
        t = in_que.find_one({"name" : tar})
        total = t['total']
        session['pr'] = total 
        session['usr'] = tar
        if bill_method == "1":
           return redirect(url_for('lipa_na_mpesa'))
        else:
            in_que.find_one_and_delete({"name": tar})
            return redirect(url_for('dispense'))
       
        

    return render_template('disp.html' ,  p =  patients )

@app.route('/',methods=['POST','GET'])
def index():
    session.pop('loged_in', None)
    if request.method == 'POST':
        login_user = users.find_one({'name' : request.form['username']})      
        if login_user:
            form_pass = request.form['pass'].encode('utf-8')
            if form_pass == "11111111":
                session['loged_in'] = request.form['username']
                return redirect(url_for('reset_passw'))
            else:
                hashed_pass = login_user['password']         
                if Hash_passcode.verify(form_pass,hashed_pass):
                    if login_user['dep'] == 'doctor':
                        session['loged_in'] = request.form['username']
                        return redirect(url_for('doctor_dash'))
                    if login_user['dep'] == 'patient':
                        session['loged_in'] = request.form['username']
                        return redirect(url_for('patient'))
                    if login_user['dep'] == 'chemist':
                        session['loged_in'] = request.form['username']
                        return redirect(url_for('chemist'))         
    return render_template('index.html')


@app.route('/login', methods=['POST','GET'])

def login():
    session.pop('loged_in', None)
    if request.method == 'POST':
        users = mongo.db.accounts
        login_user = users.find_one({'name' : request.form['username']})      
        if login_user:
            form_pass = request.form['pass'].encode('utf-8')
            if form_pass == "11111111":
                session['loged_in'] = request.form['username']
                return redirect(url_for('reset_passw'))
            else:
                hashed_pass = login_user['password']         
                if Hash_passcode.verify(form_pass,hashed_pass):
                    if login_user['dep'] == 'doctor':
                        session['loged_in'] = request.form['username']
                        return redirect(url_for('doctor_dash'))
                    if login_user['dep'] == 'patient':
                        session['loged_in'] = request.form['username']
                        return redirect(url_for('patient'))
                    if login_user['dep'] == 'chemist':
                        session['loged_in'] = request.form['username']
                        return redirect(url_for('chemist'))
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    session.pop('loged_in', None)
    if request.method == 'POST':
        users = mongo.db.accounts
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            passcode = request.form['pass'] 
            dep = "patient"
            email = request.form['email']
            hashpass = Hash_passcode.hash(passcode)
            user_id = random.randint(200 , 300)
            viewed = []
            users.insert_one({'name' : request.form['username'], 'password' : hashpass, "viewed" : viewed ,
                              "user_id" : user_id ,'dep':dep,'email':email})
            return redirect(url_for('index'))
        
        return 'That username already exists!'

    return render_template('register.html')
@app.route('/reset_passw' , methods=['POST','GET'])
@login_required
def reset_passw():
    if request.method == 'POST':
        logged =  session['loged_in']
        
        user_in = users.find_one({'name' : logged})
        
        old_pass = request.form['defau']
        
        new_pass1 = request.form['pass1']
        
        new_pass2 = request.form['pass2']
        
        if new_pass2 == new_pass1:
            if Hash_passcode.verify(old_pass , user_in['password']):
                new_password = Hash_passcode.hash(new_pass2)
                users.find_one_and_update({"name" : logged}  ,{ '$set' :  {"password": new_password}})
                return redirect (url_for('index'))
        else:
            return redirect(url_for('reset_passw' , mess =  "Passwords not Similler,Try again"))
    return render_template('reset_passw.html')
    
@app.route('/db_err' , methods=['POST','GET']) 
def db_err():
    return render_template('db_err.html')   
    
    return render_template('reset_passw.html')
ip = socket. gethostbyname(socket. gethostname())
ipst = str(ip)

#making Timestamp
now = datetime.now()
now_c = now.strftime("%Y%m%d%H%M%S")
new_time = str(now_c)
#mpesa variables
mpesa_api = MpesaAPI(app)
app.config["API_ENVIRONMENT"] = "sandbox"
app.config["APP_KEY"] = "TW1w1QUIjlIPu9Ig6xMEAVllxLqvlRby"  
app.config["APP_SECRET"] = "G5FpnkA7rdsvC4lw"
base_url =ipst + ":4000"
passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
bs_shortcode = '174379'
password = bs_shortcode + passkey + new_time
ret = base64.b64encode(password.encode())
pd = ret.decode('utf-8')

consumer_key = app.config["APP_KEY"]
consumer_secret = app.config["APP_SECRET"]

api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

def mpesa_token():
    mpesa_auth_url = ' https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    verify = (requests.get(mpesa_auth_url, auth = HTTPBasicAuth(consumer_key , consumer_secret))).json()
    tok = verify['access_token']
    return tok

@app.route('/' , methods=["POST"])
def home():
    
    return "Welcome home"

@app.route('/home2/' , methods=["GET" ,"POST"])
def home2():
    '''
    headers = {"Authorization" : "Bearer %s" %mpesa_token(),
                'Content-Type': 'application/json'
                }
    '''
    headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer pUZYReswbylV4QAONIwBc18fxU0T'
    }
    payload = {
    "BusinessShortCode": 174379,
    "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjIwMTA0MTEwMDEx",
    "Timestamp": "20220104110011",
    "CheckoutRequestID": "ws_CO_040120221134452840",
    }
   
    response_from_auth = requests.post('https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query',json=payload,headers=headers)
   
    return response_from_auth.text.encode('utf8')
    
    
@app.route('/pay/' , methods=['GET', "POST" ])
def pay():
    age = 10
    if 10 == age:
            tok = mpesa_token()
            return render_template('tok.html' , tok = tok)
    
    return render_template('tok.html')

@app.route('/lipa_na_mpesa/' , methods = ['GET' ,'POST'])
def lipa_na_mpesa():   
    in_que = mongo.db.drugs
    tar = session['usr']
    def do_pay(number):
        amount = session['pr']
        #amount =  400
        headers = {"Authorization" : "Bearer %s" %mpesa_token(),
                    'Content-Type': 'application/json'
                    }
        
        reuest = {
        "BusinessShortCode": bs_shortcode,
        "Password": pd,
        "Timestamp": new_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": number,
        "PartyB": bs_shortcode,
        "PhoneNumber": number,
        "CallBackURL": "https://b437-197-248-246-149.ngrok.io/",
        "AccountReference": "Monte Carlo Hos",
        "TransactionDesc": "ARVs" 
    }
     
        response_from_auth = requests.post(api_url,json=reuest,headers=headers)
            
        if response_from_auth.status_code > 299:
                return{
                        "code" : response_from_auth.status_code ,
                        "success": False,
                        "message":"Sorry, something went wrong please try again later."
                    },400
            
        else:
             data_back = {
                    "data": json.loads(response_from_auth.text)
                },200
             in_que.find_one_and_delete({"name": tar})
             return redirect(url_for('success' , data = data_back))
         
    if request.method == 'POST':
        number = int(request.form['no'])
        return redirect('http://localhost:4000/lipa_na_mpesa/')
        #do_pay(number = number)    
         
    return render_template('bill.html')

@app.route('/success/' ,methods = ['POST','GET'])
def success():
    
    
    
    return render_template('suc.html')

if __name__ == '__main__':
    app.secret_key = 'private_tings'
    app.run(debug=True,port=5008)