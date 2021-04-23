from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send, join_room, leave_room, ConnectionRefusedError, Namespace


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    return render_template('index.html')
#for handling messages as strings
@socketio.on('message')
def handle_message(data):
    print('recieved message ' + data)
    #send is used in unnamed events
    send(message)


#for handling messages as JSON
@socketio.on('json')
def handle_json_message(json):
    print('recieved json:' + str(json))
    #send is used in unnamed events and if using Json need to specify json -true
    send(json, json=True)

# for flexibility you can use custom events to take string,bytes, int or json

@socketio.on('my event')
def handle_my_custom_event(json):
    print('recieved json' + str(json))
    #we use emit for named events
    emit("my response", json)

#ccustom events can take mutiple arguments
@socketio.on('my custom event')
def handle_my_custom_event_multiple_args(arg1, arg2, arg3):
    print('recieved args: ' + arg1 + arg2 + arg3)
    #you can send multiple arguments using tuples
    emit('my response', (arg1, arg2, arg3))

#names that are reserved for events and cannot be used for custom events message, json, connect and disconnect

#can set up namespaces which allow the ckint to have multipe connections the same physical socket independently
#when a namespace is not specified it defaults to '/'
@socketio.on('namespace event', namespace='/test')
def handle_my_custom_namespace_event(json):
    print('recieved json ' + str(json))
    #you can specify namespaces
    emit('my response', json, namespace='/test')

#in cases where you do not want to use decorator syntax you can use on_event method

def my_function_handler(data):
    pass

socketio.on_event('my function event', my_function_handler, namespace='/test')

#clients can request acknowledgement that the message was recieved, any value returned from the handler function will be passed as an argument to
#the client callback function, if returned with no value will be called with no argument and it can handle multiple arguments

def ack():
    print('recieved from client')

@socketio.on('my callback event')
def handle_my_callback(json):
    print('recieved json ' + str(json))
    #you can specify a callback to get acknowlgements from the client
    emit('my response', json, callback=ack)
    return 'recieved'

#you can specify the optional argument broadcast, when the broadcast option is set to true it is sent to all people connected to the namespace and
# if no namespace is specified it will be sent to all connected clients to the global space, callbacks are not invoked for broadcast
@socketio.on('my broadcast event')
def handle_my_broadcast(json):
    emit('my response', json, broadcast=True)

#in the event you need to have messages originate from the server in the case of notifications
#if there is no client conext specified broadcast = true is assumed
def from_server():
    socketio.emit('from server', {'data': 'hello from server'})

# the room functions can be used in a chat app with multiple chat rooms
#the optional 'to' argument can be used tosend the message to all clients connected to a given room
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' joined the chat', to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' left the chat', to=room)

#all clients are assigned to a room when they connect named with the session id of the connection which ccan be obtained from the request.sid
# a given client can join any room which can have any name, when a client disconnects they leave all the rooms they were in
# the context-free send and emit can also use the 'to' argument to send the message to all clients connected to a room
# since all clients are assigned a personall room, to address a message to a single client the session ID of the client can be used as the 'to' argument


#socket io dispatches connection events as well as disconnect events
#connection and disconnection events are sent individually to each namespace used
@socketio.on('connect')
def on_connect():
#connection refused error can be used for refusing a lient based on authentication
    # if not self.authenticate(request.args):
    #     raise ConnectionRefusedError('You Shall Not Pass!!!!!!')
    emit('my response', {'data':'connected'})

@socketio.on('disconnect')
def on_disconnect():
    print('disconnected client')

#class based namespaces
class MyCustomNamespace(Namespace):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_my_event(self, data):
        emit('my response', data)

socketio.on_namespace(MyCustomNamespace('/test'))

# Handles the default namespace
@socketio.on_error()
def error_handler(e):
    pass
# handles the '/chat' namespace
@socketio.on_error('/chat')
def error_handler_chat(e):
    pass
# handles all namespaces without an explicit error handler
@socketio.on_error_default
def default_error_handler(e):
    pass

if __name__ == '__main__':
    socketio.run(app)
