import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pandas as pd
from datetime import datetime
import time
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import UserMixin, LoginManager ,login_required, login_user, logout_user, current_user
from wtforms import StringField, IntegerField, FloatField, SubmitField, PasswordField 
from wtforms.validators import DataRequired, EqualTo, Email
from werkzeug.security import generate_password_hash, check_password_hash
from twilio.rest import Client
#-------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------

ACCOUNT_SID = "AC5f3438649249fe1846b7eeb665d857f3"
AUTH_TOKEN = "9ed80eae9dfd84c791e00337775f0a51"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
path0 = r'C:\Users\USER\Documents\Isis\fun\datasets_models\Crop_recommendation.csv'
path = r'C:\Users\USER\Documents\Isis\fun\datasets_models\model.h5'

data = pd.read_csv(path0)
X = data.iloc[:, :-1].values
y = data.iloc[:, -1].values

le = LabelEncoder()

y_encoded = le.fit_transform(y)

y_onehot = tf.keras.utils.to_categorical(y_encoded, num_classes=22)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Charlie_dont_surf1000'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c_atoms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#--------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
# OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
# OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO

class users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password


class log(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email(message='Input a valid email')])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password', message='Passwords Must match!')])
    
    submit = SubmitField('SUBMIT😙!')

class suck(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message='Input a valid email')])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('SUBMIT!')



class pouchs(FlaskForm):
    nitrogen = IntegerField('nitrogen', validators=[DataRequired()])

    phosphorous = IntegerField('phosphorous', validators=[DataRequired()])

    potassium = IntegerField('potassium', validators=[DataRequired()])

    temperature = FloatField('temperature', validators=[DataRequired()])

    humidity = FloatField('humidity', validators=[DataRequired()])

    soil_ph = FloatField('soil_ph', validators=[DataRequired()])

    rainfall = FloatField('rainfall', validators=[DataRequired()])
 

    submit = SubmitField('Know the crop🙂')

# OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
# OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'authenticate'

@lm.user_loader
def user(user_id):
    return users.query.get(int(user_id))

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


@app.before_first_request
def load_model():
    global model
    model = tf.keras.models.load_model(path)

@app.route('/admin', methods=['POST', 'GEt'])
def admin():
    id = current_user.id
    usr = users.query.get_or_404(id)
    all = users.query.order_by(users.date)
    if id == 1 or id == 5:
        flash(f'Welcome back {usr.name} 💕', category='success')
        return render_template('admin.html', all=all)
    else:
        flash('Only admins can log in to this page')
        return redirect(url_for('home'))    

@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    form = suck()

    if form.validate_on_submit():
        user = users.query.filter_by(email=form.email.data).first()

        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash(f"Successful log in, Welcome back {user.name}", category='success')
                return redirect(url_for('home'))
            else:
                flash('Wrong Password! Kindly retry...', category='error')
                return render_template('auth.html', form=form, id=user.id)
        
        else:
            flash(f"The email is not registered. Sign up for free below.", category='error')
            
    return render_template('auth.html', form=form, id=0)



@app.route('/sign', methods=['GET', 'POST'])
def sign():
    name = None
    email = None
    password = None
    Xsr = None

    form = log()

    if form.validate_on_submit():
        user = users.query.filter_by(email=form.email.data).first()
        if user:
            Xsr = user.name
            flash(f"{name}, Email already exist under the name {Xsr}! Choose another")
            return redirect(url_for('sign'))
        else:
            user = users(name=form.name.data, email=form.email.data, password=generate_password_hash(form.password.data, "sha256"))
            db.session.add(user)
            db.session.commit()
            Xsr = user.name
            message = client.messages.create(
                    to= '+254794096950',
                    from_= '+15855412051',
                    body= f"Hope you enjoying your time S->Admin LAWRENCE. Another user, name: {Xsr}, has joined!❤"
                )
            

        name = form.name.data
        email = form.email.data
        password = form.password.data

        form.email.data = ''
        form.password.data = ''
        
        flash(f'Your account has been successfully created {name}....Welcome❤', category="success")
        return redirect(url_for('home'))

    all = users.query.order_by(users.date)

    return render_template('sign.html', form=form, name=name, email=email, password=password, all=all)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = log()

    user = users.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.password = request.form['password']

        try:
            user.password = generate_password_hash(user.password, 'sha256')
            db.session.commit()
            flash(f"Changes applied successfully, {user.name}")
            return redirect(url_for('home'))
        except:
            flash("A problem occured, retry again")
            return render_template('update.html', form=form, user=user, id=id)    
    else:
        return render_template('update.html', form=form, user=user, id=id)  
    

