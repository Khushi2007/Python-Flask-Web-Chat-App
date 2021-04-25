import json
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user, LoginManager, UserMixin


with open('config.json', 'r') as c:
    params = json.load(c)["params"]


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Shadowhunters: The Mortal Instruments'
app.config['UPLOAD_FOLDER'] = params['upload_location']

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/test_db'
db = SQLAlchemy(app)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))


class Chats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receiver_id = db.Column(db.Integer)
    sender_id = db.Column(db.Integer)
    message = db.Column(db.String(5000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())


class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    profile_image = db.Column(db.String(255))


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))


@app.route('/')
@login_required
def home():
    return render_template('home.html', user=current_user)


@app.route('/profile')
@login_required
def profile():
    current_user_id = current_user.id
    image = Profiles.query.filter_by(user_id=current_user_id).first()
    return render_template('profile.html', user=current_user, image=image)


@app.route('/all-users', methods=['POST', 'GET'])
@login_required
def all_users():
    users = Users.query.order_by(Users.first_name)
    profiles = Profiles.query.order_by(Profiles.user_id)
    return render_template('all-users.html', user=current_user, users_list=users, profiles=profiles)


@app.route('/search', methods=['POST', 'GET'])
@login_required
def search():
    if request.method == 'POST':
        received = request.form.get('search')
        if len(received) < 1:
            flash('You cannot do an empty search!', category='error')
        else:
            searched = received.lower()
            return redirect(url_for('result', searched=searched))

    return render_template('search.html',  user=current_user)


@app.route('/result/<string:searched>')
def result(searched):
    users = Users.query.order_by(Users.id)
    profiles = Profiles.query.order_by(Profiles.user_id)
    return render_template('result.html', all_users=users, searched=searched, user=current_user, profiles=profiles)


@app.route('/chat/<int:user_chat_id>', methods=['POST', 'GET'])
@login_required
def chat(user_chat_id):
    chat_user = Users.query.filter_by(id=user_chat_id).first()
    messages = Chats.query.order_by(Chats.date)
    current_user_profile = Profiles.query.filter_by(user_id=current_user.id).first()
    chat_user_profile = Profiles.query.filter_by(user_id=user_chat_id).first()

    if request.method == 'POST':
        message = request.form.get('message')

        if len(message) < 1:
            flash('Please type a message to continue!', category='error')
            return render_template('chat.html', user=current_user, chat_user=chat_user, messages=messages)

        else:
            new_message = Chats(receiver_id=chat_user.id, sender_id=current_user.id, message=message)
            db.session.add(new_message)
            db.session.commit()

    return render_template('chat.html', user=current_user, chat_user=chat_user, messages=messages, profile=current_user_profile, chat_user_profile=chat_user_profile)


@app.route('/delete/<int:message_id>/<int:user_chat_id>')
def delete_message(message_id, user_chat_id):
    message_to_delete = Chats.query.get_or_404(message_id)

    try:
        db.session.delete(message_to_delete)
        db.session.commit()

    except:
        flash('There was a problem deleting that message!', category='error')

    return redirect(url_for('chat', user_chat_id=user_chat_id))


@app.route('/edit/<int:message_id>/<int:user_chat_id>', methods=['POST', 'GET'])
def edit_message(message_id, user_chat_id):
    message_to_edit = Chats.query.get_or_404(message_id)

    if request.method == 'POST':
        new_edit_message = request.form.get('message')

        if new_edit_message == "":
            flash('Message can\'t be empty!', category='error')
            return render_template('edit-message.html', user=current_user, message_to_edit=message_to_edit)

        elif new_edit_message == message_to_edit.message:
            flash('Please make some change in the message to edit it!', category='error')
            return render_template('edit-message.html', user=current_user, message_to_edit=message_to_edit)

        else:
            message_to_edit.message = new_edit_message

            try:
                db.session.commit()
                return redirect(url_for('chat', user_chat_id=user_chat_id))

            except:
                flash('There was a problem editing that message', category='error')
    else:
        return render_template('edit-message.html', user=current_user, message_to_edit=message_to_edit,
                               user_chat_id=user_chat_id)


@app.route('/chat-list')
def chat_list():
    messages = Chats.query.order_by(Chats.date)
    users = Users.query.order_by(Users.first_name)

    return render_template('chat-list.html', user=current_user, messages=messages, users_list=users)


@app.route('/forward/<int:message_id>/<int:user_chat_id>')
def forward_message(message_id, user_chat_id):
    message_to_forward = Chats.query.get_or_404(message_id)
    users = Users.query.order_by(Users.first_name)

    return render_template('forward-message.html', user=current_user, message_to_forward=message_to_forward,
                           users_list=users, user_chat_id=user_chat_id)


@app.route('/forward-method/<int:chat_user_id>/<string:message>')
def forward_method(chat_user_id, message):
    forwarded_message = Chats(receiver_id=chat_user_id, sender_id=current_user.id, message=message)
    db.session.add(forwarded_message)
    db.session.commit()

    return redirect(url_for('chat', user_chat_id=chat_user_id))


@app.route('/reply/<int:message_id>/<int:chat_user_id>', methods=['POST', 'GET'])
def reply_message(message_id, chat_user_id):
    message_to_reply_to = Chats.query.get_or_404(message_id)
    chat_user = Users.query.get_or_404(chat_user_id)

    if message_to_reply_to.sender_id == current_user.id:
        message_by = 'you'
    else:
        message_by = chat_user.first_name + ' ' + chat_user.last_name

    if request.method == 'POST':
        message_reply = request.form.get('message')
        if len(message_reply) < 1:
            flash('Reply cannot be empty! Please type a reply to continue!', category='error')
        else:
            final_reply = 'Replying to: "' + message_to_reply_to.message + '" by ' + message_by + '.\n   The reply is: ' + message_reply
            replied_message = Chats(receiver_id=chat_user.id, sender_id=current_user.id, message=final_reply)
            db.session.add(replied_message)
            db.session.commit()
            return redirect(url_for('chat', user_chat_id=chat_user_id))

    return render_template('reply.html', message_to_reply_to=message_to_reply_to, chat_user=chat_user, user=current_user)


@app.route('/uploader', methods=['POST', 'GET'])
def uploader():
    if request.method == 'POST':
        profile_image = request.files['profile']
        image = secure_filename(profile_image.filename)
        profile_image.save(os.path.join(app.config['UPLOAD_FOLDER'], image))

        new_profile_image = Profiles(user_id=current_user.id, profile_image=image)
        db.session.add(new_profile_image)
        db.session.commit()

        flash('Profile image uploaded successfully!', category='success')
        return redirect(url_for('profile'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = Users.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('home'))
            else:
                flash('Incorrect password. Try again!', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template('login.html', user=current_user)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = Users.query.filter_by(email=email).first()

        if user:
            flash('Email already exists.', category='error')

        elif len(username) < 2:
            flash('Username must be greater than 1 character', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character', category='error')
        elif len(lastName) < 2:
            flash('Last name must be greater than 1 character', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters', category='error')
        elif len(password1) < 6:
            flash('Password must be at least 6 characters long', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error')

        else:
            new_user = Users(username=username, first_name=firstName, last_name=lastName, email=email,
                             password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Account created successfully!', category='success')
            return redirect(url_for('home'))

    return render_template('register.html', user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
