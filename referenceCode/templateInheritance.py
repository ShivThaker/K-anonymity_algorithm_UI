from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
import hashlib

app = Flask(__name__)
app.secret_key = 'hello'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=5) # days=5

db = SQLAlchemy(app)

# create a model to store information in
# inherits db.Model, class will be a database model

class User(db.Model):
    _id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column('name', db.String(10))
    email = db.Column('email', db.String(10))
    gender = db.Column('gender', db.String(5))
    card_no = db.Column('card_no', db.String(20))
    balance = db.Column('balance', db.Integer)
    login_password = db.Column('login_password', db.String(100))
    password = db.Column('password', db.String(100))
    existing_user = db.Column('existing_user', db.Boolean)
    # nullable=False, unique=True

    def __init__(self, name, gender, email, card_no, balance, existing_user, password, login_password):
        self.name = name
        self.email = email
        self.gender = gender
        self.card_no = card_no
        self.balance = balance
        self.existing_user = existing_user
        self.password = password
        self.login_password = login_password


# class RegistrationFrom(FlaskForm):
#     user = StringField(validators=[InputRequired(), Length(min=1, max=10)], render_kw={'placeholder': 'User name'})
#     password = PasswordField(validators=[InputRequired(), Length(min=1, max=10)], render_kw={'placeholder': 'Password'})
#     submit = SubmitField('Submit')
#
#     def validate_username(self, user):
#         existing_user_name = User.query.filter_by(name=user.data).first()
#         if existing_user_name:
#             raise ValidationError('That username already exists. Please choose a different one.')
#
#
# class LoginForm(FlaskForm):
#     user = StringField(validators=[InputRequired(), Length(min=1, max=10)], render_kw={'placeholder': 'User name'})
#     password = PasswordField(validators=[InputRequired(), Length(min=1, max=10)], render_kw={'placeholder': 'Password'})
#     submit = SubmitField('Login')


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        session.permanent = True
        # actually get the information that was in the form and use that and send it to for example the user page so we can display the user's name
        card_no = request.form["card_no"]
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        # set up some session data based on whatever information they typed in
        session['card_no'] = card_no

        found_user_frm_db = User.query.filter_by(card_no=card_no).first()
        if found_user_frm_db:
            if found_user_frm_db.login_password == password:
                session['nm'] = found_user_frm_db.name
                session['email'] = found_user_frm_db.email
                session['card_no'] = found_user_frm_db.card_no
                if found_user_frm_db.gender == '_':
                    session['gender'] = 'Rather not declare'
                else:
                    session['gender'] = found_user_frm_db.gender
                flash('Login successfull', 'info')
                return redirect(url_for('user'))
            else:
                flash('Wrong password - login denied')
                return render_template('login.html')
        else:
            flash('No account found with the given card number')
            return render_template('login.html')
            # usr = User('', '', card_no, '')
            # db.session.add(usr) # add the usr model to the database
            # db.session.commit()
    else:
        # if we hit the GET request, we can just render out the login template
        # meaning we did not click on the submit button, we just clicked on the /login page
        if 'card_no' in session:
            flash('Already logged in', 'info')
            return redirect(url_for('user'))
        return render_template('login.html')

@app.route("/logout/")
def logout():
    if 'card_no' in session:
        # user = session['user']
        flash('Logout successful', 'info') # ('msg', 'built in category')
    session.pop('nm', None)
    session.pop('email', None)
    session.pop('card_no', None)
    session.pop('existing_user', None)
    session.pop('balance', None)
    session.pop('gender', None)
    # render_template('login.html', alert='alert alert-success')
    return redirect(url_for('login'))

@app.route('/user/', methods=['POST', 'GET'])
def user():
    if 'card_no' in session:
        if request.method == 'POST':
            name = request.form['nm']
            card_no = request.form['card_no']
            email = request.form['email']
            gender = request.form['gender']
            session['nm'] = name
            session['card_no'] = card_no
            session['email'] = email
            session['gender'] = gender
            if gender == 'Rather not declare':
                gender = '_'
                session['gender'] = 'Rather not declare'

            found_user_frm_db = User.query.filter_by(card_no=card_no).first()
            found_user_frm_db.name = name
            found_user_frm_db.card_no = card_no
            found_user_frm_db.email = email
            found_user_frm_db.gender = gender
            db.session.commit()
            flash('New Details saved')
            return render_template('user.html', nm=session['nm'], email=session['email'], card_no=session['card_no'], gender=session['gender'], alert='alert alert-success')
        else:
            return render_template('user.html', nm=session['nm'], email=session['email'], card_no=session['card_no'], gender=session['gender'], alert='alert alert-success')
    else:
        flash('You are not logged in', 'info')
        return redirect(url_for('login'))
        # , alert = 'alert alert-danger'

