from App import app , socketio
# Run face detection in a background thread


if __name__ == '__main__':
    socketio.run(app,host='0.0.0.0', debug=True, port=5000)
