from datetime import datetime
from app import db
from sqlalchemy import inspect
from sqlalchemy_utils import ScalarListType, force_auto_coercion

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

force_auto_coercion()

# Original Model
# shows = db.Table(
# 	'shows',
# 	db.Column('id', db.Integer, primary_key=True),
# 	db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), nullable=True),
# 	db.Column('venue_id', db.Integer, db.ForeignKey('venue_id'), nullable=True),
# 	db.Column('start_time', db.TIMESTAMP, nullable=True)
# )
# Switching to a different format. For this reason: https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#association-object

class Show(db.Model):
	__tablename__ = "shows"

	id = db.Column(db.Integer, primary_key=True)
	artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
	venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
	start_time = db.Column(db.TIMESTAMP, nullable=False)
	venues = db.relationship("Venue", back_populates="artists")
	artists = db.relationship("Artist", back_populates="venues")


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(
      db.ARRAY(db.String).with_variant(ScalarListType(), 'postgresql'), nullable=False
    )
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now())
    seeking_talent =db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    artists = db.relationship(
      "Show", 
      back_populates="venues", 
      cascade='all, delete-orphan',
      lazy=False
    )

    def __repr__(self):
       return f"<Venue(name: {self.name}, location: {self.city +' , '+ self.state}, genres: {self.genres}> \n"

    def _asdict(self):
      return {c.key: getattr(self, c.key)
        for c in inspect(self).mapper.column_attrs}
  
class Artist(db.Model):
    __tablename__ = 'artists'
 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(
      db.ARRAY(db.String).with_variant(ScalarListType(), 'postgresql'), nullable=False
    )
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now())
    seeking_venues = db.Column(db.Boolean, nullable =False, default=True)
    seeking_description = db.Column(db.String(500))
    venues = db.relationship(
      "Show", 
      back_populates="artists", 
      cascade='all, delete-orphan', 
      lazy=False
    )

    def __repr__(self):
       return f"<Artist(name: {self.name}, location: {self.city +' , '+ self.state}, genres: {self.genres}> \n"

    def _asdict(self):
      return {c.key: getattr(self, c.key)
        for c in inspect(self).mapper.column_attrs}
