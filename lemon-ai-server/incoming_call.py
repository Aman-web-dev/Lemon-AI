from socketIO_client import SocketIO
from flask import request, Blueprint
import json

incoming_call_app = Blueprint("incoming_call", __name__)


socket_connection = None

def get_socket():
    global socket_connection
    if socket_connection is None:
        socket_connection = SocketIO("localhost", 9000)
    return socket_connection




message=socket_connection.recieve()
print(message)

def send(type_, body):
    socket =get_socket()
    message = {
        "type": type_,
        "body": body
    }
    socket.emit('chat message', json.dumps(message))

@incoming_call_app.route("/room", methods=["POST"])
def connect_to_room():
    global socket_connection
    try:
        data = request.get_json()
        channel_name = data["channelname"]
        print(data, channel_name)

        socket = get_socket()
        send("join_channel",{channel_name:channel_name})

        return "Connected to room"

    except Exception as e:
        print("Error:", e)
        return str(e), 500

@incoming_call_app.route("/call")
def pick_call():
    print("We got a call")
    return "Call picked"
