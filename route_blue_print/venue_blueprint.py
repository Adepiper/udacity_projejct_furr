from flask import Blueprint, flash, redirect, render_template, request, url_for
from forms import VenueForm
from models import (
    Venue,
    concatenate_genre,
    deconcatenate_genre,
    get_past_venue_shows,
    get_upcoming_venue_shows,
    get_venue_by_city_and_state,
    get_venue_form_data,
    db,
)

venue_bp = Blueprint(
    "venue_bp",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/",
)


@venue_bp.route("")
def venues():

    venue_data = []
    venue_per_city = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()

    for venue in venue_per_city:
        venue_data.append(
            {
                "city": venue[0],
                "state": venue[1],
                "venues": [
                    v.get_venues()
                    for v in get_venue_by_city_and_state(venue[0], venue[1])
                ],
            }
        )

    return render_template("pages/venues.html", areas=venue_data)


@venue_bp.route("/search", methods=["POST"])
def search_venues():
    search_term = request.form.get("search_term", "")
    venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()

    response = {"count": len(venues), "data": venues}
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@venue_bp.route("/<int:venue_id>")
def show_venue(venue_id):
    single_venue = Venue.query.get(venue_id)
    if single_venue is None:
        return render_template("errors/404.html")
    upcoming_shows_per_venue = get_upcoming_venue_shows(venue_id)
    past_shows_per_venue = get_past_venue_shows(venue_id)
    print(single_venue.genres)
    genres = (
        deconcatenate_genre(single_venue.genres)
        if single_venue.genres is not None
        else ""
    )
    past_shows_count = len(past_shows_per_venue)
    upcoming_shows_count = len(upcoming_shows_per_venue)

    new_data = {
        **single_venue.serialize(),
        "past_shows": [show.serialize() for show in past_shows_per_venue],
        "upcoming_shows": [show.serialize() for show in upcoming_shows_per_venue],
        "past_shows_count": past_shows_count,
        "upcoming_shows_count": upcoming_shows_count,
        "genres": genres,
    }

    return render_template("pages/show_venue.html", venue=new_data)


#  Create Venue
#  ----------------------------------------------------------------


@venue_bp.route("/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@venue_bp.route("/create", methods=["POST"])
def create_venue_submission():
    form = VenueForm(request.form)
    try:
        venue = get_venue_form_data(request)
        db.session.add(venue)
        db.session.commit()
        flash("Venue " + request.form["name"] + " was successfully listed!")
    except:
        flash(
            "An error occurred. Venue " + request.form["name"] + " could not be listed."
        )
        return render_template("forms/new_venue.html", form=form)
    return render_template("pages/home.html")


@venue_bp.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):

    new_venue = Venue.query.get(venue_id)
    genres = (
        deconcatenate_genre(new_venue.genres) if new_venue.genres is not None else []
    )

    venue = {
        **new_venue.serialize(),
        "genres": genres,
        "website_link": new_venue.website_link,
    }
    form = VenueForm(data=venue)
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@venue_bp.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    try:
        get_genres_from_form = request.form.getlist("genres")
        venue.name = request.form["name"]
        venue.city = request.form["city"]
        venue.state = request.form["state"]
        venue.phone = request.form["phone"]
        venue.genres = concatenate_genre(get_genres_from_form)
        venue.image_link = request.form["image_link"]
        venue.facebook_link = request.form["facebook_link"]
        venue.website_link = request.form["website_link"]
        venue.seeking_talent = True if "seeking_talent" in request.form else False
        venue.seeking_description = request.form["seeking_description"]
        venue.address = request.form["address"]
        db.session.commit()
        flash(" Venue " + request.form["name"] + " is  updated.")
    except Exception as e:
        db.session.rollback()
        flash(
            "An error occurred. Venue "
            + request.form["name"]
            + " could not be updated."
        )
        return redirect(url_for("shows_bp.edit_venue", venue_id=venue_id))

    return redirect(url_for("shows_bp.show_venue", venue_id=venue_id))


@venue_bp.route("/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash("Venue was successfully deleted!")
        return render_template("pages/home.html")
    except:
        db.session.rollback()
        flash("An error occurred. Venue could not be deleted.")
        return redirect(url_for("shows_bp.show_venue"))
