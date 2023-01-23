from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from .forms import SignupForm
from .models import User
from flask_login import login_user

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        name = form.name.data
        password = form.password.data
    # if request.method == 'POST':
    #     email = request.form.get('email')
    #     name = request.form.get('name')
    #     password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email уже занят')
            return redirect(url_for('auth.signup'))

        new_user = User(
            email=email,
            name=name,
            password=generate_password_hash(password, method='sha256'),
        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user, remember=True)
        return redirect(url_for('main.index'))

    return render_template('signup.html', form=form)


@auth.route('/logout')
def logout():
    return render_template('signup.html')
