from flask import Flask, render_template, redirect, url_for, flash #import flask framework and render_template function
from flask_sqlalchemy  import SQLAlchemy    # import SQLAlchemy for database management
from flask_login   import UserMixin #import UserMixin for user session management
from flask_login import LoginManager, login_user, login_required, logout_user, current_user #import LoginManager for user session management
import os # import os module for operating system dependent functionality like path manipulation
from flask_wtf import FlaskForm # import FlaskForm for form handling
from wtforms import StringField, PasswordField, SubmitField, BooleanField # import form fields from wtforms
from wtforms.validators import input_required, Length, ValidationError# import validators for form fields
from flask_bcrypt import Bcrypt# import functions for password hashing and checking

# Create a Flask application instance with instance-relative configuration
# The instance folder is a place where you can store files that are specific to this instance of the application
app = Flask(__name__, instance_relative_config=True) # Create a Flask application instance

# Initialize Flask-Bcrypt for password hashing
bcrypt = Bcrypt(app) # Initialize Flask-Bcrypt  for password hashing

# path to the database inside the instance folder
db_path= os.path.join(app.instance_path, 'database.db')
# ensure that the instance folder exists
if not os.path.exists(app.instance_path):
    os.makedirs(app.instance_path, exist_ok=True) # Create the instance folder if it does not exist, allowing existing folders to be ignored

# configure sqlite
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}" # Set the database URI to use SQLite and point to the database file in the instance folder
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable track modifications to save resources
app.config['SECRET_KEY'] = '123456789'# Secret key for session management

db = SQLAlchemy(app) # Initialize SQLAlchemy


# Initialize Flask-Login
login_manager = LoginManager() # Create an instance of LoginManager
login_manager.init_app(app) # Initialize the LoginManager with the Flask app    
login_manager.login_view = 'login' # Set the login view to the 'login' endpoint, which is the route for the login page
# The login_view is the endpoint that Flask-Login will redirect to when a user tries to access a protected route without being logged in


# The User class is a model that represents a user in the database
# The UserMixin class provides default implementations for the methods required by Flask-Login
# Creating tables in db 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True) # username must be unique and cannot be null
    email = db.Column(db.String(120), unique=True, nullable=False) # email must be unique
    password = db.Column(db.String(80), nullable=False)

# The registratioForm class defines the fields and validation rules for the registration form
class registratioForm(FlaskForm): # Create a registration form using Flask-WTF
    username = StringField(validators=[input_required(), Length(min=4, max=20)], render_kw={"placeholder": "Username"}) # Username field with validation
    email = StringField(validators=[input_required(), Length(min=6, max=120)], render_kw={"placeholder": "Email"}) # Email field with validation
    password = PasswordField(validators=[input_required(), Length(min=6, max=20)], render_kw={"placeholder": "Password"}) # Password field with validation
    submit = SubmitField('Register') # Submit button for the form

    def validate_usename(self, username):
        exisitng_user_name = User.query.filter_by(username=username.data).first()
        if exisitng_user_name: # Check if the username already exists in the database
            raise ValidationError('Username already exists, please use another one') # Raise a validation error if it does
        
    def validate_email(self, email):
        existing_email = User.query.filter_by(email=email.data).first()
        if existing_email: # Check if the email already exists in the database
            raise ValidationError('Email already exists, please use another one') # Raise a validation error if it does
        

# The loginForm class defines the fields and validation rules for the login form
class loginForm(FlaskForm): # Create a login form using Flask-WTF
    username = StringField(validators=[input_required(), Length(min=4, max=20)], render_kw={"placeholder": "Username"}) # Username field with validation
    password = PasswordField(validators=[input_required(), Length(min=6, max=20)], render_kw={"placeholder": "Password"}) # Password field with validation
    submit = SubmitField('Login') # Submit button for the form

    
#Initialize the database
with app.app_context(): #Enter the app context so that we can use the app's configuration
    db.create_all() #creates the tables  for all models if they dont exists 


# The load_user function is used by Flask-Login to load a user from the user ID stored in the session   
@login_manager.user_loader # Decorator to load a user from the user ID stored in the session
def load_user(user_id): # Function to load a user by their ID
    return User.query.get(int(user_id)) # Query the database for the user with the given ID and return it
# The load_user function is called by Flask-Login to load the user object from the database
# The user object is then stored in the session, allowing you to access the current user with current_user




# define routes and urls 

@app.route('/',endpoint='index') # defines the root url route
def home(): #vie function for /(homepage)
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/contact')  
def contact():
    return render_template('contact.html')
@app.route('/shop')
def shop():
    return render_template('shop.html')
@app.route('/login', methods=['GET', 'POST']) # route for login page, allows both GET and POST requests
def login():
    form = loginForm()
    if form.validate_on_submit(): # check if the form is submitted and valid
        user = User.query.filter_by(username=form.username.data).first() # query the database for the user with the given username
        if user and bcrypt.check_password_hash(user.password,   form.password.data):
            login_user(user)
            flash("You are now logged in!", "success") # flash a success message to the user
            return redirect(url_for("index"))# log in the user and redirect to the home page
        else:
            return render_template('login.html', form=form, error='Invalid username or password')

    return render_template('login.html', form=form) # render the login template with the form


@app.route('/register', methods=['GET', 'POST']) # route for registration page, allows both GET and POST requests
def register():
    form = registratioForm()

    if form.validate_on_submit(): # check if the form is submitted and valid

        hashed_password= bcrypt.generate_password_hash(form.password.data).decode('utf-8') # hash the password using Flask-Bcrypt
        new_user = User(
            username=form.username.data, # get the username from the form
            email=form.email.data, # get the email from the form
            password=hashed_password # set the hashed password
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        # flash a success message to the user
        return render_template('login.html', form=loginForm())

    return render_template('register.html', form=form) # render the registration template with the form

@app.route('/logout') # route for logout
@login_required # requires the user to be logged in to access this route
def logout():
    logout_user() # log out the user
    return render_template('index.html') # redirect to the home page after logging out
    

if __name__ == '__main__': # run this only when executing 'python3 app.py ' / 'flask run' 
    app.run(debug=True) # debug=True enables debug mode, which provides detailed error messages and auto-reloads the server on code changes