@app.route('/changepin/', methods=['POST', 'GET'])
def changepin():
    # card_no = None
    nm = None
    email = None
    password = None
    if 'card_no' in session:
        card_no = session['card_no']
        found_user_frm_db = User.query.filter_by(card_no=card_no).first()
        session['existing_user'] = found_user_frm_db.existing_user
        existing_user = session['existing_user']

        if request.method == 'POST' and existing_user:
            oldpass = hashlib.sha256(request.form['oldpass'].encode()).hexdigest()
            newpass = hashlib.sha256(request.form['newpass'].encode()).hexdigest()
            verifynewpass = hashlib.sha256(request.form['verifynewpass'].encode()).hexdigest()

            if found_user_frm_db.password == oldpass:
                if newpass == verifynewpass:
                    found_user_frm_db.password = newpass
                    db.session.commit()
                    flash('New Password saved')
                    return render_template('changepin.html', alert='alert alert-success', control=True)
                else:
                    flash('New Passwords do not match')
                    return render_template('changepin.html', alert='alert alert-danger', control=True)
            else:
                flash('Old password not correct for change of passowrd')
                return render_template('changepin.html', alert='alert alert-danger', control=True)

        elif request.method == 'POST' and not existing_user:
            newpass = hashlib.sha256(request.form['newpass'].encode()).hexdigest()
            verifynewpass = hashlib.sha256(request.form['verifynewpass'].encode()).hexdigest()

            if newpass == verifynewpass:
                found_user_frm_db.password = newpass
                found_user_frm_db.existing_user = True
                db.session.commit()
                flash('New Password saved')
                return render_template('changepin.html', alert='alert alert-success', control=True)
            else:
                flash('New Passwords do not match')
                return render_template('changepin.html', alert='alert alert-danger', control=False)

        elif not existing_user:
            return render_template('changepin.html', control=False)

        elif existing_user:
            return render_template('changepin.html', control=True)

        else:
            pass
        return render_template('changepin.html')
    else:
        flash('You are not logged in', 'info')
        return redirect(url_for('login'))

@app.route('/withdrawl/', methods=['POST', 'GET'])
def withdrawl():
    if 'card_no' in session:
        card_no = session['card_no']
        found_user_frm_db = User.query.filter_by(card_no=card_no).first()
        session['existing_user'] = found_user_frm_db.existing_user
        session['balance'] = found_user_frm_db.balance
        existing_user = session['existing_user']
        balance = session['balance']

        if request.method == 'POST' and existing_user:
            withdraw_amount = int(request.form['amount'])
            pin = hashlib.sha256(request.form['pin'].encode()).hexdigest()
            # pin = request.form['pin']
            if found_user_frm_db.password == pin:
                if found_user_frm_db.balance >= withdraw_amount:
                    found_user_frm_db.balance = found_user_frm_db.balance - withdraw_amount
                    db.session.commit()
                    flash('Amount withdrawn')
                    return render_template('withdrawl.html', alert='alert alert-success', control=True, balance=found_user_frm_db.balance)
                else:
                    flash('Withdraw amount more than balance - withdrawl blocked')
                    return render_template('withdrawl.html', alert='alert alert-danger', control=True, balance=found_user_frm_db.balance)
            else:
                flash('Wrong pin - withdrawl blocked')
                return render_template('withdrawl.html', alert='alert alert-danger', control=True, balance=found_user_frm_db.balance)

        elif request.method == 'POST' and not existing_user:
            return render_template('withdrawl.html', alert='alert alert-danger', control=False)

        elif not existing_user:
            return render_template('withdrawl.html', control=False, balance=balance)

        elif existing_user:
            return render_template('withdrawl.html', control=True, balance=balance)

        else:
            pass
        return render_template('withdrawl.html')
    else:
        flash('You are not logged in', 'info')
        return redirect(url_for('login'))

@app.route('/view/')
def view():
    # get all the users and pass them as objects into our render template, to display info
    return render_template('view.html', values=User.query.all())

if __name__ == '__main__':
    # this will create the database if it doesn't already exist, very important
    db.create_all()
    app.run(debug=True)

# session, use while the user is browsing on the website
# as soon as they leave, it will dissapear, temporary, stored on the server, not on the client side
# desinged for quick access of information, a way to pass information around the server
# all the session data is encrypted on the server, we need to define a secret key to be able to encrypt and decrypt data


# .delete() on one specific object

'''
credentials
login pin
op  8989
io  abc
ui  9999
kl 6767
ooo 4545
uuu 
'''