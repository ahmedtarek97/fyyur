#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import SQLALCHEMY_DATABASE_URI 
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# DONE: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
   
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    image_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref="show_venue")

    def __repr__(self):
        return f'<Venue {self.name} >'

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref="show_artist")

    def __repr__(self):
        return f'<Artist {self.name} >'


class Show(db.Model):  

  id = db.Column(db.Integer, primary_key=True)
  venue = db.Column(db.Integer,db.ForeignKey('venue.id'))
  artist = db.Column(db.Integer,db.ForeignKey('artist.id'))
  date = db.Column(db.DateTime)

  def __repr__(self):
        return f'<Show {self.id} {self.date}>'



    # DONE: implement any missing fields, as a database migration using Flask-Migrate

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  # get all the distinct cities and states
  cities = db.session.query(Venue.city,Venue.state).distinct(Venue.city,Venue.state)

  for city in cities:
    city_venues_data = db.session.query(Venue.id, Venue.name).filter(Venue.city == city[0]).filter(Venue.state == city[1])
    data.append({
        "city": city[0],
        "state": city[1],
        "venues": city_venues_data
      })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response = {}
  try:
    search_term = request.form.get('search_term', '')
    matches = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
    data = []

    for match in matches:
      data.append({
        "id": match.id,
        "name": match.name,        
      })
  
    
  except:
    print(sys.exc_info())
    flash("Error occured during searching")

  response = {
        "count": len(matches),
        "data": data
      }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  past_shows = []
  upcoming_shows = []
  clicked_venue = Venue.query.get(venue_id)
  venue_shows = db.session.query(Show).join(Artist).filter(Show.venue == venue_id).all()
  for venue_show in venue_shows:
    if venue_show.date > datetime.now():
      upcoming_shows.append({
      "artist_id": venue_show.artist,
      "artist_name": venue_show.show_artist.name,
      "artist_image_link": venue_show.show_artist.image_link,
      "start_time": venue_show.date.strftime('%Y-%m-%d %H:%M:%S')
      })
    else:
        past_shows.append({
        "artist_id": venue_show.artist,
        "artist_name": venue_show.show_artist.name,
        "artist_image_link": venue_show.show_artist.image_link,
        "start_time": venue_show.date.strftime('%Y-%m-%d %H:%M:%S')
        })
  data = {

    "id": clicked_venue.id,
    "name": clicked_venue.name,
    "genres": clicked_venue.genres,
    "address": clicked_venue.address,
    "city": clicked_venue.city,
    "state": clicked_venue.state,
    "phone": clicked_venue.phone,
    "website": clicked_venue.website,
    "facebook_link": clicked_venue.facebook_link,
    "seeking_talent": clicked_venue.seeking_talent,
    "image_link":clicked_venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),

  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  # Done: modify data to be the data object returned from db insertion
  try:
    venue = Venue(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    address = request.form['address'],
    phone = request.form['phone'],
    image_link = request.form['image_link'],
    genres = request.form['genres'],
    facebook_link = request.form['facebook_link'],
    website = request.form['website'],
    seeking_talent = True if request.form['seeking_talent'] =='Yes' else False ,
    seeking_description = request.form['seeking_description']
    )
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
  # DONE: on unsuccessful db insert, flash an error instead.
  except:
   db.session.rollback()
   print(sys.exc_info())
   flash('An error occurred. Venue ' + request.form['seeking_talent'] + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Done: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash('Venue deleted')
  except:    
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred during deleting')
  finally:
    db.session.close()
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  data= db.session.query(Artist.id,Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response = {}
  try:
    search_term = request.form.get('search_term', '')
    matches = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
    data = []

    for match in matches:
      data.append({
        "id": match.id,
        "name": match.name,        
      })
  
    
  except:
    print(sys.exc_info())
    flash("Error occured during searching")

  response = {
        "count": len(matches),
        "data": data
      }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  past_shows = []
  upcoming_shows = []
  clicked_artist = Venue.query.get(artist_id)
  artist_shows = db.session.query(Show).join(Venue).filter(Show.artist == artist_id).all()
  for artist_show in artist_shows:
    if artist_show.date > datetime.now():
      upcoming_shows.append({
      "venue_id": artist_show.artist,
      "venue_name": artist_show.show_venue.name,
      "venue_image_link": artist_show.show_venue.image_link,
      "start_time": artist_show.date.strftime('%Y-%m-%d %H:%M:%S')
      })
    else:
      past_shows.append({
      "venue_id": artist_show.artist,
      "venue_name": artist_show.show_venue.name,
      "venue_image_link": artist_show.show_venue.image_link,
      "start_time": artist_show.date.strftime('%Y-%m-%d %H:%M:%S')
      })
  data = {

    "id": clicked_artist.id,
    "name": clicked_artist.name,
    "genres": clicked_artist.genres,
    "address": clicked_artist.address,
    "city": clicked_artist.city,
    "state": clicked_artist.state,
    "phone": clicked_artist.phone,
    "website": clicked_artist.website,
    "facebook_link": clicked_artist.facebook_link,
    "seeking_talent": clicked_artist.seeking_talent,
    "image_link":clicked_artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),

  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  if artist: 
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website.data = artist.website
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description

  # DONE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # done: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)

  try: 
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form['image_link']
    artist.facebook_link = request.form['facebook_link']
    artist.website = request.form['website']
    artist.seeking_venue = True if 'seeking_venue' in request.form else False 
    artist.seeking_description = request.form['seeking_description']

    db.session.commit()
    flash('Artist Edited')
  except: 
    
    db.session.rollback()
    print(sys.exc_info())
    flash('Error ocurred')
  finally: 
    db.session.close()
  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue: 
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website.data = venue.website
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)

  try: 
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.seeking_talent = True if request.form['seeking_talent'] =='Yes' else False 
    venue.seeking_description = request.form['seeking_description']
   
   
    db.session.commit()
    flash('Venue Edited')
  except: 
    
    db.session.rollback()
    print(sys.exc_info())
    flash('Error ocurred')
  finally: 
    db.session.close()

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
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  try:
    artist = Artist(name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    phone = request.form['phone'],
    image_link = request.form['image_link'],
    genres = request.form['genres'],
    facebook_link = request.form['facebook_link'],
    website = request.form['website'],
    seeking_venue = True if request.form['seeking_venue'] =='Yes' else False ,
    seeking_description = request.form['seeking_description']
    )
  
    db.session.add(artist)
    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # DONE: on unsuccessful db insert, flash an error instead.
  except:
   db.session.rollback()
   print(sys.exc_info())
   flash('An error occurred. Artist ' + request.form['image_link'] + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # Done: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  queries = db.session.query(Show).join(Artist).join(Venue)
  for query in  queries:
    data.append({
      "venue_id": query.venue,
      "venue_name":query.show_venue.name,
      "artist_id":query.artist,
      "artist_name":query.show_artist.name,
      "artist_image_link":query.show_artist.image_link,
      "start_time": query.date.strftime('%Y-%m-%d %H:%M:%S')


    })


  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE insert form data as a new Show record in the db, instead
  try:
    show = Show(
    artist = request.form['artist_id'],
    venue = request.form['venue_id'],
    date = request.form['start_time'],
    )
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  # DONE: on unsuccessful db insert, flash an error instead.
  except:
   db.session.rollback()
   print(sys.exc_info())
   flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
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
