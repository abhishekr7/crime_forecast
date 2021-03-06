from flask import Flask, render_template, request, redirect, url_for, flash
from form import RegistrationForm, LoginForm
from pymongo import MongoClient
from passlib.hash import sha256_crypt
import requests
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = '0f728c6b5c9f6e02690f9496da4818ae'

@app.route("/")
@app.route("/home")
def home():
	return render_template('index.html')

@app.route("/about")
def about():
	return render_template('about.html', title = 'About')

@app.route("/map")
def map():
	return render_template('map.html', title = 'Map')

@app.route("/forgot")
def forgot():
	return render_template('forgot.html')

@app.route("/admin")
def admin():
	return render_template('admin.html', title = 'Admin')

@app.route("/admin", methods = ['POST'])
def submitArticle():
	text = request.form['text']
	processed_text = text

	client = MongoClient("mongodb+srv://test:test123%23@cluster0-l5ord.mongodb.net/test?retryWrites=true&w=majority")
	db = client.get_database('user_db')

	article_db = db.articles

	print(processed_text)

	data = json.dumps({"text" : processed_text})

	#data = '{"text": "Seven young men, armed with sharp weapons, went on the rampage in Nigdi on Friday night."}'

	print(data)
	#print(data2)

	response = requests.post('http://localhost:5005/model/parse', data=data)

	json_data = json.loads(response.text)

	article_doc = {"article" : str(json_data)}

	article_db.insert(article_doc)

	return render_template('admin.html', title = 'Admin')

@app.route("/login", methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		client = MongoClient("mongodb+srv://test:test123%23@cluster0-l5ord.mongodb.net/test?retryWrites=true&w=majority")
		db = client.get_database('user_db')
		creds = db.user_creds
		find_user = list(creds.find({'email':form.email.data}))
		if len(find_user) == 1:
			if sha256_crypt.verify(form.password.data, find_user[0]['passwd']):
				flash('You have been logged in!', 'success')
				return redirect(url_for('home'))
			else:
				flash('Please enter the correct email or password', 'danger')
		else:
			flash('Please enter the correct email or password', 'danger')

	return render_template('login.html', title = 'Login', form = form)

@app.route("/register", methods = ['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		client = MongoClient("mongodb+srv://test:test123%23@cluster0-l5ord.mongodb.net/test?retryWrites=true&w=majority")
		db = client.get_database('user_db')
		creds = db.user_creds
		dup_user = list(creds.find({'username' : form.username.data}))
		dup_email = list(creds.find({'email' : form.email.data}))

		if len(dup_user) == 0 and len(dup_email) == 0:
			enc_pass = sha256_crypt.encrypt(form.password.data)
			new_user = {'username' : form.username.data, 'email' : form.email.data, 'passwd' : enc_pass}
			creds.insert_one(new_user)
			flash(f'Account created for {form.username.data}!', 'success')
			return redirect(url_for('home'))
		elif len(dup_user) == 0:
			flash(f'{form.email.data} is already in use', 'danger')
		else:
			flash(f'{form.username.data} is already in use', 'danger')
	return render_template('register.html', title = 'Register', form = form)

if __name__ == '__main__':
	app.run(debug = True)
