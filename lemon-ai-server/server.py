from flask import Flask;
from incoming_call import incoming_call_app

app = Flask(__name__)

app.register_blueprint(incoming_call_app)

@app.route("/")
def hello_world():
    
    return "<h1>hello World</h1>"

if __name__ == '__main__':
    app.run()