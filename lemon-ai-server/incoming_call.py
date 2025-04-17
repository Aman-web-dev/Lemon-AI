from flask import request, Blueprint
import json
import logging
import socketio
import threading

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

incoming_call_app = Blueprint("incoming_call", __name__)

# Store socket connection
socket_connection = None

def get_socket():
    global socket_connection
    if socket_connection is None:
        try:
            socket_connection = socketio.Client()
            # Register event handlers before connecting
            register_handlers(socket_connection)
            socket_connection.connect("http://localhost:9000")
            logger.info("SocketIO connection established")
            # Start a thread to keep the connection alive and process events
            threading.Thread(target=socket_connection.wait, daemon=True).start()
        except Exception as e:
            logger.error(f"Failed to connect to SocketIO server: {e}")
            raise
    return socket_connection




def register_handlers(sio):
    @sio.on("message")
    def on_message(data, *args):
        logger.info(f"Received raw message: {data}")  # Log raw data for debugging
        print("I got a message:", data,*args)
        try:
            if isinstance(data, str):
                # Try to parse as JSON only if it looks like JSON
                if data.startswith('{') or data.startswith('['):
                    msg_data = json.loads(data)
                    logger.info(f"Parsed message: {msg_data}")
                    # Example reply with JSON
                    reply = {"type": "response", "body": f"Received: {msg_data}"}
                    sio.emit("reply", json.dumps(reply))
                    logger.info(f"Sent reply: {reply}")
                else:
                    logger.info(f"Plain string message: {data}")
                    # Handle plain string (no JSON parsing)
                    reply = {"type": "response", "body": f"Received: {data}"}
                    sio.emit("reply", json.dumps(reply))
                    logger.info(f"Sent reply for plain text: {reply}")
            else:
                logger.info(f"Non-string message (e.g., dict): {data}")
                # Handle non-string data (e.g., dict or list)
                reply = {"type": "response", "body": f"Received: {data}"}
                sio.emit("reply", json.dumps(reply))
                logger.info(f"Sent reply for non-JSON: {reply}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in message: {e}, Raw data: {data}")
            # Handle invalid JSON with raw data
            sio.emit("reply", json.dumps({"type": "error", "body": f"Invalid JSON: {data}"}))

# Rest of your code remains the same


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
        
        socket = get_socket()
        print(socket)

        obj = {
            "channelName": channel_name,
            "userId": "python_server"
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
        send("pick_call", {"userId": "python_server"})
        return {"message": "Call picked"}, 200
    except Exception as e:
        logger.error(f"Error in pick_call: {e}")
        return {"error": str(e)}, 500