#----------------------------------------------------------------------------#
# Learned leasons
#----------------------------------------------------------------------------#

# example: To fetch names & age where age is greater than 20
# rows = Model.query.with_entities(Model.name, Model.age).filter(Model.age >= 20).all()
# return   List of tuples

# association table valid only if we use the foreign keys only if we need to add any other date 
# we should use association model (association object patters)
# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-many

# https://werkzeug.palletsprojects.com/en/2.2.x/datastructures/#werkzeug.datastructures.MultiDict

# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#association-object

# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

# https://stackoverflow.com/questions/41270319/how-do-i-query-an-association-table-in-sqlalchemy

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


import sys
import os
import json
import dateutil.parser
import babel
import logging
from logging import Formatter, FileHandler

from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_wtf import Form
from flask_moment import Moment
from flask_migrate import Migrate
from psycopg2 import Date

from models import *
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

# doesn't work with the currnt version of python 
# return an error so it's comminted in the html part
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  data = []
  distinct_cities = Venue.query.distinct('city').order_by(desc('city')).all()
  for city in distinct_cities:
    city_record = {}
    city_record['city'] = city.city
    city_record['state'] = city.state
    venues = Venue.query.filter_by(city=city_record['city'], state=city_record['state']).all()
    city_record['venues'] = []
    for v in venues:
      venue = {}
      venue['id'] = v.id
      venue['name'] = v.name
      num_upcoming_shows = Show.query.filter(func.date(Show.start_time) > datetime.now(),
                            Show.venue_id == venue.get('id')).count()
      venue['num_upcoming_shows'] = num_upcoming_shows
      city_record['venues'].append(venue)
    data.append(city_record)
  return render_template('pages/venues.html', areas=data)



@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  search = f"%{search_term}%"
  venues = Venue.query.filter(or_(
    Venue.name.ilike(db.literal(search)),
    Venue.city.ilike(db.literal(search)),
    Venue.state.ilike(db.literal(search)))).all()
  response={
    "count": len(venues),
    # "data": [{
    #   "id": 2,
    #   "name": "The Dueling Pianos Bar",
    #   "num_upcoming_shows": 0,
    # }]
    "data" : []
  }
  for venue in venues:
    res = {}
    res['id'] = venue.id
    res['name'] = venue.name
    res['num_upcomig_shows'] = Show.query.filter(func.date(Show.start_time) > datetime.now(),
                            Show.venue_id ==venue.id).count()
    response['data'].append(res)
  return render_template('pages/search_venues.html', results=response, search_term=search_term)




@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id


  query = Venue.query.get(venue_id)
  if query == None:
    return render_template('errors/404.html')
  data = object_as_dict(query)
  data['genres'] = data['genres'].split(',')

# past shows data

  data['past_shows'] = []
  past_shows_query = Show.query.filter(func.date(Show.start_time) < datetime.now(),
                            Show.venue_id == data.get('id')).all() 
  for show in past_shows_query:
    past = {}                           
    artist = Artist.query.get(show.artist_id) 
    past['artist_id'] = artist.id
    past['artist_name'] = artist.name
    past['artist_image_link'] = artist.image_link
    past['start_time'] = str(show.start_time)
    data['past_shows'].append(past)

  data['past_shows_count'] = len(data['past_shows'])

# upcoming shows data

  data['upcoming_shows'] = []
  upcoming_shows_query = Show.query.filter(func.date(Show.start_time) > datetime.now(),
                            Show.venue_id == data.get('id')).all() 
  for show in upcoming_shows_query:
    upcoming = {}                           
    artist = Artist.query.get(show.artist_id) 
    upcoming['artist_id'] = artist.id
    upcoming['artist_name'] = artist.name
    upcoming['artist_image_link'] = artist.image_link
    upcoming['start_time'] =str(show.start_time)
    data['upcoming_shows'].append(upcoming)

  data['upcoming_shows_count'] = len(data['upcoming_shows'])
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)




