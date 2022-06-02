# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#
from email.policy import default
import imp
import dateutil.parser
import babel
from flask import render_template, request, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from forms import *
from models import *
from route_blue_print.venue_blueprint import venue_bp
from route_blue_print.artists_blueprint import artist_bp
from route_blue_print.show_blue_print import shows_bp

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#


app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
moment = Moment(app)
app.register_blueprint(venue_bp, url_prefix="/venues")
app.register_blueprint(artist_bp, url_prefix="/artists")
app.register_blueprint(shows_bp, url_prefix="/shows")


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
