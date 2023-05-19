from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from datetime import date


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        
        user = User.query.filter_by(u_email=login).first()
        if user == None:
            user = User.query.filter_by(u_name=login).first()

        if user:
            if check_password_hash(user.u_password, password):
                flash("Logged in successfully", category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash("Incorect password!", category='error')
        else:
            flash("Email/Account does not exist", category='error')

    return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        u_name = request.form.get('userName')
        u_fname = request.form.get('firstName')
        u_lname = request.form.get('lastName')
        u_email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(u_email=u_email).first()

        if user:
            flash('User already exists.', category='error')
        elif len(u_email) < 4:
            flash('Email must be greater than 4 chars', category='error')
        elif len(u_fname) < 2:
            flash('First name must be greater than 1 chars', category='error')
        elif password1 != password2:
            flash('Password don\'t match', category='error')
        elif len(password1) < 3:
            flash('Password must be at least 7 characters', category='error')
        else:
            new_user = User(u_name=u_name, u_fname=u_fname, u_lname=u_lname, u_email=u_email, u_password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('sign_up.html', user=current_user)
