from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, RequestForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Request
from werkzeug.urls import url_parse
from datetime import datetime

@app.route('/')
@app.route('/index')
# @login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome, you are now a registered user.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    form = RequestForm()
    if form.validate_on_submit():
        request = Request(title=form.title.data, 
        description=form.description.data,
        product_area=form.product_area.data,
        clients=form.clients.data,
        priority=form.priority.data, 
        requestor=current_user)
        db.session.add(request)
        db.session.commit()
        flash('Your request has been recorded.')
        return redirect(url_for('index'))
    #requests = Request.query.filter_by(user_id=current_user.user_id).all()
    user = User.query.filter_by(username=username).first_or_404()
    features = current_user.user_requests()
    return render_template('user.html', user=user, features=features, form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()