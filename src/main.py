import json

from flask import Blueprint, render_template, redirect, url_for, flash
from . import db, socketio
from .models import User, Visit, Chat
from flask_login import LoginManager, current_user
from .forms import ChatForm, ReplyForm
from datetime import datetime

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<id>')
def profile(id):
    user = User.query.filter_by(id=id).first_or_404()

    return render_template('profile.html', user=user)

@main.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@main.route('/visit')
def visit_history():
    if current_user.is_authenticated:
        visits = Visit.query.filter_by(user_id=current_user.id).all()
        return render_template('visit_history.html', visits=visits)
    else:
        return redirect(url_for('auth.login'))


@socketio.on('send_message')
def handle_send_message(data):
    message = data['message']
    user_name = data['user_name']
    created_at = datetime.now()
    new_message = Chat(message=message, user_id=current_user.id)
    db.session.add(new_message)
    db.session.commit()
    now = datetime.now()
    json_time = now.strftime("%Y-%m-%d %H:%M:%S")
    data = {"time": json_time}
    json_data = json.dumps(data)
    socketio.emit('receive_message', {'message': message, 'user_name': user_name, 'created_at': json_data}, broadcast=True)

@main.route('/chat', methods=['GET', 'POST'])
def chat():
    form = ChatForm()
    reply_form = ReplyForm()
    if form.validate_on_submit():
        if form.message.data.strip() != "":
            message = Chat(message=form.message.data, user_id=current_user.id)

            db.session.add(message)
            db.session.commit()
            socketio.emit('new_message', {'message': form.message.data, 'username': current_user.name}, broadcast=True)

        else:
            flash("Сообщение пустое", 'danger')
        # flash('Your message has been sent!', 'success')

        return redirect(url_for('main.chat'))
    messages = Chat.query.order_by(Chat.id.desc()).filter(Chat.reply_id == None).paginate(page=1, per_page=10).items
    return render_template('chat.html', form=form, messages=messages, reply_form=reply_form)

@main.route('/chat/reply/<int:message_id>', methods=['POST'])
def reply(message_id):
    form = ReplyForm()
    if form.validate_on_submit():
        reply = Chat(message=form.message.data, user_id=current_user.id, reply_id=message_id)
        db.session.add(reply)
        db.session.commit()
        return redirect(url_for('main.chat'))