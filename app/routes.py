from flask import render_template, flash, redirect
from app import app
from app.forms import LoginForm

@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit:
    flash('Login requested for user {}, remember_ne={}'.format(
      form.username.data, form.remember_me.data
    ))
    return redirect('/')
  return render_template('login.html', title='Sign in', form=form)

@app.route('/')
def hello_world():
  return 'Hello, World!'