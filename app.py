#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from email.policy import default
import os
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from config import config
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
moment = Moment(app)
app.config.from_object(config.get('default'))
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
# DONE: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    genres = db.Column(db.String, default='')
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent =db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, city, state, phone, genres, image_link, facebook_link, seeking_talent, seeking_description, website_link, address):
      self.name = name
      self.city = city
      self.state = state
      self.phone = phone 
      self.genres = genres
      self.image_link = image_link
      self.facebook_link = facebook_link
      self.seeking_talent = seeking_talent
      self.seeking_description = seeking_description
      self.website_link = website_link
      self.address = address

    def serialize(self): 
      return {
        "id": self.id,
        "name": self.name,
        "city": self.city,
        "state": self.state,
        "address": self.address,
        "phone": self.phone,
        "image_link": self.image_link,
        "facebook_link": self.facebook_link,
        "seeking_talent": self.seeking_talent,
        "seeking_description": self.seeking_description,
        "website": self.website_link,
      }

    def get_venues(self):
      return {
        "id": self.id,
        "name": self.name,
        "num_upcoming_shows": len(get_upcoming_venue_shows(self.id))
      }


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, city, state, phone, genres, image_link, facebook_link, seeking_venue, seeking_description, website_link):
      self.name = name
      self.city = city
      self.state = state
      self.phone = phone 
      self.genres = genres
      self.image_link = image_link
      self.facebook_link = facebook_link
      self.seeking_venue = seeking_venue
      self.seeking_description = seeking_description
      self.website_link = website_link
 

    def serialize(self): 
      return {
        "id": self.id,
        "name": self.name,
        "city": self.city,
        "state": self.state,
        "phone": self.phone,
        "image_link": self.image_link,
        "facebook_link": self.facebook_link,
        "seeking_venue": self.seeking_venue,
        "seeking_description": self.seeking_description,
        "website": self.website_link
      }
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __table_name__ = 'Show'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, artist_id, venue_id, start_time):
      self.artist_id = artist_id
      self.venue_id = venue_id
      self.start_time = start_time

    def serialize(self): 
        return {
          "venue_id": get_venue_by_id(self.venue_id).id,
          "venue_name": get_venue_by_id(self.venue_id).name,
          "artist_id": get_artist_by_id(self.artist_id).id,
          "artist_name": get_artist_by_id(self.artist_id).name,
          "artist_image_link": get_artist_by_id(self.artist_id).image_link,
          "start_time": self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        }


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def get_artist_by_id(id):
  return Artist.query.get(id)

def get_venue_by_id(id):
  return Venue.query.get(id)

def get_venue_by_city_and_state(city, state):
  return Venue.query.filter_by(city=city, state=state).all()

def get_shows_by_venue_id(id):
  return Show.query.filter_by(venue_id=id).all()

def get_shows_by_artist_id(id):
  return Show.query.filter_by(artist_id=id).all()

def get_shows_by_venue_id_and_artist_id(venue_id, artist_id):
  return Show.query.filter_by(venue_id=venue_id, artist_id=artist_id).all()

def get_upcoming_venue_shows(venue_id):
  return Show.query.filter(Show.start_time > datetime.now()).filter_by(venue_id=venue_id).all()

def get_upcoming_artist_shows(artist_id):
  return Show.query.filter(Show.start_time > datetime.now()).filter_by(artist_id=artist_id).all()

def get_past_venue_shows(venue_id):
  return Show.query.filter(Show.start_time < datetime.now()).filter_by(venue_id=venue_id).all()

def get_past_artist_shows(artist_id):
  return Show.query.filter(Show.start_time < datetime.now()).filter_by(artist_id=artist_id).all()

def deconcatenate_genre(genres):
  return genres.split(',')

def concatenate_genre(genres):
  return ','.join(genres)

def get_venue_form_data(request):
  get_genres_from_form = request.form.getlist('genres')
  genres = ','.join(get_genres_from_form)
  seeking_talent = True if 'seeking_talent' in request.form else False
  venue = Venue(name=request.form['name'], city=request.form['city'], state= request.form['state'], phone= request.form['phone'], genres= genres,image_link=request.form['image_link'], facebook_link= request.form['facebook_link'], seeking_talent= seeking_talent, seeking_description= request.form['seeking_description'], website_link= request.form['website_link'], address=request.form['address'])
  return venue

