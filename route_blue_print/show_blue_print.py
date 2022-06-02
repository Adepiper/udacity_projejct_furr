from flask import Blueprint, flash, render_template, request
from forms import ShowForm

from models import Show, db


shows_bp = Blueprint(
    "shows_bp",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/",
)


@shows_bp.route("")
def shows():
    shows = Show.query.all()
    data = [show.serialize() for show in shows]
    return render_template("pages/shows.html", shows=data)


@shows_bp.route("/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@shows_bp.route("/create", methods=["POST"])
def create_show_submission():
    form = ShowForm(request.form)
    try:
        show = Show(
            artist_id=request.form["artist_id"],
            venue_id=request.form["venue_id"],
            start_time=request.form["start_time"],
        )
        db.session.add(show)
        db.session.commit()
        flash("Show was successfully listed!")
    except:
        flash("An error occurred. Show could not be listed.")
        return render_template("forms/new_show.html", form=form)
    return render_template("pages/home.html")
