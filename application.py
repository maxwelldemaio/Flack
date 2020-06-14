import os, settings

from time import localtime, strftime
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit, send, join_room, leave_room

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Chat posts (Limit to 100)
posts = []
myRooms = ["Lounge", "Chess", "News", "Coding"]

@app.route("/")
def index():
    """ Homepage """
    return render_template("index.html")

@app.route("/chat")
def chat():
    """ Chat """
    return render_template("chat.html", rooms=myRooms)

@app.route("/posts", methods=["POST"])
def posts():
    pass
    """ AJAX route that obtains posts for chat room """
    
    # Each room will have a list of posts which we will read in
    # We will populate the empty list and fetch them for the client here
    # Read from the text file associated with room
    # NOTE each line has to be ended with a new line, or else the list will be empty

    # IDEA screw the load() function
    # slap that sucker right into the join function in your chat.js file so you know 
    # EXACTLY what is goin' down
    
    # Get channel from client
    channel = request.form.get("channel")
    print(f"{channel}.txt")

    # Populate list of posts
    with open(f"./channels/{channel}.txt", "r") as channel:
        data = channel.read().splitlines()
        print(data)

    # Return list of posts
    return jsonify(data)


## Socket IO event bucket handlers
@socketio.on("message")
def message(data):
    """ Broadcast message, username, and time """
    
    # TODO 
    # Store message related to room in a text file with the name of that room
    # If the CSV file doesn't already exist in rooms dir, create w/ "roomName.csv"
    # Add message, username, time to new line in CSV

    print(data)
    send({"message": data["message"], "username": data["username"], 
    "time": strftime('%b-%d %I:%M%p', localtime()), "room": data["room"]}, room=data["room"])

@socketio.on('join')
def on_join(data):
    """ Upon join (Info received from client), update active users """
    username = data['username']
    room = data['room']
    join_room(room)
    send({"message": username + ' has entered the ' + room + ' room.', "room": room}, room=room)

@socketio.on('leave')
def on_leave(data):
    """ Upon leave (Info received from client), update active users """
    username = data['username']
    room = data['room']
    leave_room(room)
    send({"message": username + ' has left the ' + room + ' room.', "room": room}, room=room)


if __name__ == "__main__":
    socketio.run(app, debug=True)
