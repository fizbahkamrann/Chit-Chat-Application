from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chitchat_key'
socketio = SocketIO(app)

chat_history = []
active_users = 0

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    global active_users
    active_users += 1
    emit('status_msg', {'msg': 'A user joined the chat'}, broadcast=True)
    emit('user_count', {'count': active_users}, broadcast=True)
    emit('load_history', chat_history)

@socketio.on('disconnect')
def handle_disconnect():
    global active_users
    active_users -= 1
    emit('status_msg', {'msg': 'A user left the chat'}, broadcast=True)
    emit('user_count', {'count': active_users}, broadcast=True)

@socketio.on('message')
def handle_message(data):
    data['id'] = str(uuid.uuid4())
    data['time'] = datetime.now().strftime('%H:%M')
    chat_history.append(data)
    if len(chat_history) > 50: chat_history.pop(0)
    emit('message', data, broadcast=True)

@socketio.on('typing')
def handle_typing(data):
    emit('is_typing', data, broadcast=True, include_self=False)

@socketio.on('delete_message')
def handle_delete(data):
    global chat_history
    chat_history = [m for m in chat_history if m['id'] != data['id']]
    emit('remove_message', {'id': data['id']}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)