#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct, func, desc, inspect


db = SQLAlchemy()



#-----------------------------------------------------------------------------------------#
#    https://riptutorial.com/sqlalchemy/example/6614/converting-a-query-result-to-dict

def object_as_dict(obj):                                    # map queries into object(dict)
  return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
#-----------------------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'
    # child class
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(120))

    def __repr__(self):
      return f'<Vid:{self.id}, Vname:{ self.name}, city:{self.city}, state:{self.state}, address:{self.address} >'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# -----------------------------------Association Table-------------------------------------
# show = db.Table('show',
#         db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
#         db.Column('venue_id' , db.Integer, db.ForeignKey('venue.id') , primary_key=True),
#         db.Column('start_time',db.DateTime, nullable=False))


# -----------------------------------Association Object Pattern-----------------------------
# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#association-object

class Show(db.Model):
    __tablename__ = 'show'
    artist_id = db.Column( db.Integer, db.ForeignKey('artist.id',ondelete="CASCADE"), primary_key=True)
    venue_id = db.Column( db.Integer, db.ForeignKey('venue.id',ondelete="CASCADE") , primary_key=True)
    start_time = db.Column( db.DateTime, nullable=False, default=datetime.now(), primary_key=True)

    venue = db.relationship("Venue", backref="artist_assoc")
    artist = db.relationship("Artist", backref="venue_assoc")

    def __repr__(self):
      return f'<Artist id: {self.artist_id}, Venue id: {self.venue_id}, Start time: {self.start_time}>'


class Artist(db.Model):
    __tablename__ = 'artist'
    # parent class
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(120))
    venues = db.relationship('Venue', secondary="show",cascade="all, delete",
            backref=db.backref('artists', lazy=True))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate