from flask import Blueprint, flash, redirect, render_template, request, url_for
from forms import ArtistForm

from models import (
    Artist,
    concatenate_genre,
    deconcatenate_genre,
    get_artist_form_data,
    get_past_artist_shows,
    get_upcoming_artist_shows,
    db,
)


artist_bp = Blueprint(
    "artist_bp",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/",
)


@artist_bp.route("")
def artists():

    new_data = Artist.query.all()
    return render_template("pages/artists.html", artists=new_data)


@artist_bp.route("/search", methods=["POST"])
def search_artists():

    search_term = request.form.get("search_term", "")
    data = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
    response = {"count": len(data), "data": data}
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@artist_bp.route("/<int:artist_id>")
def show_artist(artist_id):

    artist = Artist.query.get(artist_id)
    if artist is None:
        return render_template("errors/404.html")
    past_shows = [show.serialize() for show in get_past_artist_shows(artist_id)]
    upcoming_shows = [show.serialize() for show in get_upcoming_artist_shows(artist_id)]

    past_shows_count = len(past_shows)
    upcoming_shows_count = len(upcoming_shows)

    genres = deconcatenate_genre(artist.genres) if artist.genres is not None else ""

    new_data = {
        **artist.serialize(),
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
        "genres": genres,
    }
    return render_template("pages/show_artist.html", artist=new_data)


#  Update
#  ----------------------------------------------------------------
@artist_bp.route("/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):

    new_artist = Artist.query.get(artist_id)
    genres = (
        deconcatenate_genre(new_artist.genres) if new_artist.genres is not None else []
    )

    artist = {
        **new_artist.serialize(),
        "genres": genres,
        "website_link": new_artist.website_link,
    }
    form = ArtistForm(data=artist)

    return render_template("forms/edit_artist.html", form=form, artist=artist)


@artist_bp.route("/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    try:
        artist = Artist.query.get(artist_id)
        get_genres_from_form = request.form.getlist("genres")
        artist.name = request.form["name"]
        artist.city = request.form["city"]
        artist.state = request.form["state"]
        artist.phone = request.form["phone"]
        artist.genres = concatenate_genre(get_genres_from_form)
        artist.image_link = request.form["image_link"]
        artist.facebook_link = request.form["facebook_link"]
        artist.website_link = request.form["website_link"]
        artist.seeking_venue = True if "seeking_venue" in request.form else False
        artist.seeking_description = request.form["seeking_description"]
        db.session.commit()
        flash(" Artist " + request.form["name"] + " is  updated.")
    except Exception as e:
        db.session.rollback()
        flash(
            "An error occurred. Artist "
            + request.form["name"]
            + " could not be updated."
        )
        return redirect(url_for("artist_bp.edit_artist", artist_id=artist_id))

    return redirect(url_for("artist_bp.show_artist", artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------


@artist_bp.route("/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@artist_bp.route("/create", methods=["POST"])
def create_artist_submission():
    form = ArtistForm(request.form)
    try:
        artist = get_artist_form_data(request)
        db.session.add(artist)
        db.session.commit()
        flash("Artist " + request.form["name"] + " was successfully listed!")
    except:
        flash(
            "An error occurred. Artist "
            + request.form["name"]
            + " could not be listed."
        )
        return render_template("forms/new_artist.html", form=form)
    return render_template("pages/home.html")
