from flask import Flask, render_template
from flask_sqlalchemy  import SQLAlchemy
from flask_login   import UserMixin 
import os


app = Flask(__name__) # Create a Flask application instance
basedir = os.path.abspath(os.path.dirname(__file__)) # Get the base directory of the application
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'database.db') # Database URIexit
app.config['SECRET_KEY'] = '123456789'# Secret key for session management

db = SQLAlchemy(app) # Initialize SQLAlchemy

# Creating tables in db 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(80), nullable=False)


@app.route('/',endpoint='index')
def home():
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
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/register')
def register():
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)

