import socket
import threading
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')
messages = []
connected_users = set()

def handle_message(data):
    print('Mensagem recebida:', data)
    messages.append(data)
    socketio.emit('message', data)

def update_users():
    emit('update_users', list(connected_users), broadcast=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/messages')
def get_messages():
    return jsonify(messages)

@app.route('/messages', methods=['POST'])
def send_message():
    data = request.json
    threading.Thread(target=handle_message, args=(data,)).start()
    return jsonify(data)

@socketio.on('connect')
def connect():
    print('Cliente conectado')

@socketio.on('disconnect')
def disconnect():
    print('Cliente desconectado')
    if request.sid in connected_users:
        connected_users.remove(request.sid)
        update_users()

@socketio.on('message')
def receive_message(data):
    if request.sid not in connected_users:
        connected_users.add(request.sid)
        update_users()
    print('Mensagem recebida:', data)
    messages.append(data)
    emit('message', data, broadcast=True)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 5000))
    server_socket.listen()
    print('Servidor iniciado')
    while True:
        client_socket, client_address = server_socket.accept()
        print(f'Cliente conectado: {client_address}')
        threading.Thread(target=handle_client, args=(client_socket,)).start()

def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            print(f'Cliente desconectado: {client_socket.getpeername()}')
            client_socket.close()
            return
        message = data.decode().strip()
        print(f'Mensagem recebida: {message}')
        threading.Thread(target=handle_message, args=(message,)).start()

def run_socketio_in_thread():
    print('Iniciando servidor Flask')
    socketio.run(app, host='0.0.0.0', port=8000, debug=False)

if __name__ == '__main__':
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=run_socketio_in_thread, daemon=True).start()
    while True:
        pass
