import datetime

from api import db


class Device(db.Model):
    device_id = db.Column(db.String(100), primary_key=True)
    count = db.Column(db.Integer)

    def __init__(self, device_id, count):
        self.device_id = device_id
        self.count = count


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(100), primary_key=True)
    time = db.Column(db.DateTime)
    msg = db.Column(db.String(256))

    def __init__(self, log_id, device_id, time, msg):
        self.id = log_id
        self.device_id = device_id
        self.time = time
        self.msg = msg


class LogStorage:

    LOG_MAXIMUM_COUNT = 100

    def read(self, device_id):
        return Log.query.filter_by(device_id=device_id).order_by(Log.time).all()

    def get_device_list(self):
        return Device.query.all()

    def save(self, device_id, msg):
        count = self._get_device_count(device_id)
        if count is None:
            count = self._set_device_count(device_id, 0)

        time = datetime.datetime.now()
        log = Log.query.filter_by(device_id=device_id, id=count).first()
        if log is None:
            log = Log(count, device_id, time, msg)
            db.session.add(log)
        else:
            log.time = datetime.datetime.now()
            log.msg = msg

        db.session.commit()

        count = count + 1
        if count >= self.LOG_MAXIMUM_COUNT:
            count = count - self.LOG_MAXIMUM_COUNT
        self._set_device_count(device_id, count)

        return log

    def _get_key(self):
        return int(self.key)

    def _get_device_count(self, device_id):
        device = Device.query.filter_by(device_id=device_id).first()
        if device is None:
            return None
        else:
            return int(device.count)

    def _set_device_count(self, device_id, count):
        device = Device.query.filter_by(device_id=device_id).first()

        if device is None:
            db.session.add(Device(device_id, count))
        else:
            device.count = count

        db.session.commit()
        return count