#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    # https://werkzeug.palletsprojects.com/en/2.2.x/datastructures/#werkzeug.datastructures.MultiDict
    # print('----------------------------------------------------------------------------------------')
    # print(request.form)  #request.form === MultiDict
    # print('----------------------------------------------------------------------------------------')

    talent = True  if request.form.get('seeking_talent') =='y' else  False
    list_of_genres =request.form.getlist('genres')
    genres = ','.join(list_of_genres)
    venue = Venue(name = request.form["name"],
                  city = request.form["city"],
                  state = request.form["state"],
                  address = request.form["address"],
                  phone = request.form["phone"],
                  image_link= request.form["image_link"],
                  facebook_link = request.form["facebook_link"],
                  website_link = request.form["website_link"],
                  seeking_talent = talent,
                  seeking_description = request.form["seeking_description"],
                  genres = genres,
                  )              
    db.session.add(venue)                
    db.session.commit()         
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    v = Venue.query.get(venue_id)
    name = v.name

    # ERROR -> (<class 'AssertionError'>, AssertionError("Dependency rule tried to blank-out primary key column 'show.venue_id' on instance ))
    # db.session.delete(v)  

    db.session.execute(f'delete from venue where id = {venue_id}')
    db.session.commit()
    flash('Venue ' + name + ' was successfully deleted!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue could not be deleted.')
  finally:
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for("index"))



@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    name = Artist.query.get(artist_id).name
    # db.session.delete(a)
    db.session.execute(f'delete from artist where id = {artist_id}')
    db.session.commit()
    flash('Artist ' + name + ' was successfully deleted!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist could not be deleted.')
  finally:
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for("index"))



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.with_entities(Artist.id,Artist.name).all()
  # print('-------------------------------------------------------------------------------------')
  # print(artists)
  # print('-------------------------------------------------------------------------------------')
  data = []
  for artist in artists:
    name_id = {}
    name_id['id'] = artist.id
    name_id['name'] = artist.name
    data.append(name_id)
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

  

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  search = f"%{search_term}%"
  artists = Artist.query.filter(or_(
    Artist.name.ilike(db.literal(search)),
    Artist.city.ilike(db.literal(search)),
    Artist.state.ilike(db.literal(search)),)).all()
  response={
    "count": len(artists),
    "data" : []
  }
  for artist in artists:
    res = {}
    res['id'] = artist.id
    res['name'] = artist.name
    res['num_upcomig_shows'] = Show.query.filter(func.date(Show.start_time) > datetime.now(),
                            Show.artist_id ==artist.id).count()
    response['data'].append(res)
  return render_template('pages/search_artists.html', results=response, search_term=search_term)



@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id


  query = Artist.query.get(artist_id)
  if query == None:
    return render_template('errors/404.html')
  data = object_as_dict(query)
  data['genres'] = data['genres'].split(',')

# past shows data

  data['past_shows'] = []
  past_shows_query = Show.query.filter(func.date(Show.start_time) < datetime.now(),
                                            Show.artist_id == data.get('id')).all() 
  for show in past_shows_query:
    past = {}                           
    venue = Venue.query.get(show.venue_id)
    past['venue_id'] = venue.id
    past['venue_name'] = venue.name
    past['venue_image_link'] = venue.image_link
    past['start_time'] = str(show.start_time)
    data['past_shows'].append(past)

  data['past_shows_count'] = len(data['past_shows'])

# upcoming shows data

  data['upcoming_shows'] = []
  upcoming_shows_query = Show.query.filter(func.date(Show.start_time) > datetime.now(),
                            Show.artist_id == data.get('id')).all() 
  for show in upcoming_shows_query:
    upcoming = {}                           
    venue = Venue.query.get(show.venue_id) 
    upcoming['venue_id'] = venue.id
    upcoming['venue_name'] = venue.name
    upcoming['venue_image_link'] = venue.image_link
    upcoming['start_time'] =str(show.start_time)
    data['upcoming_shows'].append(upcoming)

  data['upcoming_shows_count'] = len(data['upcoming_shows'])





  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>

  # couldn't populate state field (select) and genres field (multi-select)
  # this might be possible by using js but, i haven't tried yet
  
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  # Eleminate invalid artist ids 
  if artist == None:
    return render_template('errors/404.html')

  artist =object_as_dict(artist)
  artist['genres'] = artist['genres'].split(',')
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  return render_template('forms/edit_artist.html', form=form, artist=artist)