def get_artist_form_data(request):
  get_genres_from_form = request.form.getlist('genres')
  genres = ','.join(get_genres_from_form)
  seeking_venue = True if 'seeking_venue' in request.form else False

  artist = Artist(name=request.form['name'], city=request.form['city'], state= request.form['state'], phone= request.form['phone'], genres= genres,image_link=request.form['image_link'], facebook_link= request.form['facebook_link'], seeking_venue= seeking_venue, seeking_description= request.form['seeking_description'], website_link= request.form['website_link'])
  return artist




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
  venue_data = []
  venue_per_city = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()

  for venue in venue_per_city:
    venue_data.append({
      "city": venue[0],
      "state": venue[1],
      "venues": [v.get_venues() for v in get_venue_by_city_and_state(venue[0], venue[1])]
    })
  
  return render_template('pages/venues.html', areas=venue_data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  response={
    "count": len(venues),
    "data": venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  single_venue = Venue.query.get(venue_id)
  if single_venue is None:
    return render_template('errors/404.html')
  upcoming_shows_per_venue = get_upcoming_venue_shows(venue_id)
  past_shows_per_venue = get_past_venue_shows(venue_id)
  print(single_venue.genres)
  genres = deconcatenate_genre(single_venue.genres) if single_venue.genres is not None else ''
  past_shows_count = len(past_shows_per_venue)
  upcoming_shows_count = len(upcoming_shows_per_venue)


  new_data = {
    **single_venue.serialize(),
    "past_shows": [ show.serialize() for show in past_shows_per_venue ],
    "upcoming_shows": [ show.serialize() for show in upcoming_shows_per_venue ],
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
    "genres": genres
  }

  return render_template('pages/show_venue.html', venue=new_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  try:
    venue = get_venue_form_data(request)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except: 
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    return render_template('forms/new_venue.html', form=form)
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue was successfully deleted!')
    return render_template('pages/home.html')
  except:
    db.session.rollback()
    flash('An error occurred. Venue could not be deleted.')
    return redirect(url_for('show_venue'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  new_data = Artist.query.all() 
  return render_template('pages/artists.html', artists=new_data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  data = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):


  # shows the artist page with the given artist_id

  artist = Artist.query.get(artist_id)
  if artist is None:
    return render_template('errors/404.html')
  past_shows = [ show.serialize() for show in get_past_artist_shows(artist_id) ]
  upcoming_shows = [ show.serialize() for show in get_upcoming_artist_shows(artist_id) ]

  past_shows_count = len(past_shows)
  upcoming_shows_count = len(upcoming_shows)
  print(artist)
  genres = deconcatenate_genre(artist.genres) if artist.genres is not None else ''

  new_data = {
    **artist.serialize(),
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
    "genres": genres
  }
  return render_template('pages/show_artist.html', artist=new_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  new_artist = Artist.query.get(artist_id)
  genres = deconcatenate_genre(new_artist.genres) if new_artist.genres is not None else []

  artist = {
    **new_artist.serialize(),
    "genres": genres, 
    "website_link": new_artist.website_link,
  }
  form = ArtistForm(data=artist)
 
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)
  try: 
    artist = Artist.query.get(artist_id)
    get_genres_from_form = request.form.getlist('genres')
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = concatenate_genre( get_genres_from_form)
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website_link = request.form['website_link']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
    artist.seeking_description = request.form['seeking_description']
    db.session.commit()
    flash(' Artist ' + request.form['name'] + ' is  updated.')
  except Exception as e:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
    return redirect(url_for('edit_artist', artist_id=artist_id))

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  new_venue = Venue.query.get(venue_id)
  genres = deconcatenate_genre(new_venue.genres) if new_venue.genres is not None else []

  venue={
   **new_venue.serialize(),
    "genres": genres, 
    "website_link": new_venue.website_link,
  }
  form = VenueForm(data=venue)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  try:
    get_genres_from_form = request.form.getlist('genres')
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.genres = concatenate_genre( get_genres_from_form)
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website_link = request.form['website_link']
    venue.seeking_talent = True if 'seeking_talent' in request.form else False
    venue.seeking_description = request.form['seeking_description']
    venue.address = request.form['address']
    db.session.commit()
    flash(' Venue ' + request.form['name'] + ' is  updated.')
  except Exception as e:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
    return redirect(url_for('edit_venue', venue_id=venue_id))

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)  
  try:
    artist = get_artist_form_data(request)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    return render_template('forms/new_artist.html', form=form)
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data = [ show.serialize() for show in shows ]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  try: 
    show = Show(artist_id=request.form['artist_id'], venue_id=request.form['venue_id'], start_time=request.form['start_time'])
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except: 
    flash('An error occurred. Show could not be listed.')
    return render_template('forms/new_show.html', form=form)
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
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
