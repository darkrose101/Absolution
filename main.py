import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, PasswordField 
from wtforms.validators import DataRequired, EqualTo, Email
from werkzeug.security import generate_password_hash, check_password_hash

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

class users(db.Model):
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



#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


@app.before_first_request
def load_model():
    global model
    model = tf.keras.models.load_model(path)


@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    email = None
    password = None
    passed = None
    user = None
    
    form = suck()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = users.query.filter_by(email=email).first()
        passed = check_password_hash(user.password, password)

        form.email.data = ''
        form.password.data = ''

        if passed == True:
            flash(f"Successful log in, Welcome back {user.name}", category='success')
            return redirect(url_for('home'))
        else:
            flash('Wrong Password! Kindly retry...', category='error')
            return render_template('auth.html', form=form, email=email, password=password)
    
    return render_template('auth.html', form=form, email=email, password=password)



@app.route('/sign', methods=['GET', 'POST'])
def sign():
    name = None
    email = None
    password = None
    
    form = log()

    if form.validate_on_submit():
        user = users.query.filter_by(email=form.email.data).first()
        if user:
            flash(f"{name}, Email already exist! Choose another")
            return redirect(url_for('sign'))
        else:
            user = users(name=form.name.data, email=form.email.data, password=generate_password_hash(form.password.data, "sha256"))
            db.session.add(user)
            db.session.commit()
            

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
            db.session.commit()
            flash(f"Changes applied successfully, {user.name}")
            return redirect(url_for('home'))
        except:
            flash("A problem occured, retry again")
            return render_template('update.html', form=form, user=user, id=id)    
    else:
        return render_template('update.html', form=form, user=user, id=id)  

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
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/model', methods=['GET', 'POST'])
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