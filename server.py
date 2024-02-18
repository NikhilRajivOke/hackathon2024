from flask import Flask, jsonify, request
# from flask.globals import _app_ctx_stack
from flask_cors import CORS
from flask import g

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes in the app

currentNumber = 0

@app.route('/', methods=['GET'])
def get_value():
    global currentNumber
    value = currentNumber
    if value is not None:
        return jsonify({'value': value}), 200
    else:
        return jsonify({'error': 'Value not set'}), 404

@app.route('/', methods=['PUT'])
def update_value():
    # ctx = _app_ctx_stack.top
    value = request.json.get('value', None)
    if value is not None:
        global currentNumber
        currentNumber = value
        print('value Updated' + str(value))
        return jsonify({'message': 'Value updated'}), 200
    else:
        return jsonify({'error': 'Value not provided in request'}), 400

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

