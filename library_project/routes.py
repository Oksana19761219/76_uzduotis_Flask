from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, logout_user, login_user, login_required
import library_project.forms as forms
from library_project.functions import save_image, send_reset_email
from library_project.database import User, Bibliography
from library_project import app, db, bcrypt, login_manager


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


@app.route('/library_records')
@login_required
def records():
    # page = request.args.get('page', 1, type=int)
    # records = Bibliography.query.filter_by(user_id=current_user.id).paginate(page=page, per_page=2)
    records = Bibliography.query.filter_by(user_id=current_user.id)
    return render_template('library_records.html', records=records)
    # return render_template('library_records.html')



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


# @app.route("/delete/<int:id>")
# def delete(id):
#     record = Bibliography.query.get(id)
#     db.session.delete(record)
#     db.session.commit()
#     return redirect(url_for('bibliography'))
#
#
# @app.route('/update/<int:id>', methods=['GET', 'POST'])
# def update(id):
#     form = forms.BibliographyForm()
#     record = Bibliography.query.get(id)
#     if form.validate_on_submit():
#         record.author = form.author.data
#         record.title = form.title.data
#         record.year = form.year.data
#         db.session.commit()
#         return redirect(url_for('bibliography'))
#     return render_template('update.html', form=form, record=record)


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

