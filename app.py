from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
#from data import Articles
from flask_mysqldb import MySQL
import validators
import mysql.connector
from passlib.hash import sha256_crypt
from functools import wraps
import json
import re
import pyotp
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

# # Config MySQL
# app.config['MYSQL_HOST'] = '127.0.0.1'
# app.config['MYSQL_USER'] = 'root'
# # app.config['MYSQL_PASSWORD'] = '123456'
# app.config['MYSQL_DB'] = 'users'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# # init MYSQL
# mysql = MySQL(app)

# Register Form Class
mydb = mysql.connector.connect(host = "127.0.0.1", user = "root",database = "users")
email_id = ''  
fh_2fa = ''
# creates SMTP session 
s = smtplib.SMTP('smtp.gmail.com')
# Authentication
s.starttls()
# start TLS for security
s.login("sushilraverkar007@gmail.com", "Youcanthackme789")
 #create object of the connection
def pass_val(passwd):
    while True:
        if len(passwd) < 8:
            return "Make sure your password is at lest 8 letters"
        elif re.search('[0-9]',passwd) is None:
            return "Make sure your password has a number in it"
        elif re.search('[A-Z]',passwd) is None: 
            return "Make sure your password has a capital letter in it"
        else:
            print("Your password seems fine")
            return "true"

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = request.json  
    print("@@@@@@@@@@",form)
    val_email = validators.email(form["email"])
    print(val_email)
    val_passwd = pass_val(form["password"])
    if val_email == True:
        print("In email")
        if val_passwd == "true":
            print("In passwd")
            if form["confirm_password"] == form["password"]:
                print("In confirm passwd")
                password = sha256_crypt.encrypt(str(form["password"]))
                # Create cursor
                cur = mydb.cursor()
                # Execute query
                cur.execute("INSERT INTO Users(name, email, username, password) VALUES(%s, %s, %s, %s)", (form["name"], form["email"], form["username"], password))
                # Commit to DB
                mydb.commit()
                
                # Close connection
                cur.close()
                # flash('You are now registered and can log in', 'success')
        # return redirect(url_for('login'))
    return "Sign up successfully"  
    # return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    sender_address = 'sushilraverkar007@gmail.com'
    message = MIMEMultipart()
    message['From'] = sender_address
    message['Subject'] = 'OTP From Green Thumb'
    if request.method == 'POST':
        # Get Form Fields
        username = request.json['username']
        password_candidate = request.json['password']
        # Create cursor
        cur = mydb.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s ', [username])
        myresult = cur.fetchone()
        cur.close()
        password = myresult[5]
        email_id = myresult[2]
        if sha256_crypt.verify(password_candidate, password):
            session['logged_in'] = True
            session['username'] = username
            totp = pyotp.TOTP('base32secret3232',interval=90)
            fh_2fa = totp.now() 
            message.attach(MIMEText(fh_2fa, 'plain'))
            text = message.as_string()
            # sending the mail 
            s.sendmail(sender_address, email_id,text)
            # terminating the session 
            s.quit()  
            
            print("!!!!!!!!!!!!!",fh_2fa)
            return "OTP sent to your mail"
        else:
            return "Please try again"
        # #return redirect(url_for('dashboard'))
        #     else:
        #         error = 'Invalid login'
        #         return "Go to login page Again"
        #     # Close connection
            
        # else:
        #     error = 'Username not found'
        #     return error
    # return render_template('login.html')

# OTP
@app.route('/otpauth', methods=['GET', 'POST'])
def otp_auth():
    temp_otp = request.json['otp']
    print("HERE",fh_2fa)
    if temp_otp == fh_2fa:
        print("TRUEEEEEEEEEEEEEEEEEE")
    else:
        print("Wrong OTP!!!!!!!!!!!!!!!!!!!!!")    
    
    return "Welcome to Green Thumb"

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)