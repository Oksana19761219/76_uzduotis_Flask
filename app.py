import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, UserMixin, current_user, logout_user, login_user, login_required
import secrets
from PIL import Image
import forms
from flask_mail import Message, Mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer



basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = '8752e4durtxkseoem73s4ayr'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'library.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'register'
login_manager.login_message_category = 'info'



class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column('name', db.String(50), unique=True, nullable=False)
    email = db.Column('email', db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(50), nullable=False, default='default.jpg')
    password = db.Column('password', db.String(50), unique=True, nullable=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


class Bibliography(db.Model):
    __tablename__ = 'bibliography'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(250))
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')



class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.el_pastas == 'o.valioniene@gmail.com'

admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(ModelView(Bibliography, db.session))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        encoded_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data, password=encoded_password)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', title='register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login failed. Check your email and password', 'danger')
    return render_template('login.html', title='login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# @app.route('/admin')
# @login_required
# def admin():
#     return redirect(url_for('admin'))


@app.route('/bibliography')
@login_required
def records():
    page = request.args.get('page', 1, type=int)
    records = Bibliography.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=10)
    return render_template('bibliography1.html', records=records)



@app.route("/new_record", methods=['GET', 'POST'])
def add_record():
    form = forms.BibliographyForm()
    if form.validate_on_submit():
        new_record = Bibliography(author=form.author.data,
                                  title=form.title.data,
                                  year=form.year.data,
                                  user_id=current_user.id)
        db.session.add(new_record)
        db.session.commit()
        flash(f'Record created', 'success')
        return render_template('new_record.html', form=form)
    return render_template('new_record.html', form=form)


@app.route("/delete/<int:id>")
def delete(id):
    record = Bibliography.query.get(id)
    db.session.delete(record)
    db.session.commit()
    return redirect(url_for('bibliography'))


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = forms.BibliographyForm()
    record = Bibliography.query.get(id)
    if form.validate_on_submit():
        record.author = form.author.data
        record.title = form.title.data
        record.year = form.year.data
        db.session.commit()
        return redirect(url_for('bibliography'))
    return render_template('update.html', form=form, record=record)



def save_image(form_image):
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_image.filename)
    image_filename = random_hex + file_extension
    image_path = os.path.join(app.root_path, 'static/images', image_filename)

    output_size = (150, 150)
    image = Image.open(form_image)
    image.thumbnail(output_size)
    image.save(image_path)

    return image_filename


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = forms.AccountUpdateForm()
    if form.validate_on_submit():
        if form.image.data:
            image = save_image(form.image.data)
            current_user.image = image
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    image = url_for('static', filename='images/' + current_user.image)
    return render_template('account.html', title='Account', form=form, image=image)





app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = MAIL_USERNAME
# app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
mail = Mail(app)


def send_reset_email(user):
    token = user.get_reset_token()

    # msg = Message('Slaptažodžio atnaujinimo užklausa',
    #               sender='o.valioniene.testinis@gmail.com',
    #               recipients=[user.email])
    # msg.body = f'''Norėdami atnaujinti slaptažodį, paspauskite nuorodą:
    # {url_for('reset_token', token=token, _external=True)}
    # Jei jūs nedarėte šios užklausos, nieko nedarykite ir slaptažodis nebus pakeistas.
    # '''
    # mail.send(msg)



@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = forms.QueryUpdateForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Password reset instructions sent to your email', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('The request is invalid or has expired', 'warning')
        return redirect(url_for('reset_request'))
    form = forms.PasswordUpdateForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! Can login', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)









db.create_all()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
