from flask import Flask, render_template, request, url_for, session, redirect, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pickle
import pandas as pd
import pandas as pd
import re 
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
import pickle
import h5py
import numpy as np # linear algebra
import pandas as pd  

from sklearn.feature_extraction.text import CountVectorizer
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.metrics import AUC
from sklearn.model_selection import train_test_split


import re
import pickle
app = Flask(__name__)
# read object TfidfVectorizer and model from disk
stress = pickle.load(open('stress.pkl','rb'))

app.secret_key = 'neha'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'feedback'
mysql = MySQL(app)

@app.route('/',methods = ['GET','POST'])
def first():
    return render_template('first.html')
@app.route('/performance') 
def performance():
	return render_template('performance.html')
 
  
@app.route('/loginad') 
def loginad():
	return render_template('loginad.html')
    
@app.route('/upload') 
def upload():
	return render_template('upload.html') 
@app.route('/preview',methods=["POST"])
def preview():
    if request.method == 'POST':
        dataset = request.files['datasetfile']
        df = pd.read_csv(dataset,encoding = 'unicode_escape')
        df.set_index('Id', inplace=True)
        return render_template("preview.html",df_view = df)


@app.route('/login', methods = ['GET',"POST"])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student WHERE username = %s AND password = %s', (username, password))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            global Id
            session['Id'] = account['Id']
              
            Id = session['Id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('index'))
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password! Please login with correct credentials')
            return redirect(url_for('login'))
    # Show the login form with message (if any)

    return render_template('login.html', msg=msg)

@app.route('/register',methods= ['GET',"POST"])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'collegename' in request.form and 'degree' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        collegename = request.form['collegename']
        degree = request.form['degree']
        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,10}$"
        pattern = re.compile(reg)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Check if account exists using MySQL)
        cursor.execute('SELECT * FROM student WHERE Username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not re.search(pattern,password):
            msg = 'Password should contain atleast one number, one lower case character, one uppercase character,one special symbol and must be between 6 to 10 characters long'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into employee table
            cursor.execute('INSERT INTO student VALUES (NULL, %s, %s, %s, %s, %s)', (username, email, password,collegename,degree))
            mysql.connection.commit()
            flash('You have successfully registered! Please proceed for login!')
            return redirect(url_for('login'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
        return msg
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

@app.route('/index')
def index():
 	return render_template("index.html")

@app.route('/predict',methods=['POST'])
def predict():
     if request.method == 'POST':    
        
        gender=request.form['gender']
        if gender=='0':
             gen='Male'
        elif gender=='1':
             gen='Female'     
        financial_issues=request.form['financial_issues']
        if financial_issues=='0':
             fin ='None'
        elif financial_issues=='1':
              fin ='Repay Loan Issues;Deadline of Fee payment'   
        elif financial_issues=='2':
              fin ='Payment for Hostel'
        elif financial_issues=='3':
              fin ='Repay Loan Issues'
        elif financial_issues=='4':
              fin ='Deadline of Fee paymen'
        elif financial_issues=='5':
              fin ='Deadline of Fee payment;Payment for Hostel'
        elif financial_issues=='6':
              fin ='Repay Loan Issues;Deadline of Fee payment;Payment for Hostel'   
        elif financial_issues=='7':
              fin ='Payment for room rent'
        elif financial_issues=='8':
              fin ='Family loan'
        elif financial_issues=='9':
              fin ='Repay Loan Issues;Payment for Hostel'
                                          
        family_issues=request.form['family_issues']
        if family_issues == '0':
             fam = 'None'
        elif family_issues == '1':
             fam = 'Parental Expectations'
        elif family_issues == '2':
             fam = 'Parental Expectations;Poor Communication and misunderstandings'
        elif family_issues == '3':
             fam = 'Parental Expectations;Being bullied by siblings'
        elif family_issues == '4':
             fam = 'Poor Communication and misunderstandings' 
        elif family_issues == '5':
             fam = 'Parental Expectations;Poor Communication and misunderstandings;Negligence of Children'
        elif family_issues == '6':
             fam = 'Parental Expectations;Internal family dispute'
        elif family_issues == '7':
             fam = 'Poor Communication and misunderstandings;Negligence of Children'
        elif family_issues == '8':
             fam = 'Parental Expectations;Negligence of Children' 
        elif family_issues == '9':
             fam = 'Negligence of Children'
        elif family_issues == '10':
             fam = 'Parental Expectations;Divorce of Parents'                
        elif family_issues == '11':
             fam = 'Being bullied by siblings'
        elif family_issues == '12':
             fam = 'Divorce of Parents;Poor Communication and misunderstandings'
        elif family_issues == '13':
             fam = 'Being bullied by siblings;Divorce of Parents;Poor Communication and misunderstandings'
        elif family_issues == '14':
             fam = 'Parental Expectations;Being bullied by siblings;Divorce of Parents' 
        elif family_issues == '15':
             fam = 'Divorce of Parents;Negligence of Children'
        elif family_issues == '16':
             fam = 'Divorce of Parents;Poor Communication and misunderstandings;Negligence of Children'
        elif family_issues == '17':
             fam = 'Being bullied by siblings;Poor Communication and misunderstandings;Negligence of Children'
        elif family_issues == '18':
             fam = 'Parental Expectations;Divorce of Parents;Negligence of Children' 
        elif family_issues == '19':
             fam = 'Parental Expectations;Being bullied by siblings;Poor Communication and misunderstandings'
        elif family_issues == '20':
             fam = 'Being bullied by siblings;Poor Communication and misunderstandings'              
        elif family_issues == '21':
             fam = 'Being bullied by siblings;Negligence of Children'
        elif family_issues == '22':
             fam = 'Being bullied by siblings;Divorce of Parents;Negligence of Children'
        elif family_issues == '23':
             fam = 'Parental Expectations;Divorce of Parents;Poor Communication and misunderstandings'
        elif family_issues == '24':
             fam = 'Parental Expectations;Being bullied by siblings;Divorce of Parents;Negligence of Children' 
        elif family_issues == '25':
             fam = 'Parental Expectations;Being bullied by siblings;Negligence of Children'
        elif family_issues == '26':
             fam = 'Being bullied by siblings;Divorce of Parents'
        elif family_issues == '27':
             fam = 'Parental Expectations;Being bullied by siblings;Divorce of Parents;Poor Communication and misunderstandings;Negligence of Children'
        elif family_issues == '28':
             fam = 'Parental Expectations;Being bullied by siblings;Divorce of Parents;Poor Communication and misunderstandings' 
        elif family_issues == '29':
             fam = 'Divorce of Parents'
        elif family_issues == '30':
             fam = 'Internal family dispute'              
        elif family_issues == '31':
             fam = 'Poor Communication'
                 

        
        study_hours=request.form['study_hours']
        

        health_issues=request.form['health_issues']
        if health_issues == '0':
             health = 'None'
        elif health_issues == '1':
             health = 'Anxiety or Tension'
        elif health_issues == '2':
             health = 'Insomnia (Sleep Deprivation);Low Energy;Anxiety or Tension;Sleeping Problem;Concentration Problem'  
        elif health_issues == '3':
             health = 'Concentration Problem'  
        elif health_issues == '4':
             health = 'Sinus or Migraine or Headaches;Insomnia (Sleep Deprivation);Anxiety or Tension;Lonliness;Sleeping Problem;Concentration Problem'  
        elif health_issues == '5':
             health = 'Anxiety or Tension;Sleeping Problem'
        elif health_issues == '6':
             health = 'Sinus or Migraine or Headaches;Low Energy;Anxiety or Tension;Lonliness;Concentration Problem'
        elif health_issues == '7':
             health = 'Insomnia (Sleep Deprivation);Low Energy;Anxiety or Tension;Concentration Problem'  
        elif health_issues == '8':
             health = 'Sinus or Migraine or Headaches;Insomnia (Sleep Deprivation);Low Energy;Lonliness;Sleeping Problem;Concentration Problem'  
        elif health_issues == '9':
             health = 'Insomnia (Sleep Deprivation);Low Energy;Anxiety or Tension;Lonliness;Sleeping Problem;Concentration Problem'  
        elif health_issues == '10':
             health = 'Insomnia (Sleep Deprivation);Anxiety or Tension;Sleeping Problem' 
        elif health_issues == '11':
             health = 'Insomnia (Sleep Deprivation);Low Energy;Anxiety or Tension;Lonliness'
        elif health_issues == '12':
             health = 'Sinus or Migraine or Headaches;Anxiety or Tension;Sleeping Problem'  
        elif health_issues == '13':
             health = 'Sinus or Migraine or Headaches;Insomnia (Sleep Deprivation);Anxiety or Tension'  
        elif health_issues == '14':
             health = 'Sinus or Migraine or Headaches;Covid;Low Energy;Sleeping Problem'  
        elif health_issues == '15':
             health = 'Insomnia (Sleep Deprivation);Low Energy;Anxiety or Tension'
        elif health_issues == '16':
             health = 'Sinus or Migraine or Headaches;Covid;Insomnia (Sleep Deprivation);Low Energy'
        elif health_issues == '17':
             health = 'Malnutrition;Covid;Anxiety or Tension'  
        elif health_issues == '18':
             health = 'Sinus or Migraine or Headaches;Anxiety or Tension'  
        elif health_issues == '19':
             health = 'Malnutrition;Insomnia (Sleep Deprivation)'  
        elif health_issues == '20':
             health = 'Covid;Anxiety or Tension;Concentration Problem'             
        elif health_issues == '21':
             health = 'Insomnia (Sleep Deprivation);Anxiety or Tension;Lonliness'
        elif health_issues == '22':
             health = 'Insomnia (Sleep Deprivation);Anxiety or Tension'  
        elif health_issues == '23':
             health = 'Sinus or Migraine or Headaches;Insomnia (Sleep Deprivation)'  
        elif health_issues == '24':
             health = 'Insomnia (Sleep Deprivation);Lonliness'  
        elif health_issues == '25':
             health = 'Insomnia (Sleep Deprivation);Anxiety or Tension;Concentration Problem'
        elif health_issues == '26':
             health = 'Covid;Low Energy;Lonliness'
        elif health_issues == '27':
             health = 'Malnutrition'  
        elif health_issues == '28':
             health = 'Sinus or Migraine or Headaches;Low Energy;Lonliness'  
        elif health_issues == '29':
             health = 'Malnutrition;Low Energy;Sleeping Problem'  
        elif health_issues == '30':
             health = 'Covid;Anxiety or Tension'             
        elif health_issues == '31':
             health = 'Sinus or Migraine or Headaches;Low Energy'
        elif health_issues == '32':
             health = 'Sinus or Migraine or Headaches;Covid;Insomnia (Sleep Deprivation);Sleeping Problem'  
        elif health_issues == '33':
             health = 'Covid;Concentration Problem'  
        elif health_issues == '34':
             health = 'Low Energy;Sleeping Problem'  
        elif health_issues == '35':
             health = 'Sleeping Problem'
        elif health_issues == '36':
             health = 'Malnutrition;Sinus or Migraine or Headaches;Covid'
        elif health_issues == '37':
             health = 'Covid;Low Energy;Sleeping Problem'  
        elif health_issues == '38':
             health = 'Covid;Anxiety or Tension;Sleeping Problem'  
        elif health_issues == '39':
             health = 'Covid;Insomnia (Sleep Deprivation);Low Energy'  
        elif health_issues == '40':
             health = 'Covid;Low Energy;Concentration Problem'             
        elif health_issues == '41':
             health = 'Malnutrition;Anxiety or Tension;Sleeping Problem'
        elif health_issues == '42':
             health = 'Malnutrition;Insomnia (Sleep Deprivation);Low Energy;Anxiety or Tension'  
        elif health_issues == '43':
             health = 'Malnutrition;Insomnia (Sleep Deprivation);Lonliness;Concentration Problem'  
        elif health_issues == '44':
             health = 'Malnutrition;Covid;Lonliness'  
        elif health_issues == '45':
             health = 'Malnutrition;Insomnia (Sleep Deprivation);Lonliness'
        elif health_issues == '46':
             health = 'Covid;Lonliness'
        elif health_issues == '47':
             health = 'Malnutrition;Insomnia (Sleep Deprivation);Sleeping Problem'  
        elif health_issues == '48':
             health = 'Anxiety or Tension;Lonliness;Concentration Problem'  
        elif health_issues == '49':
             health = 'Lonliness'  
        elif health_issues == '50':
             health = 'Anxiety or Tension;Lonliness;Sleeping Problem;Concentration Problem'             
        elif health_issues == '51':
             health = 'Sinus or Migraine or Headaches;Covid;Insomnia (Sleep Deprivation);Low Energy;Lonliness;Sleeping Problem;Concentration Problem'
        elif health_issues == '52':
             health = 'Insomnia (Sleep Deprivation);Anxiety or Tension;Lonliness;Concentration Problem'  
        elif health_issues == '53':
             health = 'Covid;Insomnia (Sleep Deprivation);Anxiety or Tension;Sleeping Problem;Concentration Problem'  
        elif health_issues == '54':
             health = 'Covid;Insomnia (Sleep Deprivation);Anxiety or Tension;Sleeping Problem'  
        elif health_issues == '55':
             health = 'Sinus or Migraine or Headaches;Insomnia (Sleep Deprivation);Anxiety or Tension;Sleeping Problem'
        elif health_issues == '56':
             health = 'Sinus or Migraine or Headaches;Insomnia (Sleep Deprivation);Sleeping Problem'
        elif health_issues == '57':
             health = 'Low Energy;Lonliness'  
        elif health_issues == '58':
             health = 'Sinus or Migraine or Headaches;Low Energy;Anxiety or Tension'  
        elif health_issues == '59':
             health = 'Sinus or Migraine or Headaches;Insomnia (Sleep Deprivation);Lonliness'  
        elif health_issues == '60':
             health = 'Insomnia (Sleep Deprivation);Low Energy'             
        elif health_issues == '61':
             health = 'Sinus or Migraine or Headaches;Covid;Insomnia (Sleep Deprivation);Anxiety or Tension;Lonliness;Sleeping Problem;Concentration Problem'
        elif health_issues == '62':
             health = 'alnutrition;Covid;Low Energy'  
        elif health_issues == '63':
             health = 'Sinus or Migraine or Headaches;Insomnia (Sleep Deprivation);Lonliness;Concentration Problem'  
        elif health_issues == '64':
             health = 'Covid;Low Energy;Anxiety or Tension'  
        elif health_issues == '65':
             health = 'Covid;Insomnia (Sleep Deprivation);Low Energy;Sleeping Problem'
        elif health_issues == '66':
             health = 'Low Energy;Lonliness;Sleeping Problem'
        elif health_issues == '67':
             health = 'Sinus or Migraine or Headaches;Insomnia (Sleep Deprivation);Low Energy;Sleeping Problem'  
        elif health_issues == '68':
             health = 'Covid;Low Energy;Lonliness;Sleeping Problem'  
        elif health_issues == '69':
             health = 'Sinus or Migraine or Headaches;Insomnia (Sleep Deprivation);Low Energy'  
        elif health_issues == '70':
             health = 'Malnutrition;Anxiety or Tension'             
        elif health_issues == '71':
             health = 'Low Energy;Lonliness;Concentration Problem'
        elif health_issues == '72':
             health = 'Sinus or Migraine or Headaches;Covid;Low Energy;Anxiety or Tension'  
        elif health_issues == '73':
             health = 'Covid;Insomnia (Sleep Deprivation);Low Energy;Anxiety or Tension;Lonliness;Sleeping Problem;Concentration Problem'  
        elif health_issues == '74':
             health = 'Sinus or Migraine or Headaches;Covid;Insomnia (Sleep Deprivation);Concentration Problem'  
        elif health_issues == '75':
             health = 'Malnutrition;Insomnia (Sleep Deprivation);Low Energy;Anxiety or Tension;Lonliness'
        elif health_issues == '76':
             health = 'Sinus or Migraine or Headaches;Covid;Insomnia (Sleep Deprivation);Low Energy;Lonliness'
        elif health_issues == '77':
             health = 'Covid;Insomnia (Sleep Deprivation)'  
        elif health_issues == '78':
             health = 'Sinus or Migraine or Headaches;Covid;Anxiety or Tension'  
        elif health_issues == '79':
             health = 'Covid;Lonliness;Sleeping Problem'  
        elif health_issues == '80':
             health = 'Sinus or Migraine or Headaches;Low Energy;Sleeping Problem'             
        elif health_issues == '81':
             health = 'Covid;Anxiety or Tension;Lonliness'
        elif health_issues == '82':
             health = 'Sinus or Migraine or Headaches;Lonliness'  
        elif health_issues == '83':
             health = 'Sinus or Migraine or Headaches;Covid;Sleeping Problem'  
        elif health_issues == '84':
             health = 'Low Energy;Anxiety or Tension;Concentration Problem'  
        elif health_issues == '85':
             health = 'Sinus or Migraine or Headaches;Sleeping Problem'
        elif health_issues == '86':
             health = 'Covid;Low Energy;Anxiety or Tension;Sleeping Problem'
        elif health_issues == '87':
             health = 'Insomnia (Sleep Deprivation);Low Energy;Lonliness'  
        elif health_issues == '88':
             health = 'Covid;Low Energy;Anxiety or Tension;Concentration Problem'  
        elif health_issues == '89':
             health = 'Sinus or Migraine or Headaches'  
        elif health_issues == '90':
             health = 'Sleeping Problem;Concentration Problem'    
        elif health_issues == '91':
             health = 'Low Energy'         
                                  


        friends_issues=request.form['friends_issues']
        if friends_issues == '0':
             friend = 'None'
        elif friends_issues == '1':
             friend = 'Comparison between them' 
        elif friends_issues == '2':
             friend = 'Mistrust' 
        elif friends_issues == '3':
             friend = 'Jealousy;Mistrust' 
        elif friends_issues == '4':
             friend = 'Betrayal' 
        elif friends_issues == '5':
             friend = 'Comparison between them;Jealousy'
        elif friends_issues == '6':
             friend = 'Conflicts' 
        elif friends_issues == '7':
             friend = 'Conflicts;Comparison between them;Betrayal' 
        elif friends_issues == '8':
             friend = 'Jealousy' 
        elif friends_issues == '9':
             friend = 'Comparison between them;Mistrust' 
        elif friends_issues == '10':
             friend = 'Conflicts;Comparison between them;Jealousy' 
        elif friends_issues == '11':
             friend = 'Conflicts;Comparison between them;Mistrust' 
        elif friends_issues == '12':
             friend = 'Comparison between them;lack of deep communication' 
        elif friends_issues == '13':
             friend = 'friendly' 
        elif friends_issues == '14':
             friend = 'Jealousy;Betrayal' 
        elif friends_issues == '15':
             friend = 'Conflicts;Jealousy'
        elif friends_issues == '16':
             friend = 'Conflicts;Comparison between them' 
        elif friends_issues == '17':
             friend = 'Comparison between them;Jealousy;Mistrust' 
        elif friends_issues == '18':
             friend = 'Conflicts;Jealousy;Betrayal' 
        elif friends_issues == '19':
             friend = 'Comparison between them;Betrayal' 
        elif friends_issues == '20':
             friend = 'Mistrust;Betrayal'            
        elif friends_issues == '21':
             friend = 'Conflicts;Comparison between them;Jealousy;Mistrust;Betrayal' 
        elif friends_issues == '22':
             friend = 'Jealousy;Mistrust;Betrayal' 
        elif friends_issues == '23':
             friend = 'Conflicts;Mistrust' 
        elif friends_issues == '24':
             friend = 'Comparison between them;Jealousy;Betrayal' 
        elif friends_issues == '25':
             friend = 'Comparison between them;Mistrust;Betrayal'
        elif friends_issues == '26':
             friend = 'Conflicts;Jealousy;Mistrust' 
        elif friends_issues == '27':
             friend = 'Comparison between them;Jealousy;Mistrust;Betrayal' 
        elif friends_issues == '28':
             friend = 'Conflicts;Jealousy;Mistrust;Betrayal' 
                                                            
        
        friends_time=request.form['friends_time']
        overload=request.form['overload']
        if overload == '0':
             over = 'No'
        elif overload ==  '1':
             over = 'Yes'     
        unpleasant=request.form['unpleasant']
        if unpleasant == '0':
             unp = 'No'
        elif unpleasant ==  '1':
             unp = 'Yes' 
        academic=request.form['academic']
        if academic == '0':
             acade = 'No'
        elif academic ==  '1':
             acade = 'Yes' 
        career=request.form['career']
        if career == '0':
             car = 'No'
        elif career ==  '1':
             car = 'Yes' 
        criticism=request.form['criticism']
        if criticism == '0':
             cri = 'No'
        elif criticism ==  '1':
             cri = 'Yes' 
        conflicts=request.form['conflicts']
        if conflicts == '0':
             con = 'No'
        elif conflicts ==  '1':
             con = 'Yes' 
          
        input_variables = pd.DataFrame([[gender,financial_issues,family_issues,study_hours,health_issues,friends_issues,friends_time,overload,unpleasant,academic,career,criticism,conflicts]],
                                       columns=['gender','financial_issues','family_issues','study_hours','health_issues','friends_issues','friends_time','overload', 'unpleasant','academic','career', 'criticism','conflicts'],
                                       dtype=float,
                                       index=['input'])
        print(input_variables)
        prediction = stress.predict(input_variables)[0]
        if prediction == 0:
              pred= "Normal"
        elif prediction == 1:
              pred="Stressed"
        elif prediction == 2:
              pred="Highly Stressed"

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO review(gender,financial_issues,family_issues,study_hours,health_issues,friends_issues,friends_time,overload,unpleasant,academic,career,criticism,conflicts,pred,userid) VALUES (%s,%s,%s,%s,%s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ", (gen,fin,fam,study_hours,health,friend,friends_time,over,unp,acade,car,cri,con,pred,Id))
         
        mysql.connection.commit()
        cur.close()
        return redirect('/users')
     return render_template('index.html') 


@app.route('/users')
def users():
     
    cur = mysql.connection.cursor()
    resultValue = cur.execute(" SELECT * from student INNER JOIN review ON student.ID = review.USERID;")
     
    if resultValue > 0:
        userDetails = cur.fetchall()
         
        return render_template('users.html',userDetails=userDetails)  

@app.route('/admin')
def admin():
    cur = mysql.connection.cursor()
    resultValue = cur.execute(" SELECT * from student INNER JOIN review ON student.ID = review.USERID;")
     
    if resultValue > 0:
        userDetails = cur.fetchall()
         
        return render_template('admin.html',userDetails=userDetails)  
@app.route('/userdetail')
def userdetail():  
   cur = mysql.connection.cursor()      
   cur.execute("SELECT * from student")
   useradmin=cur.fetchall()
   print(useradmin)
       
   return render_template('userdetail.html',useradmin=useradmin) 


@app.route('/chart3')
def chart3():
    legend = "review by pred"
    cursor = mysql.connection.cursor()
    
    try:
        cursor.execute("SELECT pred from review GROUP BY pred")
        # data = cursor.fetchone()
        rows = cursor.fetchall()
        labels = list()
        i = 0
        for row in rows:
            labels.append(row[i])
        
        cursor.execute("SELECT COUNT(id) from review GROUP BY pred")
        rows = cursor.fetchall()
        # Convert query to objects of key-value pairs
        values = list()
        i = 0
        for row in rows:
            values.append(row[i])
        cursor.close()
         
        
    except:
        print ("Error: unable to fetch items")    

    return render_template('chart3.html', values=values, labels = labels, legend=legend)   
# app.route('/sandy',methods=['POST','GET'])
# def sandy():
  
#     if request.method == 'POST':    
        
#         query_content=request.form['news_content']
        
#         total= query_content
#         total = re.sub('<[^>]*>', '', total)
#         total = re.sub(r'[^\w\s]','', total)
#         total = total.lower()     
#         data=[total]
#         twt = tokenizer.texts_to_sequences(data)
#         twt = pad_sequences(twt, maxlen=65, dtype='int32', value=0)
#         # transform data
#         sentiment = model.predict(twt,batch_size=1,verbose = 2)[0]
#         if(np.argmax(sentiment) == 0):
#               pred= "worry"
#         elif (np.argmax(sentiment) == 1):
#               pred="sad"
#         elif (np.argmax(sentiment) == 2):
#               pred="neutral"
   
#         login()
#         details = request.form
        
#         news_content = details['news_content']
#         professor_name = details['professor_name']
        
         
#         cur = mysql.connection.cursor()
#         cur.execute("INSERT INTO review(news_content,pred,userid,professor_name) VALUES ( %s, %s,%s,%s) ", (news_content,pred,Id,professor_name))
         
#         mysql.connection.commit()
#         cur.close()
#         return redirect('/users')
         
 
         
     
         
#     return render_template('index.html') @
# @app.route('/users')
# def users():
     
#     cur = mysql.connection.cursor()
#     resultValue = cur.execute(" SELECT * from student INNER JOIN review ON student.ID = review.USERID;")
     
#     if resultValue > 0:
#         userDetails = cur.fetchall()
         
#         return render_template('users.html',userDetails=userDetails)    
# @app.route('/admin')
# def admin():
#     cur = mysql.connection.cursor()
#     resultValue = cur.execute(" SELECT * from student INNER JOIN review ON student.ID = review.USERID;")
     
#     if resultValue > 0:
#         userDetails = cur.fetchall()
         
#         return render_template('admin.html',userDetails=userDetails)  
# @app.route('/userdetail')
# def userdetail():  
#    cur = mysql.connection.cursor()      
#    cur.execute("SELECT * from student")
#    useradmin=cur.fetchall()
#    print(useradmin)
       
#    return render_template('userdetail.html',useradmin=useradmin)         
# @app.route('/chart')
# def chart():
#     legend = "review by professor_name"
#     cursor = mysql.connection.cursor()
#     try:
#         cursor.execute("SELECT professor_name from review GROUP BY professor_name")
#         # data = cursor.fetchone()
#         rows1 = cursor.fetchall()
#         labels = list()
#         i = 0
#         for row1 in rows1:
#             labels.append(row1[i])
         

         
#         cursor.execute("SELECT professor_name from review GROUP BY professor_name")
#         # data = cursor.fetchone()
#         rows2 = cursor.fetchall()
        
#         label = list()
#         j = 0
#         values = list()
#         k = 0
#         for row2 in rows2:
#             label.append(row2[j])
#             cursor.execute("SELECT COUNT(id) from review WHERE  pred = 'neutral' and professor_name=%s", (row2[j],))
#             rows3 = cursor.fetchall()
             
#             #j=j+1
#         # Convert query to objects of key-value pairs
            
#             for row3 in rows3:
# 	              values.append(row3[k])
#             #k=k+1
#         mysql.connection.commit()
#         cursor.close()
        
        
        
#     except:
#         print('Error: unable to fetch items')    

#     return render_template('chart.html', values=values, labels = labels, legend=legend)
# @app.route('/sadness')
# def sadness():
#     legend = "review by professor_name"
#     cursor = mysql.connection.cursor()
#     try:
#         cursor.execute("SELECT professor_name from review GROUP BY professor_name")
#         # data = cursor.fetchone()
#         rows1 = cursor.fetchall()
#         labels = list()
#         i = 0
#         for row1 in rows1:
#             labels.append(row1[i])
         

         
#         cursor.execute("SELECT professor_name from review GROUP BY professor_name")
#         # data = cursor.fetchone()
#         rows2 = cursor.fetchall()
        
#         label = list()
#         j = 0
#         values = list()
#         k = 0
#         for row2 in rows2:
#             label.append(row2[j])
#             cursor.execute("SELECT COUNT(id) from review WHERE  pred = 'sad' and professor_name=%s", (row2[j],))
#             rows3 = cursor.fetchall()
             
#             #j=j+1
#         # Convert query to objects of key-value pairs
            
#             for row3 in rows3:
# 	              values.append(row3[k])
#             #k=k+1
#         mysql.connection.commit()
#         cursor.close()
        
        
        
#     except:
#         print('Error: unable to fetch items')    

# #     return render_template('sadness.html', values=values, labels = labels, legend=legend) 
# @app.route('/worry')
# def worry():
#     legend = "review by professor_name"
#     cursor = mysql.connection.cursor()
#     try:
#         cursor.execute("SELECT professor_name from review GROUP BY professor_name")
#         # data = cursor.fetchone()
#         rows1 = cursor.fetchall()
#         labels = list()
#         i = 0
#         for row1 in rows1:
#             labels.append(row1[i])
         

         
#         cursor.execute("SELECT professor_name from review GROUP BY professor_name")
#         # data = cursor.fetchone()
#         rows2 = cursor.fetchall()
        
#         label = list()
#         j = 0
#         values = list()
#         k = 0
#         for row2 in rows2:
#             label.append(row2[j])
#             cursor.execute("SELECT COUNT(id) from review WHERE  pred = 'worry' and professor_name=%s", (row2[j],))
#             rows3 = cursor.fetchall()
             
#             #j=j+1
#         # Convert query to objects of key-value pairs
            
#             for row3 in rows3:
# 	              values.append(row3[k])
#             #k=k+1
#         mysql.connection.commit()
#         cursor.close()
        
        
        
#     except:
#         print('Error: unable to fetch items')    

#     return render_template('worry.html', values=values, labels = labels, legend=legend)     
if __name__ == '__main__':
    app.run()