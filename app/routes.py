from flask import render_template
from app import app
from app.forms import LoginForm

@app.route('/login')
def login():
  form = LoginForm()
  return render_template('login.html', title='Sign in', form=form)

@app.route('/')
def hello_world():
  return 'Hello, World!'