from flask import Flask, redirect, render_template, request, session, jsonify
from flask_session import Session
from flask_mail import Mail, Message
import sqlite3
import time
import random
import re
import os
import json;
from flask import request

# Configure app
template_dir = os.path.abspath('C:/Users/Windows/Documents/CSE370/templates')
static_dir = os.path.abspath('C:/Users/Windows/Documents/CSE370/static')
app = Flask(__name__)#, template_folder=template_dir, static_folder=static_dir)


app.config["MAIL_DEFAULT_SENDER"] = "**email address"
app.config["MAIL_PASSWORD"] = "**password"
app.config["MAIL_PORT"] = 587
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "**email address"
app.config["DEBUG"] = True

mail = Mail(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


app.secret_key ="PETONOID"


## Connect to database
import mysql.connector



## FLASK routes defined
@app.route("/")
def index():
    if session.get("username"):
        if session.get("user")== "owner":
            return render_template("index.html")
        else:
            return redirect("/dindex")
    else:
        return render_template("indexA.html")
   
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print(username,password)
        database = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="PET"
        )

        db = database.cursor()
        db.execute("SELECT * FROM user WHERE username=%s AND password=%s", (username, password))
        x=db.fetchall()
        l= len(x)
        if l!=0:
            session["username"] = username
            session["user"] = "owner"
            return redirect("/")
        else:
            db.execute("SELECT * FROM doctor WHERE username=%s AND password=%s", (username, password))
            l1 = len(db.fetchall())
            db.close()
            if l1 != 0:
                session["username"] = username
                session["user"] = "doctor"
                return redirect("/")
            else:
                return render_template("login.html", message="Invalid information!")
    return render_template("login.html", message="")
   
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method== "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        database = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="PET"
        )

        db = database.cursor()
        db.execute("SELECT * FROM doctor WHERE username=%s AND password=%s", (username, password))
        l= len(db.fetchall())
        if l != 0:
            return render_template("signup.html", message="Account already exists with given information!")
        db.execute("INSERT INTO user values(%s, %s)", (username, password))
        database.commit()
        db.close()
        return redirect("/login")
    else:
        return render_template("signup.html", message="")

@app.route("/store")
def store():
    database = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="PET"
    )


    db = database.cursor()
    db.execute("SELECT * FROM store")
    items=db.fetchall()
    db.close()
    return render_template("store.html", items=items)

@app.route("/order", methods =["POST"])
def order():
    if session.get("username"):
        bought = request.form.get("bought")
        bought=bought.split(",")
        bill = request.form.get("bill")
        address = request.form.get("address")
        database = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="PET"
        )

        db = database.cursor()
        db.execute("SELECT * FROM purchase")
        id= len(db.fetchall())+1
        db.execute("INSERT INTO purchase values(%s,%s,%s,%s)",(id, session["username"], bill, address))
        database.commit()
        for i in bought:
            db.execute("INSERT INTO odetails values(%s,%s)",(id, i))
            database.commit()
        db.close()
    return redirect("/pastorders")

@app.route("/pastorders")
def pastorders():
    if session.get("username"):
        database = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="PET"
        )

        db = database.cursor()
        db.execute("SELECT id, bill, address FROM purchase WHERE username=%s", (session["username"],))
        purchases = db.fetchall()
        lt=[]
        for p in purchases:
            print(p)
            db.execute("SELECT product FROM odetails WHERE id=%s", (p[0],))
            products = db.fetchall()
            print("products", products)
            l1=[]
            for x in products:
                l1+= [x[0]]
            print(list(p))
            lt.append([list(p) + [l1]])
            print(lt)

        db.close()
    return render_template("pastorders.html", list=lt, l=len(lt))



@app.route("/appointment")
def appointment():
    if session.get("username"):
        database = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="PET"
        )

        db = database.cursor()

        db.execute("SELECT name,type,hospital,branch,status FROM doctor,appointment WHERE doctor.username=appointment.dusername AND pusername= %s", (session["username"],))
        appointments = db.fetchall()
        db.close()
    return render_template("appointment.html", appointments=appointments, l=len(appointments))

@app.route("/dindex")
def dindex():
    if session.get("username"):
        database = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="PET"
        )

        db = database.cursor()

        db.execute("SELECT pusername, status FROM appointment WHERE dusername=%s", (session["username"],))
        owners = db.fetchall()
        db.close()
    return render_template("dindex.html", owners=owners, user=session["username"])


@app.route("/dresponse", methods=["POST"])
def dresponse():
    if session.get("username"):
        if request.form.get("answer"):
            ans=request.form.get("answer")
        else:
            ans=request.form.get("answer1")

        owner = request.form.get("owner")
        print(owner, session["username"], ans)
        database = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="PET"
        )

        db = database.cursor()

        db.execute("UPDATE appointment SET status=%s WHERE pusername=%s AND dusername=%s", (ans, owner, session["username"]))
        database.commit()
        db.close()
    return redirect("/dindex")



@app.route("/makeappointment", methods=["POST"])
def makeappointment():
    if session.get("username"):
        dusername = request.form.get("dusername")
        print(dusername)
        database = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="PET"
        )

        db = database.cursor()

        db.execute("INSERT INTO appointment values(%s, %s, %s)",(session["username"], dusername, "Requested"))
        database.commit()
        db.close()
    return redirect("/appointment")

@app.route("/doctor", methods=["GET", "POST"])
def doctor():
    database = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="root",
        database="PET"
    )

    db = database.cursor()
    db.execute("SELECT username, name, type, branch, hospital FROM doctor")
    doctors1 = db.fetchall()
    db.execute("SELECT distinct type FROM doctor")
    types= db.fetchall()
    db.execute("SELECT distinct hospital FROM doctor")
    hospitals = db.fetchall()
    db.execute("SELECT distinct branch FROM doctor")
    branches = db.fetchall()
    doctors=[]
    db.close()
    if request.form.get("type"):
        x = request.form.get("type")
        for i in doctors1:
            if x in i:
                doctors.append(i)
    elif request.form.get("hospital"):
        x = request.form.get("hospital")
        for i in doctors1:
            if x in i:
                doctors.append(i)
    elif request.form.get("branch"):
        x = request.form.get("branch")
        for i in doctors1:
            if x in i:
                doctors.append(i)
    else:
        doctors=doctors1
    return render_template("doctor.html", doctors=doctors, types=types, hospitals=hospitals, branches=branches)

@app.route("/blog")
def blog():
    return render_template("blog.html")

@app.route("/logout")
def logout():
    session["username"] = None
    session["user"] = None
    return redirect("/")


#############################################################################
if __name__ == '__main__':
    app.run(debug=True)