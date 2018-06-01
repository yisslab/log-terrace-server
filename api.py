from flask import Flask, render_template
from flask_restplus import Resource, Api
from flask_restplus import fields
from flask_restplus import reqparse
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logs.sqlite3'
api = Api(app)
socket_io = SocketIO(app)

db = SQLAlchemy(app)

from log_storage import LogStorage
log_storage = LogStorage()

log_request = api.model('LogRequest', {
    'device_id': fields.String,
    'msg': fields.String,
})

log_response = api.model('LogResponse', {
    'id': fields.Integer,
    'device_id': fields.String,
    'time': fields.DateTime,
    'msg': fields.String
})

parser = reqparse.RequestParser()
parser.add_argument('device_id', required=True, location='json')
parser.add_argument('msg', required=True, location='json')


@api.route('/log')
class LogTerrace(Resource):

    @api.expect(log_request)
    @api.marshal_with(log_response)
    def post(self):
        args = parser.parse_args()
        res = log_storage.save(args['device_id'], args['msg'])

        message = dict()
        message['body'] = res.device_id + ' - ' + res.time.strftime('%Y-%m-%d %H:%M:%S') + ' - ' + res.msg

        send(message, broadcast=True, namespace='/')

        return res


device_response = api.model('DeviceResponse', {
    'device_id': fields.String,
    'count': fields.Integer
})


@api.route('/devices')
class DeviceList(Resource):
    @api.marshal_list_with(device_response)
    def get(self):
        return log_storage.get_device_list()


@api.route('/devices/<string:device_id>')
class Device(Resource):
    @api.marshal_list_with(log_response)
    def get(self, device_id):
        return log_storage.read(device_id)


@app.route('/terminal')
def tail():
    return render_template('terminal.html')
