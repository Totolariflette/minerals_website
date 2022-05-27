import os.path

from flask import Flask, render_template, url_for, redirect, request
from flask_login import UserMixin, LoginManager, login_required, logout_user, current_user, login_user
from flask_bcrypt import Bcrypt
from flask_dropzone import Dropzone

from models import db, User
from forms import RegisterForm, LoginForm

db_path = '../db/login.db'
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
db.init_app(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SECRET_KEY'] = 'mykey'

app.config.update(UPLOADED_PATH=os.path.join(basedir, 'uploads'), DROPZONE_MAX_FILE_SIZE=1024,
                  DROPZONE_TIMEOUT=5 * 60 * 1000)
dropzone = Dropzone(app)

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


@app.route('/main', methods=['GET', 'POST'])
@login_required
def main():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    return render_template('main.html')


@app.route('/test')
def test():
    return render_template('base.html')


if __name__ == "__main__":
    app.run(debug=True)
