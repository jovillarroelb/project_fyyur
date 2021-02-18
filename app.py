##### Imports #####
from datetime import date, datetime
import json
import dateutil.parser
import babel

from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for)

from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import Form

import logging
from logging import Formatter, FileHandler

# Import other *.py files of the project
from forms import *
from models import db, Venue, Artist, Show

##### APP CONFIG #####
app = Flask(__name__)
app.config.from_object('config')
moment = Moment(app)
db.init_app(app)

# Activate Migration
migrate = Migrate(app, db)

##### FILTERS #####
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

##### CONTROLLERS #####
@app.route('/')
def index():
  return render_template('pages/home.html')

##### Artists #####
# 1.- Create Artist
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form, csrf_enabled=False)
    if form.validate():
        try:
            # Using FlaskForm:
            artist = Artist(
                name = form.name.data,
                city = form.city.data,
                seeking_venue = form.seeking_venue.data,
                state = form.state.data,
                phone = form.phone.data,
                website = form.website.data,
                seeking_description = form.seeking_description.data,
                image_link = form.image_link.data,
                genres = form.genres.data,
                facebook_link = form.facebook_link.data,
            )
            # Or:
            # artist = Artist()
            # form.populate_obj(artist)

            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + form.name.data + ' was successfully listed!')
        except ValueError as e:
            print(e)
            flash('An error occurred. Artist ' + form.name.data + 
                ' could not be listed.')
            db.session.rollback()
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))
    
    return render_template('pages/home.html')

# 2.- Get Artist
@app.route('/artists')
def artists():
    return render_template('pages/artists.html',
                           artists=Artist.query.all())

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

    artist = Artist.query.filter_by(id=artist_id).first_or_404()

    past_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
        Show.venue_id == Venue.id,
        Show.artist_id == artist_id,
        Show.start_time < datetime.now()
    ).\
    all()

    upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
    filter(
        Show.venue_id == Venue.id,
        Show.artist_id == artist_id,
        Show.start_time > datetime.now()
    ).\
    all()

    data = {
        'id': artist.id,
        'name': artist.name,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website,
        'image_link': artist.image_link,
        'genres': artist.genres,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'past_shows': [{
            'venue_id': venue.id,
            'venue_name': venue.name,
            'venue_image_link': venue.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for venue, show in past_shows],
        'upcoming_shows': [{
            'venue_id': venue.id,
            'venue_name': venue.name,
            'venue_image_link': venue.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for venue, show in upcoming_shows],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

    return render_template('pages/show_artist.html', artist=data)

# 3.- Update Artist
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # OR:
    # form = ArtistForm()
    # artist = Artist.query.get(artist_id)
    # return render_template('forms/edit_artist.html', form=form, artist=artist)

    artist = Artist.query.first_or_404(artist_id)
    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    error = False
    form = ArtistForm(request.form, csrf_enabled=False)
    if form.validate():
        try:
            # Using FlaskForm:
            artist.name = form.name.data
            artist.city = form.city.data
            artist.seeking_venue = form.seeking_venue.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.website = form.website.data
            artist.seeking_description = form.seeking_description.data
            artist.image_link = form.image_link.data
            artist.genres = form.genres.data
            artist.facebook_link = form.facebook_link.data

            db.session.add(artist)
            db.session.commit()
            flash('Artist ' + artist.name + ' was successfully updated!')
        except ValueError as e:
            print(e)
            flash('An error occurred. Artist ' + artist.name + 
                ' could not be updated.')
            db.session.rollback()
        finally:
            db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/artists/search', methods=['POST'])

def search_artists():
    search_term = request.form.get('search_term')
    search_results = Artist.query.filter(
        Artist.name.ilike('%{}%'.format(search_term))).all()  # search results by ilike matching partern to match every search term

    response = {}
    response['count'] = len(search_results)
    response['data'] = search_results

    return render_template('pages/search_artists.html',
                           results=response,
                           search_term=request.form.get('search_term', ''))

##### VENUES #####
#  1.- Create Venue:
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form, csrf_enabled=False)
    if form.validate():
        try:
            # Using FlaskForm:
            venue = Venue(
                name = form.name.data,
                city = form.city.data,
                state = form.state.data,
                address = form.address.data,
                phone = form.phone.data,
                image_link = form.image_link.data,
                website = form.website.data,
                seeking_talent = form.seeking_talent.data,
                seeking_description = form.seeking_description.data,
                genres = form.genres.data,
                facebook_link = form.facebook_link.data,            
            )
            # Or:
            # venue = Venue()
            # form.populate_obj(venue)

            db.session.add(venue)
            db.session.commit()
            flash('Venue ' + form.name.data + ' was successfully listed!')
        except ValueError as e:
            print(e)
            flash('An error occured. Venue ' + form.name.data + 
                ' Could not be listed!')
            db.session.rollback()                
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))
    
    return render_template('pages/home.html')

