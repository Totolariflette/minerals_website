import os.path

from flask import Flask, render_template, url_for, redirect, request, flash
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_bcrypt import Bcrypt

from models import db, User
from forms import RegisterForm, LoginForm
from algos import save_file, uploads_path, get_nns_directories_name, apply_nn_on_image

from PIL import Image
from threading import Thread

Image.MAX_IMAGE_PIXELS = None
FLASK_DEBUG = 1
# Paths
db_path = '../db/login.db'

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

original_uploaded_filename = ""


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


@app.route('/upload_image', methods=['GET', 'POST'])
@login_required
def upload_image():
    global original_uploaded_filename
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('choose_file'))
    selected_file = request.files['file']
    if selected_file.filename == '':
        flash('No image selected for uploading')
        return redirect(url_for('choose_file'))

    if selected_file and selected_file.filename.split('.')[-1] in supported_image_types:
        original_uploaded_filename = selected_file.filename
        display_image_filename = save_file(selected_file)

        return render_template('choose_file.html', display_image_filename=display_image_filename,
                               filename=selected_file.filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg')
        return redirect(url_for('choose_file'))


@app.route('/display/<filename>')
def display_image(filename):
    return redirect(url_for('static', filename='uploads/' + filename))


@app.route('/select_model/<display_image_filename>', methods=['GET', 'POST'])
@login_required
def select_model(display_image_filename):
    return render_template('select_model.html', display_image_filename=display_image_filename,
                           nns=get_nns_directories_name())


@app.route('/apply_model/<nn>', methods=['GET', 'POST'])
@login_required
def apply_model(nn):
    if original_uploaded_filename != "":
        apply_nn_on_image(nn, original_uploaded_filename)
        return render_template('apply_model.html')
    else:
        return redirect(url_for('choose_file'))


@app.route('/main')
@login_required
def main():
    return render_template('main.html')


@app.route('/test')
def test():
    return render_template('base.html')


if __name__ == "__main__":
    app.run(debug=True)
