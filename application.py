import os

from flask import Flask, session, render_template, redirect, url_for, escape, request, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask import g 
import requests
from flask import jsonify
import json

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'



@app.route("/")
def index():
    return render_template("index.html")

@app.route('/login', methods=["GET", "POST"])
def login():
	if request.method == 'POST':
		username =  request.form.get("username")
		password =  request.form.get("password")
		rows = db.execute("SELECT * FROM users WHERE username = :username", {"username":username}).fetchall()

		if not rows or not check_password_hash(rows[0]['password'], request.form.get("password")):
			return render_template("login.html", message="Username or password incorrect")
		

		session["username"] = rows[0]['username']
		session['logged_in'] = True
		return redirect(url_for('dashboard'))
	return render_template("login.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		username = request.form.get("username")
		password = request.form.get("password")
		password2 = generate_password_hash(password)
		email = request.form.get("email")
		# Check if username exists in database
		try:
			db.execute("INSERT INTO users(username, password, email) VALUES(:name, :password, :email)",{"name":username, "password":password2, "email":email})
		except:
			return render_template("signup.html", message="User name is already taken by someone else, Please Choose another one")
		db.commit()
		session['username']=username
		return redirect(url_for('login'))
	return render_template("signup.html")


@app.route('/logout')
def logout():
    session.pop('username', None)
    session['logged_in'] = False
    return redirect(url_for('index'))



@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
	if request.method == "POST":
		if 'username' in session:
			search = request.form.get("search")
			search_values = db.execute("select * from books where title like :search or author like :search or isbn like :search or year like :search" , {"search": f"%{search}%"}).fetchall()

			if len(search_values) == 0:
				return render_template("dashboard.html", message="Search Not Found")
			else:
				return render_template("dashboard.html", search_values=search_values)
			
		
		return redirect (url_for("error"))
	return render_template("dashboard.html")

@app.route("/dashboard/<string:isbn>", methods=['GET', 'POST'])
def book(isbn):
	if request.method == "POST":
		username = session['username']
		rate = request.form.get("rate")
		rate = int(rate)
		comment = request.form.get("comment")
		check = db.execute("select * from reviews where user_username = :username and book_isbn = :isbn" , {"username": username, "isbn":isbn}).fetchall()
		if len(check) == 0:
			db.execute("INSERT INTO reviews(user_username, book_isbn, rate, comment) VALUES(:user_username, :book_isbn, :rate, :comment)",{"user_username":username, "book_isbn":isbn, "rate":rate, "comment":comment})
			db.commit()
		else:
			return render_template("error.html")
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "liVnFxoJhIIC3giMBuFw", "isbns": isbn})
	data = res.json()
	rate = data['books'][0]['average_rating']
	ratecount = data['books'][0]['ratings_count']
	
	value = db.execute("select * from books where isbn = :isbn", {"isbn":isbn}).fetchone()
	comments = db.execute("select * from reviews where book_isbn = :book_isbn", {"book_isbn":isbn}).fetchall()
	return render_template("book.html", value=value, rate=rate, ratecount=ratecount, comments=comments)


@app.route("/error")
def error():
	return render_template('error.html')

@app.route("/api/<string:isbn>")
def book_api(isbn):
	book = db.execute("select * from books where isbn = :isbn", {"isbn":isbn}).fetchone()
	review_count = db.execute("select count(*) from reviews where book_isbn = :isbn", {"isbn":isbn}).fetchall()
	result1 =[]
	for row in review_count:
		result1.append([x for x in row]) 
	average_score = db.execute("select AVG(rate) from reviews where book_isbn = :isbn", {"isbn":isbn}).fetchall()
	result2 =[]
	for row in average_score:
		result2.append([x for x in row])
	if result2[0][0] is None:
		final = 0
	else:
		final = float(result2[0][0])
	if book is None:
		return jsonify({"Error": "Invalid book isbn"})
	else:
		return jsonify({
			"title": book.title,
			"author": book.author,
			"year": book.year,
			"isbn": book.isbn,
			"review_count": result1[0][0],
			"average_score": final
			})