# 2.- Get Venue:
@app.route('/venues')
def venues():
    locals = []
    venues = Venue.query.all()
    places = Venue.query.distinct(Venue.city, Venue.state).all()
        
    for place in places:
        locals.append({
            'city': place.city,
            'state': place.state,
            'venues': [{
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len([show for show in venue.shows if show.start_time > datetime.now()])
            } for venue in venues if
                venue.city == place.city and venue.state == place.state]
        })
    print(locals[0])
    return render_template('pages/venues.html', areas=locals)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term')
    venues = Venue.query.filter(
        Venue.name.ilike('%{}%'.format(search_term))).all()

    data = []
    for venue in venues:
        tmp = {}
        tmp['id'] = venue.id
        tmp['name'] = venue.name
        tmp['num_upcoming_shows'] = len(venue.shows)
        data.append(tmp)

    response = {}
    response['count'] = len(data)
    response['data'] = data

    return render_template('pages/search_venues.html',
                           results=response,
                           search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first_or_404()

    past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
    ).\
    all()

    upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time > datetime.now()
    ).\
    all()

    data = {
        'id': venue.id,
        'name': venue.name,
        'city': venue.city,
        'state': venue.state,
        'address': venue.address,
        'phone': venue.phone,
        'image_link': venue.image_link,
        'website': venue.website,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'genres': venue.genres,
        'facebook_link': venue.facebook_link,
        'past_shows': [{
            'artist_id': artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in past_shows],
        'upcoming_shows': [{
            'artist_id': artist.id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
        } for artist, show in upcoming_shows],
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows)
    }

    print(venue.genres)

    return render_template('pages/show_venue.html', venue=data)

# 3.- Update Venue:
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # OR:
    # form = VenueForm()
    # venue = Venue.query.get(venue_id).to_dict()
    # return render_template('forms/edit_venue.html', form=form, venue=venue)
    
    venue = Venue.query.first_or_404(venue_id)
    form = VenueForm(obj=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    error = False
    form = VenueForm(request.form, csrf_enabled=False)
    if form.validate():
        try:
            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.image_link = form.image_link.data
            venue.website = form.website.data
            venue.seeking_description = form.seeking_description.data
            venue.genres = form.genres.data
            # Revisar!!!!:
            # tmp_genres = request.form.getlist('genres')
            # venue.genres = ','.join(tmp_genres)  # convert list to string
            venue.facebook_link = form.facebook_link.data

            db.session.add(venue)
            db.session.commit()
            flash('Venue ' + venue.name + ' was successfully updated!')
        except ValueError as e:
            print(e)
            flash('An error occurred. Venue ' + venue.name + 
                ' could not be updated.')
            db.session.rollback()
        finally:
            db.session.close()
            
    return redirect(url_for('show_venue', venue_id=venue_id))

##### SHOWS #####
@app.route('/shows')
def shows():
    shows = Show.query.all()

    data = []
    for show in shows:
        data.append({
            'venue_id': show.venue.id,
            'venue_name': show.venue.name,
            'artist_id': show.artist.id,
            'artist_name': show.artist.name,
            'artist_image_link': show.artist.image_link,
            'start_time': show.start_time.isoformat()
        })

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    form = ShowForm(request.form, csrf_enabled=False)
    if form.validate():
        try:
            # Using FlaskForm:
            show = Show(
                artist_id = form.artist_id.data,
                venue_id = form.venue_id.data,
                start_time = form.start_time.data,
            )
            # Or:
            # show = Show()
            # form.populate_obj(show)

            db.session.add(show)
            db.session.commit()

            flash('Requested show was successfully listed')
        except ValueError as e:
            print(e)
            flash('An error occurred. Requested show could not be listed.')
            db.session.rollback()
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors ' + str(message))

        
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

##### Launch #####

# Default port:
if __name__ == '__main__':
  app.run()