from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm
from app.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime
from flask_babel import _
from langdetect import detect, LangDetectException


@app.before_request
def before_request():
  if current_user.is_authenticated:
    current_user.last_seen = datetime.utcnow()
    db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():  

  form = PostForm()
  if form.validate_on_submit():
    try:
      language = detect(form.post.data)
    except LangDetectException:
      language = ''
    post = Post(body=form.post.data, author=current_user, language=language)
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('index'))

  page = request.args.get('page', 1, type=int)
  posts = current_user.followed_posts().paginate(
    page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
  next_url = url_for('index', page=posts.next_num) \
    if posts.has_next else None
  prev_url = url_for('index', page=posts.prev_num) \
    if posts.has_prev else None
  return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print("logged in ")
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'Post'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = RegistrationForm()
  if form.validate_on_submit():
    user = User(username=form.username.data, email=form.email.data)
    user.set_password(form.password.data)
    db.session.add(user)
    db.session.commit()
    flash(_('Congrats, you are now a registered user'))
    return redirect(url_for('login'))
  return render_template('registration.html', title="Register", form=form)

@app.route('/explore')
@login_required
def explore():
  page = request.args.get('page', type=int)
  posts = current_user.followed_posts().paginate(
    page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
  next_url = url_for('index', page=posts.next_num) if posts.has_next else None
  prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None 

  return render_template('index.html', title='explore', posts=posts.items, next_url=next_url,
                        prev_url=prev_url)


@app.route('/user/<username>')
@login_required
def user(username):
  form=EmptyForm()
  user = User.query.filter_by(username=username).first_or_404()
  page = request.args.get('page', type=int)
  posts = user.posts.order_by(Post.timestamp.desc()).paginage(
    page = page, per_page=app.config['POSTS_PER_PAGE'], type=int
  )
  next_url = url_for('user', username=user.username, page=posts.next_num) if posts.has_next else None
  prev_url = url_for('user', username=user.username, page=posts.prev_num) if posts.has_prev else None
  posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
  return render_template('user.html', user=user, posts=posts.items, form=form, next_url=next_url, prev_url=prev_url)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
  form = EditProfileForm(current_user.username)
  if form.validate_on_submit():
    current_user.username = form.username.data
    current_user.about_me = form.about_me.data
    db.session.commit()
    flash(_('Your changes have been saved'))
    return redirect(url_for('edit_profile'))
  elif request.method == 'GET':
    form.username.data = current_user.username
    form.about_me.data = current_user.about_me
  return render_template('edit_profile.html', title='Edit Profile', form=form)



@app.route('/follow/<username>', methods=['Post'])
@login_required
def follow(username):
  form = EmptyForm()
  if form.validate_on_submit():
    user = User.query.filter_by(username=username).first()
    if user is None:
      flash(_('User {} not found'.format(username)))
      return redirect(url_for('index'))
    if user == current_user:
      flash(_('You cannot follow yourself!'))
      return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following {}'.format(username)))
    return redirect(url_for('user', username=username))
  else:
    return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
  form = EmptyForm()
  if form.validate_on_submit():
    user = User.query.filter_by(username=username).first()
    if user is None:
      flash(_('User {} not found.'.format(username)))
      return redirect(url_for('index'))
    if user == current_user:
      flash(_('You cannot unfollow yourself!'))
      return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are following {}'.format(username)))
    return redirect(url_for('user', username=username))
  else:
    return redirect(url_for('index'))
