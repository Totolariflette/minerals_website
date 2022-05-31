import os.path

from flask import Flask, render_template, url_for, redirect, request, flash
from flask_login import UserMixin, LoginManager, login_required, logout_user, current_user, login_user
from flask_bcrypt import Bcrypt

from models import db, User
from forms import RegisterForm, LoginForm

# Paths
db_path = '../db/login.db'
uploads_path = "static/uploads"

# Constants
basedir = os.path.abspath(os.path.dirname(__file__))
supported_image_types = ['jpg', 'jpeg', "png"]

# Init the app
app = Flask(__name__)
db.init_app(app)
# Init the encryptor for the passwords
bcrypt = Bcrypt(app)
# Init the sqlite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SECRET_KEY'] = 'mykey'

# Init the dropzone in the main page
app.config.update(UPLOADED_PATH=uploads_path, DROPZONE_MAX_FILE_SIZE=1024,
                  DROPZONE_TIMEOUT=5 * 60 * 1000)

# Init the login manager for the login session
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('main'))

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/choose_file', methods=['GET', 'POST'])
@login_required
def choose_file():
    return render_template('choose_file.html')


@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('choose_file'))
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(url_for('choose_file'))

    if file and file.filename.split('.')[-1] in supported_image_types:
        file.save(os.path.join(app.config['UPLOADED_PATH'], file.filename))

        flash('Image successfully uploaded and displayed below')
        return render_template('upload_image.html', filename=file.filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(url_for('choose_file'))


@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


@app.route('/main')
def main():
    return render_template('main.html')


@app.route('/test')
def test():
    return render_template('base.html')


if __name__ == "__main__":
    app.run(debug=True)