@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  try:
    list_of_genres =request.form.getlist('genres')
    venue = True  if request.form.get('seeking_venues') =='y' else  False
    genres = ','.join(list_of_genres)
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get("name")
    artist.city = request.form.get("city")
    artist.state = request.form.get("state")
    artist.phone = request.form.get("phone")
    artist.image_link= request.form.get("image_link")
    artist.facebook_link = request.form.get("facebook_link")
    artist.website_link = request.form.get("website_link")
    artist.seeking_venues = venue
    artist.seeking_description = request.form.get("seeking_description")
    artist.genres = genres                      
    db.session.add(artist)                
    db.session.commit()       
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
  finally:
    return redirect(url_for('show_artist', artist_id=artist_id))



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  if venue == None:
      return render_template('errors/404.html')
  # venue =object_as_dict(venue)
  # venue['genres'] = venue['genres'].split(',')
  venue_data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)



@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue = Venue.query.get(venue_id)
    list_of_genres =request.form.getlist('genres')
    talent = True  if request.form.get('seeking_talent') =='y' else  False
    genres = ','.join(list_of_genres)
    venue.name = request.form.get("name")
    venue.city = request.form.get("city")
    venue.state = request.form.get("state")
    venue.address = request.form.get("address")
    venue.phone = request.form.get("phone")
    venue.image_link= request.form.get("image_link")
    venue.facebook_link = request.form.get("facebook_link")
    venue.website_link = request.form.get("website_link")
    venue.seeking_talent = talent
    venue.seeking_description = request.form.get("seeking_description")
    venue.genres = genres                      
    db.session.add(venue)                
    db.session.commit()       
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  finally:
    return redirect(url_for('show_venue', venue_id=venue_id))



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)



@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  try:
    # https://werkzeug.palletsprojects.com/en/2.2.x/datastructures/#werkzeug.datastructures.MultiDict
    print(request.form)  #request.form === MultiDict

    list_of_genres =request.form.getlist('genres')
    venue = True  if request.form.get('seeking_venues') =='y' else  False
    genres = ','.join(list_of_genres)
    artist = Artist(name = request.form.get("name"),
                  city = request.form.get("city"),
                  state = request.form.get("state"),
                  phone = request.form.get("phone"),
                  image_link= request.form.get("image_link"),
                  facebook_link = request.form.get("facebook_link"),
                  website_link = request.form.get("website_link"),
                  seeking_venues = venue,
                  seeking_description = request.form.get("seeking_description"),
                  genres = genres,
                  )                             
    db.session.add(artist)                
    db.session.commit()       
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    print(sys.exc_info())
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  records = db.session.query(Show,Artist,Venue).filter(
        (Artist.id == Show.artist_id ) & (Venue.id == Show.venue_id)).with_entities(
          Show.venue_id , Venue.name , Show.artist_id, Artist.name, Artist.image_link, Show.start_time
        ).all()
  data = []
  for record in records:
    show = {}
    show["venue_id"] = record[0]
    show['venue_name'] = record[1]
    show['artist_id'] = record[2]
    show['artist_name'] = record[3]
    show['artist_image_link'] = record[4]
    show['start_time'] = record[5]
    data.append(show)
  print(data)

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)



@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)




@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    show = Show(start_time=request.form.get('start_time'))
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    artist = Artist.query.get(artist_id)
    venue = Venue.query.get(venue_id)
    show.artist= artist
    show.venue = venue
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 2000))
    app.run(host='0.0.0.0', port=port)

