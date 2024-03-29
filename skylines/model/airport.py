# -*- coding: utf-8 -*-

from datetime import datetime
from sqlalchemy import Column, func
from sqlalchemy.types import Integer, Float, String, DateTime
from sqlalchemy.sql.expression import cast
from geoalchemy2.types import Geometry, Geography
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from skylines.model.base import DeclarativeBase
from skylines.model.session import DBSession
from skylines.model.geo import Location


class Airport(DeclarativeBase):
    __tablename__ = 'airports'

    id = Column(Integer, autoincrement=True, primary_key=True)
    time_created = Column(DateTime, nullable=False, default=datetime.utcnow)
    time_modified = Column(DateTime, nullable=False, default=datetime.utcnow)

    location_wkt = Column(Geometry('POINT', management=True))
    altitude = Column(Float)

    name = Column(String(), nullable=False)
    short_name = Column(String())
    icao = Column(String(4))
    country_code = Column(String(2), nullable=False)

    surface = Column(String(10))
    runway_len = Column(Integer)
    runway_dir = Column(Integer)
    frequency = Column(Float)
    type = Column(String(20))

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return ('<Airport: id=%d name=\'%s\'>' % (self.id, self.name)).encode('utf-8')

    @property
    def location(self):
        if self.location_wkt is None:
            return None

        coords = to_shape(self.location_wkt)
        return Location(latitude=coords.y, longitude=coords.x)

    @location.setter
    def location(self, location):
        if location is None:
            self.location_wkt = None
        else:
            self.location_wkt = WKTElement(location.to_wkt(), srid=4326)

    @classmethod
    def by_location(cls, location, distance_threshold=0.025):
        location = WKTElement(location.to_wkt(), srid=4326)
        distance = func.ST_Distance(cls.location_wkt, location)

        airport = DBSession.query(cls, distance.label('distance')) \
            .order_by(distance).first()

        if airport is not None and (distance_threshold is None or
                                    airport.distance < distance_threshold):
            return airport.Airport
        else:
            return None

    def distance(self, location):
        loc1 = cast(self.location_wkt, Geography)
        loc2 = func.ST_GeographyFromText(location.to_wkt())
        return DBSession.scalar(func.ST_Distance(loc1, loc2))
