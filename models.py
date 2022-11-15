from datetime import datetime
from sqlalchemy import inspect
from sqlalchemy.ext.associationproxy import association_proxy
#Alternative to resolving circular imports
from flask_sqlalchemy import SQLAlchemy

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Initialized without explicit app (Flask instance)
db = SQLAlchemy()

# Original Model I thought to use.
# shows = db.Table(
# 	'shows',
# 	db.Column('id', db.Integer, primary_key=True),
# 	db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), nullable=True),
# 	db.Column('venue_id', db.Integer, db.ForeignKey('venue_id'), nullable=True),
# 	db.Column('start_time', db.TIMESTAMP, nullable=True)
# )
# Switching to a different format. For this reason: https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#association-object


#https://stackoverflow.com/questions/42139767/sqlalchemy-exc-invalidrequesterror-mapper-has-no-property
#https://www.daniweb.com/programming/web-development/threads/505763/python-sqlalchemy-error
#https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html#association-object
#
#https://gist.github.com/SuryaSankar/10091097
#https://youtu.be/IlkVu_LWGys contradicts https://learn.co/lessons/sqlalchemy-association-object-lab in genres = relationship('Genre', secondary='songs', back_populates='artists')


class Show(db.Model):
	__tablename__ = "shows"

	id = db.Column(db.Integer, primary_key=True)
	artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
	venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
	start_time = db.Column(db.TIMESTAMP, nullable=False)

	venue = db.relationship("Venue", back_populates="shows")
	artist = db.relationship("Artist", back_populates="shows") #https://youtu.be/IlkVu_LWGys

#Child Table. See Artist Model below!
class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now())
    seeking_talent =db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship(
      "Show", 
      back_populates="venue", 
      cascade='all, delete',
      lazy='joined'
    )
    # artists=association_proxy('shows', 'artists')


    def __repr__(self):
       return f"<Venue(ID: {self.id}, name: {self.name}, location: {self.city +', '+ self.state}, genres: {self.genres}> \n"

    def _asdict(self):
      return {c.key: getattr(self, c.key)
        for c in inspect(self).mapper.column_attrs}
  
#Parents Table: Why? It seems to me that the venues will always need artists, whereas the artists are more independent.
#Is this view good enough to make such a choice? 
class Artist(db.Model):
    __tablename__ = 'artists'
 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    created_at = db.Column(db.TIMESTAMP, nullable=False, default=datetime.now())
    seeking_venues = db.Column(db.Boolean, nullable =False, default=True)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship(
      "Show", 
      back_populates="artist",
      cascade='all, delete', 
      lazy='joined'
    )
    # venues=association_proxy('shows', 'venues')
    
    #secondary attribute: https://hackersandslackers.com/sqlalchemy-data-models/#:~:text=this%20time%20we%20set%20the%20secondary%20attribute%20equal%20to%20the%20name%20of%20our%20association%20table
    
    def __repr__(self):
       return f"<Artist(ID: {self.id}, name: {self.name}, location: {self.city +', '+ self.state}, genres: {self.genres}> \n"

    def _asdict(self):
      return {c.key: getattr(self, c.key)
        for c in inspect(self).mapper.column_attrs}
