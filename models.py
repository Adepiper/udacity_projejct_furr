from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config

app = Flask(__name__)
app.config.from_object(config.get("default"))
db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    genres = db.Column(db.String, default="")
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(
        self,
        name,
        city,
        state,
        phone,
        genres,
        image_link,
        facebook_link,
        seeking_talent,
        seeking_description,
        website_link,
        address,
    ):
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
            "num_upcoming_shows": len(get_upcoming_venue_shows(self.id)),
        }


class Artist(db.Model):
    __tablename__ = "Artist"

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

    def __init__(
        self,
        name,
        city,
        state,
        phone,
        genres,
        image_link,
        facebook_link,
        seeking_venue,
        seeking_description,
        website_link,
    ):
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
            "website": self.website_link,
        }


class Show(db.Model):
    __table_name__ = "Show"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
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
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        }


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


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
    return (
        Show.query.filter(Show.start_time > datetime.now())
        .filter_by(venue_id=venue_id)
        .all()
    )


def get_upcoming_artist_shows(artist_id):
    return (
        Show.query.filter(Show.start_time > datetime.now())
        .filter_by(artist_id=artist_id)
        .all()
    )


def get_past_venue_shows(venue_id):
    return (
        Show.query.filter(Show.start_time < datetime.now())
        .filter_by(venue_id=venue_id)
        .all()
    )


def get_past_artist_shows(artist_id):
    return (
        Show.query.filter(Show.start_time < datetime.now())
        .filter_by(artist_id=artist_id)
        .all()
    )


def deconcatenate_genre(genres):
    return genres.split(",")


def concatenate_genre(genres):
    return ",".join(genres)


def get_venue_form_data(request):
    get_genres_from_form = request.form.getlist("genres")
    genres = ",".join(get_genres_from_form)
    seeking_talent = True if "seeking_talent" in request.form else False
    venue = Venue(
        name=request.form["name"],
        city=request.form["city"],
        state=request.form["state"],
        phone=request.form["phone"],
        genres=genres,
        image_link=request.form["image_link"],
        facebook_link=request.form["facebook_link"],
        seeking_talent=seeking_talent,
        seeking_description=request.form["seeking_description"],
        website_link=request.form["website_link"],
        address=request.form["address"],
    )
    return venue


def get_artist_form_data(request):
    get_genres_from_form = request.form.getlist("genres")
    genres = ",".join(get_genres_from_form)
    seeking_venue = True if "seeking_venue" in request.form else False

    artist = Artist(
        name=request.form["name"],
        city=request.form["city"],
        state=request.form["state"],
        phone=request.form["phone"],
        genres=genres,
        image_link=request.form["image_link"],
        facebook_link=request.form["facebook_link"],
        seeking_venue=seeking_venue,
        seeking_description=request.form["seeking_description"],
        website_link=request.form["website_link"],
    )
    return artist
