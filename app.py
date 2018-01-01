#!/usr/bin/env python
import os

import datetime
from flask import Flask, abort, request, jsonify, g, url_for, flash, render_template
from flask_mail import Message, Mail
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_login import login_required, current_user
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired, URLSafeTimedSerializer)


# initialization
from validate_email import validate_email
from werkzeug.utils import redirect

app = Flask(__name__)
mail = Mail(app)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['N_TOKENS'] = 1
# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()



class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))
    registered_on = db.Column(db.DateTime, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    password_reset_token = db.Column(db.String, nullable=True)

    def __init__(self, email, password, confirmed,
                 confirmed_on=None):
        self.email = email
        self.password = pwd_context.encrypt(password)
        self.registered_on = datetime.datetime.now()
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def verify_email(email):
        return validate_email(email,check_mx=True)


#user log in
@auth.verify_password('/api/users/login')
def verify_password(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not user.verify_password(password):
        abort(401) #can not log in
        return jsonify({'User email or password incorrect. Access Denied.'})
    g.user = user
    return True

#user sign up
@app.route('/api/users/signup', methods=['POST'])
def new_user():
    email = request.json.get('email')
    password = request.json.get('password')
    if email is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(email=email).first() is not None:
        abort(400)    # existing user
    if not email.verify_email(email):
        abort(400)   # not valid email
    user = User(email, password, confirmed=False)
    db.session.add(user)
    db.session.commit()
    send_confirmation(email)
    return jsonify({'Please check you email to confirm registration.'})

@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'email': user.email})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.email})

@app.route("/")
def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)


@app.route('/send')
def send_confirmation(email):
    token = generate_confirmation_token(email)
    confirm_url = url_for('user.confirm_email', token=token, _external=True)

    html = "<p>Hello! Thanks for signing up. Please follow this link to activate your account:</p>\
    <p><a href={}</a></p>\
    <br>\
    <p>Regards!</p>".format(confirm_url)

    subject = "Please confirm your email"
    send_email(email, subject, html)
    flash('A confirmation email has been sent.', 'success')
    return redirect(url_for('user.unconfirmed'))


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email


@app.route('/confirm/<token>')
@login_required
def confirm_email(token):
    if current_user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
        return redirect(url_for('main.home'))
    email = confirm_token(token)
    user = User.query.filter_by(email=current_user.email).first_or_404()
    if user.email == email:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'danger')
    return redirect(url_for('main.home'))


if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True)


