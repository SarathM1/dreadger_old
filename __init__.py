from flask import Flask, session, flash, request, jsonify, url_for, render_template, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import datetime

app =Flask (__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://reader:reader123@localhost/dreadger'
app.secret_key = 'my secret key is this'

class dieselLevel(db.Model):
	__tablename__ = 'dieselLevel'
	id = db.Column(db.Integer, primary_key=True)
	device = db.Column(db.String(25))
	level = db.Column(db.Integer)
	mTime = db.Column(db.DateTime)
	ip = db.Column(db.String(15))

class user(db.Model):
    __tablename__ = 'userTable'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40),unique=True)
    password = db.Column(db.String(40))
    email = db.Column(db.String(50))
    registered_on = db.Column(db.DateTime)

    def __init__(self,id,username,password,email,registered_on);
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.registered_on = datetime.utcnow()
        


def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if session['logged_in']:
			return f(*args, **kwargs)
		else:
			flash('You need to login first')
			return redirect(url_for('login'))
	return decorated_function

"""
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] = 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials.'
        else:
            session['logged_in'] = True
            flash('You have logged in')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST';
        user_auth = user.query.filter(user.username=request.form['username']).limit(1) 
        if user_auth[0].password == request.form['password']:
            session['logged_in'] = True
            flash('You have logged in')
            return redirect(url_for('home'))
        else:
            error = 'Inavlid Credentials'
        return render_template('login.html',error=error)
    if session.get('logged_in'):
        return redirect(url_for('home'))
    return render_template('login.html',error=error)


@app.route ("/index", methods=['GET'])
@login_required
def home():
	results = dieselLevel.query.order_by(dieselLevel.mTime.desc()).all()
	json_results = []
	for result in results:
		d = { 'device' : result.device,
			'level': result.level,
			'datetime' : result.mTime, 
			'ip' : result.ip}
		json_results.append(d)
	return jsonify(items=json_results)	

	
@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were just logged out')
    return redirect(url_for('login'))

def validate(data):
	try:
		datetime.strptime(data, '%d/%m/%Y %H:%M') 
		return 1 
	except:
		return None

def conTime(param):
	return datetime.strptime(param, '%d/%m/%Y %H:%M')


@app.route('/logs', methods=['GET', 'POST'])
@login_required
def logs():
    if request.method == 'POST':
        result = []
        if (validate(request.form['param1'])):
            if (validate(request.form['param2'])):
                results = dieselLevel.query.filter(conTime(request.form['param1']) < dieselLevel.mTime).filter(dieselLevel.mTime < conTime(request.form['param2'])).order_by(dieselLevel.mTime.desc()).all()
            else:
                results = dieselLevel.query.filter(conTime(request.form['param1']) < dieselLevel.mTime).order_by(dieselLevel.mTime.desc()).all()
        else:
            if (validate(request.form['param2'])):
                results = dieselLevel.query.filter(dieselLevel.mTime < conTime(request.form['param2'])).order_by(dieselLevel.mTime.desc()).all()
            else:
                return render_template('log.html')
        json_results = []
	for result in results:
		d = { 'device' : result.device,
			'level': result.level,
			'datetime' : result.mTime, 
			'ip' : result.ip}
		json_results.append(d)
	return jsonify(items=json_results)    
    return render_template('log.html')

@app.errorhandler(404)
def page_not_found(error):
	return 'This page does not exist',404

if __name__ == "__main__":
	app.run()