@app.route('/updatee/<int:id>', methods=['GET', 'POST'])
def updatee(id):
    form = log()

    user = users.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.password = request.form['password']

        try:
            user.password = generate_password_hash(user.password, 'sha256')
            db.session.commit()
            flash(f"Changes applied successfully, {user.name}")
            return redirect(url_for('home'))
        except:
            flash("A problem occured, retry again")
            return render_template('updatee.html', form=form, user=user, id=id)    
    else:
        return render_template('updatee.html', form=form, user=user, id=id)  
    

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    name = None
    email = None
    password = None
    form = log()

    user = users.query.get_or_404(id)
    all = users.query.order_by(users.date)

    try:
        db.session.delete(user)
        db.session.commit()
        flash(f"User {user.name} has been deleted successfully", category='success')
        return render_template('sign.html', form=form, name=name, email=email, password=password, all=all)
    except:
        flash("An error occured, retry again", category='error')
        return render_template('sign.html', form=form, name=name, email=email, password=password, all=all)

@app.route('/home', methods=["GET", "POST"])
@login_required
def home():
    return render_template('home.html')


@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash('you have been logged out.', category='success')
    return redirect(url_for('authenticate'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/model', methods=['GET', 'POST'])
@login_required
def model():
    nitrogen = None
    phosphorous = None
    potassium = None
    temperature = None
    humidity = None
    soil_ph = None
    rainfall = None

    form = pouchs()

    global a,b,c,d,e,f

    if form.validate_on_submit():
        nitrogen = form.nitrogen.data
        phosphorous = form.phosphorous.data
        potassium = form.potassium.data
        temperature = form.temperature.data
        humidity = form.humidity.data
        soil_ph = form.soil_ph.data
        rainfall = form.rainfall.data

        form.nitrogen.data = ""
        form.phosphorous.data = ""
        form.potassium.data = ""
        form.temperature.data = ""
        form.humidity.data = ""
        form.soil_ph.data = ""
        form.rainfall.data = ""

    if request.method == "POST":
        nitrogen = int(request.form["nitrogen"])
        phosphorous = int(request.form["phosphorous"])
        potassium = int(request.form["potassium"])
        temperature = float(request.form["temperature"])
        humidity = float(request.form["humidity"])
        soil_ph = float(request.form["soil_ph"])
        rainfall = float(request.form["rainfall"])

        return redirect(url_for('predict', a=nitrogen, b=phosphorous, c=potassium, d=temperature , e=humidity, f=soil_ph, h=rainfall))
    
    else:
        return render_template('model.html', form=form)


   
#<a>/<b>/<c>/<d>/<e>/<f>/<h>'

@app.route('/predict/<a>/<b>/<c>/<d>/<e>/<f>/<h>', methods=['POST', 'GET'])
@login_required
def predict(a, b, c, d, e, f, h):

 input_data = np.array([[a, b, c, d, e, f, h]], dtype=np.float32)
 prediction = model(input_data)
 #prediction = prediction.numpy()[0][0]
 #prediction = np.array(prediction).reshape(1, -1)

 y_pred = le.inverse_transform(np.argmax(prediction, axis=1))

 return render_template('predictions.html', a=a, b=b, c=c, d=d, e=e, f=f, h=h, prediction=y_pred)



#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


#????????????????????????????????????????????????????????
#????????????????????????????????????????????????????????
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)

#????????????????????????????????????????????????????????    
#????????????????????????????????????????????????????????