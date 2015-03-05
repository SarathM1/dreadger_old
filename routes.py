from flask import Flask, session, flash, request, jsonify, url_for, render_template, redirect
from flask.ext.sqlalchemy import SQLAlchemy
import os
from functools import wraps

app = Flask (__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' +  os.path.join(basedir, 'dreadger.db')

db = SQLAlchemy(app)

app.secret_key = 'my secret key is this'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session['logged_in']:
            return f(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('login'))
    return decorated_function


class dieselLevel(db.Model):
    __tablename__ = 'dieselLevel'
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(25))
    level = db.Column(db.Integer)

    def __init__(self, device,level):
        self.device = device
        self.level = level

    def __repr__(self):
        return '<Device %r Level %r >' % (self.device, self.level)


@app.route("/welcome")
def welcome():
    return ('welcome')

@app.route("/")
@login_required
def hello():

    results = dieselLevel.query.all()
    json_results = []
    for result in results:
        d = {
            'device' : result.device,
            'level' : result.level
        }
        json_results.append(d)
    return jsonify(items=json_results)




@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials.'
        else:
            session['logged_in'] = True
            flash('You have logged in')
            return redirect(url_for('hello'))
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were just logged out')
    return redirect(url_for('login'))

@app.route('/logs', methods=['GET', 'POST'])
@login_required
def logs():
    if request.method == 'POST':
        results = []
        if (request.form['param1']):
            if (request.form['param2']):

                results = dieselLevel.query.filter(request.form['param1'] < dieselLevel.level).filter(dieselLevel.level < request.form['param2']).all()

            else:
                results = dieselLevel.query.filter(request.form['param1'] < dieselLevel.level).all()

        else:
            if (request.form['param2']):
                results = dieselLevel.query.filter(dieselLevel.level < request.form['param2']).all()
            else:
                return render_template('log.html')

        json_results = []
        for result in results:
            d = {
                'device' : result.device,
                'level' : result.level
            }
            json_results.append(d)

        return jsonify(items=json_results)

    return render_template('log.html')

    



if __name__ == '__main__':
    app.run(debug=True)


