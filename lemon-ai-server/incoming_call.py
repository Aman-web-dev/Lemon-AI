
from flask import request, Blueprint
import json
import logging
import socketio


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

incoming_call_app = Blueprint("incoming_call", __name__)

# Store socket connection (consider using a proper connection pool for production)
socket_connection = None

def get_socket():
    global socket_connection
    if socket_connection is None:
        try:
            socket_connection = socketio.Client()
            socket_connection.connect("http://localhost:9000")
            print(socket_connection)
            logger.info("SocketIO connection established")
        except Exception as e:
            logger.error(f"Failed to connect to SocketIO server: {e}")
            raise
    return socket_connection

def send(type, body):
    try:
        socket = get_socket()
        message = {
            "type": type,
            "body": body
        }

        socket.emit('chat message', json.dumps(message))
        logger.info(f"Sent message: {message}")
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise

@incoming_call_app.route("/room", methods=["POST"])
def connect_to_room():
    try:
        data = request.get_json()
        if not data or "body" not in data or "channelName" not in data["body"]:
            return {"error": "Invalid request: channelName is required"}, 400

        channel_name = data["body"]["channelName"]
        logger.info(f"Received request to join room: {channel_name}")
        
        socket=get_socket()
        print(socket)

        obj = {
            "channelName": channel_name,
            "userId": 12442  # Replace with dynamic user ID logic
        }
        send("join", obj)

        return {"message": f"Connected to room {channel_name}"}, 200

    except Exception as e:
        logger.error(f"Error in connect_to_room: {e}")
        return {"error": str(e)}, 500

@incoming_call_app.route("/call", methods=["POST"])
def pick_call():
    try:
        logger.info("Received call pick request")
        # Add logic to handle picking a call (e.g., emit a SocketIO event)
        return {"message": "Call picked"}, 200
    except Exception as e:
        logger.error(f"Error in pick_call: {e}")
        return {"error": str(e)}, 500

# # Optional: Cleanup on app shutdown
# @incoming_call_app.teardown_app_request
# def cleanup(exception=None):
#     global socket_connection
#     if socket_connection is not None:
#         # Close SocketIO connection gracefully (if supported by socketIO_client)
#         socket_connection.disconnect()
#         socket_connection = None
#         logger.info("SocketIO connection closed")