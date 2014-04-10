from datetime import datetime

from sqlalchemy import Column, Numeric, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from flask.ext.sqlalchemy import SQLAlchemy

from home.util import get_or_create

db = SQLAlchemy()


class SerialiseMixin:

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class DataPoint(db.Model, SerialiseMixin):
    __tablename__ = 'data_point'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    value = Column(Numeric, nullable=False)

    device_series_id = Column(
        Integer, ForeignKey('device_series.id'), nullable=False)
    device_series = relationship(
        "Series", backref=backref('data_points', order_by=id))

    def __init__(self, series, device, value, created_at=None):
        self.created_at = datetime.utcnow()
        super().__init__()
        self.series = series
        self.device = device
        self.value = value
        self.created_at = created_at

    @classmethod
    def record(cls, series, device, value, created_at=None):
        data_point = DataPoint(series=series, device=device, value=value)
        if created_at is None:
            data_point.created_at = datetime.utcnow()
        db.session.add(data_point)
        return data_point

    def __repr__(self):
        return "<Data Point(%s, %s, value=%s, created_at=%s)>" % (
            self.series, self.device, self.value, self.created_at)


class DeviceSeries(db.Model, SerialiseMixin):
    __tablename__ = 'device_series'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    series_id = Column(Integer, ForeignKey('series.id'), nullable=False)
    device_id = Column(Integer, ForeignKey('device.id'), nullable=False)

    __table_args__ = (
        UniqueConstraint('series_id', 'device_id', name='_series_device_uc'),
    )

    def __init__(self, series_id, device_id):
        super().__init__()
        self.created_at = datetime.utcnow()
        self.name = name

    @classmethod
    def get_or_create(cls, **kwargs):
        r = get_or_create(cls, **kwargs)
        return r

    def __repr__(self):
        return "DeviceSeries(device_id=%s, series_id=%s)" % (
            self.device_id, self.series_id)



class Series(db.Model, SerialiseMixin):
    __tablename__ = 'series'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    name = Column(String(20), nullable=False, unique=True)

    def __init__(self, name):
        super().__init__()
        self.created_at = datetime.utcnow()
        self.name = name

    @classmethod
    def get_or_create(cls, **kwargs):
        r = get_or_create(cls, **kwargs)
        return r

    def __repr__(self):
        return "Series(name=%r)" % (self.name)

class Device(db.Model, SerialiseMixin):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False)
    name = Column(String(20), nullable=True, unique=True)
    device_type = Column(Integer)
    device_sub_type = Column(Integer)
    device_id = Column(String(20), nullable=False, unique=True)

    series = relationship("Series",
        secondary="join(DataPoint, Series, DataPoint.series_id == Series.id)",
        primaryjoin=("and_(Device.id == DataPoint.device_id, Series.id == "
                     "DataPoint.series_id)"),
        secondaryjoin="Series.id == DataPoint.series_id"
    )

    def __init__(self, device_type, device_sub_type, device_id, name=None):
        super().__init__()
        self.created_at = datetime.utcnow()
        self.device_type = device_type
        self.device_sub_type = device_sub_type
        self.device_id = device_id
        self.name = name

    @classmethod
    def get_or_create(cls, device_type, device_sub_type, device_id):
        return get_or_create(cls, device_type=device_type,
                             device_sub_type=device_sub_type,
                             device_id=device_id)

    def __repr__(self):
        return "Device(name=%s, ID=%r)" % (
            self.name, self.device_id)
