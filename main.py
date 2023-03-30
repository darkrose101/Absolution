from tensorflow.keras.models import load_model
from datetime import datetime
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField, PasswordField 
from wtforms.validators import DataRequired, Email



path = r'C:\Users\USER\Documents\Isis\fun\datasets_models\model.h5'


#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Charlie_dont_surf1000'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c_atoms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------



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
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    
    submit = SubmitField('Dive in😙!')


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

@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    email = None
    password = None
    
    form = log()

    if form.validate_on_submit() and request.method == "POST":
        return render_template('home.html')

    email = form.email.data
    password = form.password.data

    form.email.data = ''
    form.password.data = ''
        

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
            user = users(name=form.name.data, email=form.email.data, password=form.password.data)
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
        nitrogen = float(request.form["nitrogen"])
        phosphorous = float(request.form["phosphorous"])
        potassium = float(request.form["potassium"])
        temperature = float(request.form["temperature"])
        humidity = float(request.form["humidity"])
        soil_ph = float(request.form["soil_ph"])
        rainfall = float(request.form["rainfall"])

        return redirect(url_for('predict', a=nitrogen, b=phosphorous, c=potassium, d=temperature , e=humidity, f=soil_ph, h=rainfall))
    
    else:
        return render_template('model.html', form=form)
    
from tensorflow.keras.models import load_model
path = r'C:\Users\USER\Documents\Isis\fun\datasets_models\model.h5'
@app.route('/predict/<a>/<b>/<c>/<d>/<e>/<f>/<h>',)
def predict(a, b, c, d, e, f, h):

    
    model = load_model(path)
    prediction = model.predict([[a, b, c, d, e, f, h]]) 

    return render_template('predictions.html', prediction=prediction)



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