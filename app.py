#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json, sys
import dateutil.parser
import babel
from datetime import datetime
from flask import (
  Flask,
  render_template, 
  request, 
  flash, 
  redirect, 
  url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from forms import *
from models import db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
#Resolves issue of circular imports!
db.init_app(app)  # Simply initiates the app here! https://flask-sqlalchemy.palletsprojects.com/en/2.x/api/
migrate = Migrate(app, db)

#How do I interact with the app through the terminal? Is it not possible?
def create_app():
    app = Flask(__name__)
    app.config.from_object("config")

    with app.app_context():
        db.create_all()

    return app

#----------------------------------------------------------------------------#
# Some Function Helpers.
#----------------------------------------------------------------------------#


def flash_errors(form):
  # # """Flashes form errors"""   From StackOverflow
  for field, errors in form.errors.items():
    
    for error in errors:
      flash(u"Error in the %s field - %s" % (
        getattr(form, field).label.text,
        error
      ), 'error')

""" #Dear Udacity reviewer, It didn't work! I didn't have the time to look through it for the problem."""
  # message = []
  # for field, err in form.errors.items():
  #     message.append(field + ' ' + '|'.join(err))
  # flash(u'Errors in validation ' + str(message))

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

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
  all_artists=Artist.query.order_by(db.desc(Artist.created_at)).limit(10).all()
  all_venues= Venue.query.order_by(db.desc(Venue.created_at)).limit(10).all()
  return render_template('pages/home.html', artists=all_artists, venues=all_venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  dist_locale=db.session.query(Venue).with_entities( (Venue.id), (Venue.city) , (Venue.state) )\
    .distinct().order_by(Venue.city).order_by(Venue.state).all()

  all_locations = []
  for result in dist_locale:
    venues = []
    city = result.city
    state = result.state

    all_venues=Venue.query.filter(Venue.city==city, Venue.state==state).all()

    for a_venue in all_venues:
      if result.city==a_venue.city and result.state==a_venue.state: #My issue is getting another result set of all venues for me to compare their location against.
        a_venue_dict = {
          'id': a_venue.id,
          'name': a_venue.name
        }
        if a_venue_dict in venues: # checks for uniqueness of the venue_dict object.
          venues.remove(a_venue_dict)
          venues.append(a_venue_dict)
        else: 
          venues.append(a_venue_dict)

    location = {
      'city': city,
      'state': state,
      'venues': venues
    }

    if location in all_locations: # Check if data of location is already in 'all_locations' list
      location={}
    else:
      all_locations.append(location)
    
  return render_template('pages/venues.html', areas=all_locations)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term', '')
  search = Venue.query.filter(Venue.name.ilike(r"%{}%".format(search_term))   |
                        Venue.city.ilike(r"%{}%".format(search_term))    |
                        Venue.state.ilike(r"%{}%".format(search_term))).order_by(Venue.id)
  search_results = search.all()
  count_of_results = search.count()

  data_list = []
  for match in search_results:
    id = match.id
    name = match.name
    shows = list(filter(lambda show: show.start_time > datetime.now(), match.shows))
    data = {
      'id': id,
      'name': name,
      'num_upcoming_shows': len(shows)
    }
    data_list.append(data)

  results = {
    "count": count_of_results,
    "data": data_list
  }

  return render_template('pages/search_venues.html', results=results, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  """Dear Udacity Reviewer, I didn't understand the instruction in this section for a long time and struggled, 
  but I believe I eventually got it.
  I have implemented the JOIN using the 'back_populates' property in my models.py file. A video from PrettyPrinted proved helpful.
  The code is much cleaner with the if sorting each show to past or upcoming. Thank you. 
  
  But:
  1 I didn't get to see the interpreted SQL statements. Perhaps, I didn't integrate the SQLALCHEMY_ECHO statement appropriately?
  2 How can I use the association_proxy safely, to have for example, artist.venues.append(venue) 
  
  P.S.: Excuse me, but I cannot access any of the knowledge questions and answers. 
  It seems my scholarship doesn't cover that service.
  """
  venue = Venue.query.get_or_404(venue_id)
  # venue_dict_data = venue._asdict()

  past_shows = []
  upcoming_shows = []

  #venue_shows = venue.shows, is an alternative to the code below. Or just directly say, 'for show in venue.shows'
  venue_shows = db.session.query(Show).join(Venue, Show.venue_id == venue_id).\
    join(Artist, Show.artist_id == Artist.id)

  """
  The SQLAlchemy code translates to:

  SELECT shows.id AS shows_id, shows.artist_id AS shows_artist_id, 
  shows.venue_id AS shows_venue_id, shows.start_time AS shows_start_time
  FROM shows JOIN venues ON shows.venue_id = %(venue_id_1)s JOIN artists ON shows.artist_id = artists.id
    
  """

  for show in venue_shows:
    a_show = {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.strftime("%m-%d-%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
        past_shows.append(a_show)
    else:
        upcoming_shows.append(a_show)

  # Converts object class to dict
  data = vars(venue) 

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  form = VenueForm(request.form, meta={'csrf':False})
  name = form.name.data

  # Validate all fields and check for unique venue name  and form.check_for_venuename(form.name.data)==True:
  if form.validate() and form.check_for_venuename(name):
    try:
      venue=Venue(
        name = name,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        genres = form.genres.data,
        facebook_link = form.facebook_link.data,
        image_link = form.image_link.data,
        website_link = form.website_link.data,
        seeking_talent = form.seeking_talent.data,
        seeking_description = form.seeking_description.data
      )
      db.session.add(venue)
      db.session.commit()
      flash(f'Venue ' + request.form['name'] + ' was successfully listed!', 'success')
    except Exception:
      print(sys.exc_info())
      db.session.rollback()
      flash(f'An error occurred. Venue ' + form.name.data + ' could not be listed.', 'error')
    finally:
      db.session.close()
    artists=Artist.query.order_by(db.desc(Artist.created_at)).limit(10).all()
    venues= Venue.query.order_by(db.desc(Venue.created_at)).limit(10).all()

  # If there is any invalid field
  else:
    flash(f'There are errors with the validation.')
    flash_errors(form) 
    form=VenueForm()
    return render_template('forms/new_venue.html', form=form)
  return render_template('pages/home.html', artists=artists, venues=venues)

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue_form(venue_id):
  # Anything I might want to add goes HERE
  form = DeleteForm()
  venue_to_delete = db.session.query(Venue).get_or_404(venue_id, description="There is no venue with ID {}".format(venue_id))
  return render_template('forms/delete_venue.html', form=form, venue=venue_to_delete)

@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  if request.method == 'POST':
    try:
      venue_to_delete = db.session.query(Venue).get_or_404(venue_id, description="There is no venue with ID {}".format(venue_id))
      db.session.delete(venue_to_delete)
      db.session.commit()
      flash(f'The venue was successfully deleted!', 'success')
    except Exception:
      print(sys.exc_info())
      db.session.rollback()
      flash(f'Venue could not be deleted', 'error')
    finally:
      db.session.close()
  else:
    flash(f'Error!')
  return redirect(url_for('index', artists=artists, venues=venues))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  all_artists = Artist.query.with_entities(Artist.id, Artist.name).all()
  all_artists_list = []
  for an_artist in all_artists:
    artist_dict = {
      'id': an_artist.id,
      'name': an_artist.name
    }
    all_artists_list.append(artist_dict)

  return render_template('pages/artists.html', artists=all_artists_list)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  search_term=request.form.get('search_term', '')
  search = Artist.query.filter(Artist.name.ilike(r"%{}%".format(search_term))     | 
                Artist.city.ilike(r"%{}%".format(search_term))  |  
                Artist.state.ilike(r"%{}%".format(search_term))).order_by(Artist.id)
  search_results = search.all()
  count_of_results = search.count()

  data_list = []
  for match in search_results:
    shows = list(filter(lambda show: show.start_time > datetime.now(), match.shows))
    id = match.id
    name = match.name
    data = {
      'id': id,
      'name': name,
      'num_upcoming_shows': shows
    }
    data_list.append(data)

  all_results = {
    "count": count_of_results,
    "data": data_list
  }
  return render_template('pages/search_artists.html', results=all_results, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  # artist_dict_data = artist._asdict()

  past_shows = []
  upcoming_shows = []
  
  artist_shows = db.session.query(Show).join(Venue, Show.venue_id == Venue.id).\
    join(Artist, Show.artist_id == artist_id)
  """
  The SQLAlchemy code translates to:

  SELECT shows.id AS shows_id, shows.artist_id AS shows_artist_id, 
  shows.venue_id AS shows_venue_id, shows.start_time AS shows_start_time
  FROM shows JOIN venues ON shows.venue_id = venues.id JOIN artists ON shows.artist_id = %(artist_id_1)s
  
  """

  for show in artist_shows:
    a_show = {
        'venue_id': show.venue_id,
        'venue_name': show.venue.name,
        'venue_image_link': show.venue.image_link,
        'start_time': show.start_time.strftime("%m-%d-%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
        past_shows.append(a_show)
    else:
        upcoming_shows.append(a_show)

  # Converts object class to dict. Alternative method to my created ,as_dict() function
  data = vars(artist) 

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  get_artist = Artist.query.get_or_404(artist_id, description='There is no artist data with the ID {}'.format(artist_id))
  artist_dict = get_artist._asdict()
  form = ArtistForm(obj=get_artist) 
  return render_template('forms/edit_artist.html', form=form, artist=artist_dict)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  """"
  This implementation to protect against rejected inputs is not the best or the cleanest, I think.
  But, I don't think putting the validation code in a function to call will be possible. I'm not so sure. 
  I tried to do that but I was afraid that my lines of codew would fall apart.
  Moreover, I want to maintain this check for uniqueness of the artists or venues to an extent.
  """
  artist=db.session.query(Artist).get_or_404(artist_id)
  form = ArtistForm(request.form, meta={'csrf': False})
  if request.method == 'POST': # Adding this check for a POST method proved to be the only 
  #way to ensure that the application would accept the updated value instead of the old one.
    if form.name.data == artist.name:
      if form.validate():
        try:
          #Note: Putting commas after values, e.g. 
          # artist.name = form.name.data,
          # artist.city = form.city.data, may corrupt the form.attr.data value being sent. It can give ('Angela Yu',) instead of Angela Yu as the name or ('False',) instead of False, causing errors.
          '''If I try to include artist.name = form.name.data, I get an error because of the name check!
          Of course, I only found out about these issue because of input entries that were validated properly during testing.
          With the way the application is set up now, I doubt that could happen. 
          OH, IT STILL HAPPENS! IF I WANT TO PROPERLY GUARD AGAINST DUPLICATE NAMES, IT WILL COME UP
          Is it possible to change a record already inputted in the database, e.g. an Artist's name and 
          still have it maintain the duplicate name check for other inputs.
          '''
          artist.name = form.name.data 
          #print(artist.name)
          artist.city = form.city.data
          artist.state = form.state.data
          artist.phone = form.phone.data
          artist.genres = form.genres.data
          artist.facebook_link = form.facebook_link.data
          artist.image_link = form.image_link.data
          artist.website_link = form.website_link.data
          artist.seeking_venues = form.seeking_venues.data
          artist.seeking_description = form.seeking_description.data
    
          db.session.commit()
          flash(f'Artist ' + artist.name + ' was successfully edited!', 'success')
          print(artist.name)
        except Exception:
          print(sys.exc_info())
          db.session.rollback()
          flash(f'An error occurred. Artist ' + artist.name + ' was not updated.', 'error')
        finally:
          db.session.close()
        #return redirect(url_for('show_artist', artist=artist, artist_id=id)) # redirect method gives me the HTTP 302 issue. But I need the method to do the logic in show_artist
        #Note also that using return redirect(url_for('show_artist', artist=artist, artist_id=id)) will give an error from the implementation I made in show_venue.html to resolve the genres display format.
        return render_template('pages/show_artist.html', artist=artist, artist_id=id)  # However, this does not format the genres correctly for display. So, I made an implementation in show_venue.html after a fashion. Line 13!
        
      else: #If there are no errors from the validations

        flash(f'An error occurred with the validation. Check your inputs!','error')
        flash_errors(form)
        form = ArtistForm()
        #Found this as the way to keep the form data from the user's first edit, in case there was some other error with what he had inputted!
        #Had some help about this from here: https://stackoverflow.com/questions/56904775/how-to-redirect-while-keeping-form-data-using-flask-and-wtforms#:~:text=7,for%20redirect.
        #https://wtforms.readthedocs.io/en/3.0.x/forms/?highlight=forms#:~:text=If%20there%20is%20no%20POST%20data%2C%20or%20the%20data%20fails%20to%20validate%2C%20then%20the%20view%20%E2%80%9Cfalls%20through%E2%80%9D%20to%20the%20rendering%20portion.%20The%20Form%20object%20can%20be%20passed%20into%20the%20template%20and%20its%20attributes%20can%20be%20used%20to%20render%20the%20fields%20and%20also%20for%20displaying%20errors%3A
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    else:
      if form.validate() and form.check_for_artistname(form.name.data):
        try:
          artist.name = form.name.data 
          artist.city = form.city.data
          artist.state = form.state.data
          artist.phone = form.phone.data
          artist.genres = form.genres.data
          artist.facebook_link = form.facebook_link.data
          artist.image_link = form.image_link.data
          artist.website_link = form.website_link.data
          artist.seeking_venues = form.seeking_venues.data
          artist.seeking_description = form.seeking_description.data
    
          db.session.commit()
          flash(f'Artist ' + artist.name + ' was successfully edited!', 'success')
          print(artist.name)
        except Exception:
          print(sys.exc_info())
          db.session.rollback()
          flash(f'An error occurred. Artist ' + artist.name + ' was not updated.', 'error')
        finally:
          db.session.close()
        #return redirect(url_for('show_artist', artist=artist, artist_id=id)) # redirect method gives me the HTTP 302 issue. But I need the method to do the logic in show_artist
        #Note also that using return redirect(url_for('show_artist', artist=artist, artist_id=id)) will give an error from the implementation I made in show_venue.html to resolve the genres display format.
        return render_template('pages/show_artist.html', artist=artist, artist_id=id)  # However, this does not format the genres correctly for display. So, I made an implementation in show_venue.html after a fashion. Line 13!
        
      else: #If there are no errors from the validations

        flash(f'An error occurred with the validation. Check your inputs!','error')
        flash_errors(form)
        form = ArtistForm()
        #Found this as the way to keep the form data from the user's first edit, in case there was some other error with what he had inputted!
        #Had some help about this from here: https://stackoverflow.com/questions/56904775/how-to-redirect-while-keeping-form-data-using-flask-and-wtforms#:~:text=7,for%20redirect.
        #https://wtforms.readthedocs.io/en/3.0.x/forms/?highlight=forms#:~:text=If%20there%20is%20no%20POST%20data%2C%20or%20the%20data%20fails%20to%20validate%2C%20then%20the%20view%20%E2%80%9Cfalls%20through%E2%80%9D%20to%20the%20rendering%20portion.%20The%20Form%20object%20can%20be%20passed%20into%20the%20template%20and%20its%20attributes%20can%20be%20used%20to%20render%20the%20fields%20and%20also%20for%20displaying%20errors%3A
        return render_template('forms/edit_artist.html', form=form, artist=artist) 


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  get_venue = Venue.query.get_or_404(venue_id)
  form = VenueForm(obj=get_venue) #Does not automatically effect the genres form selection

  return render_template('forms/edit_venue.html', form=form, venue=get_venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  venue=db.session.query(Venue).get(venue_id) #Note: venue=Venue.query.get(venue_id) does not EFFECT  UPDATES TO THE DATABASE!
  #More Info here! == https://stackoverflow.com/questions/29194926/python-flask-db-session-commit-is-not-working 
  form = VenueForm(request.form, meta={'csrf': False})
  if request.method == 'POST': 
    if form.name.data == venue.name:
      if form.validate():
        try:
          venue.name = form.name.data
          venue.city = form.city.data
          venue.state = form.state.data
          venue.phone = form.phone.data
          venue.genres = form.genres.data
          venue.facebook_link = form.facebook_link.data
          venue.image_link = form.image_link.data
          venue.website_link = form.website_link.data
          venue.seeking_talent = form.seeking_talent.data
          venue.seeking_description = form.seeking_description.data

          db.session.commit()

          flash(f'Venue ' + venue.name + ' was successfully edited!', 'success')
        except Exception:
          print(sys.exc_info())
          db.session.rollback()
          flash(f'An error occurred. Venue ' + request.form['name'] + ' was not updated.', 'error')
        finally:
          db.session.close()
        return render_template('pages/show_venue.html', venue=venue) #Note using form.poulate_obj(venue) with this new implementation also doesn't work
        #This method also has the issue if not giving the other added data from the show_venue or show_artist endpoint
      else: #If there are errors 

        flash(f'An error occurred with the validation. Check your inputs!','error')
        flash_errors(form)
        form=VenueForm()
        return render_template('forms/edit_venue.html', form=form, venue=venue) 
    else:
      if form.validate() and form.check_for_venuename(form.name.data):
        try:
          venue.name = form.name.data
          venue.city = form.city.data
          venue.state = form.state.data
          venue.phone = form.phone.data
          venue.genres = form.genres.data
          venue.facebook_link = form.facebook_link.data
          venue.image_link = form.image_link.data
          venue.website_link = form.website_link.data
          venue.seeking_talent = form.seeking_talent.data
          venue.seeking_description = form.seeking_description.data

          db.session.commit()

          flash(f'Venue ' + venue.name + ' was successfully edited!', 'success')
        except Exception:
          print(sys.exc_info())
          db.session.rollback()
          flash(f'An error occurred. Venue ' + request.form['name'] + ' was not updated.', 'error')
        finally:
          db.session.close()
        return render_template('pages/show_venue.html', venue=venue) #Note using form.poulate_obj(venue) with this new implementation also doesn't work
        #This method also has the issue if not giving the other added data from the show_venue or show_artist endpoint
      else: #If there are errors 

        flash(f'An error occurred with the validation. Check your inputs!','error')
        flash_errors(form)
        form=VenueForm()
        return render_template('forms/edit_venue.html', form=form, venue=venue) 
        
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form, meta={'csrf': False})
  #Validates the form
  if form.validate() and form.check_for_artistname(form.name.data):
  
    try:
      artist=Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        genres = form.genres.data,
        facebook_link = form.facebook_link.data,
        image_link = form.image_link.data,
        website_link = form.website_link.data,
        seeking_venues = form.seeking_venues.data,
        seeking_description = form.seeking_description.data
      )
      db.session.add(artist)
      db.session.commit()
      flash(f'Artist ' + form.name.data + ' was successfully listed!', 'success')
    except Exception:
      print(sys.exc_info())
      db.session.rollback()
      flash(f'An error occurred. Artist ' + request.form['name'] + ' could not be listed.', 'error')
    finally:
      db.session.close()
    artists=Artist.query.order_by(db.desc(Artist.created_at)).limit(10).all()
    venues= Venue.query.order_by(db.desc(Venue.created_at)).limit(10).all()

  else: # If there is any invalid field
    
    flash(f'An error occurred with the validation. Check your inputs!','error')
    flash_errors(form)
    form=ArtistForm()
    return render_template('forms/new_artist.html', form=form)
  return render_template('pages/home.html', artists=artists, venues=venues)

#  Delete Artist
#  ----------------------------------------------------------------
@app.route('/artists/<artist_id>/delete', methods=['GET'])
def delete_artist_form(artist_id):
  form = DeleteForm()
  artist_to_delete = Artist.query.get_or_404(artist_id, description="There is no venue with ID {}".format(artist_id))
  return render_template('forms/delete_artist.html', form=form, artist=artist_to_delete)

@app.route('/artists/<artist_id>/delete', methods=['POST'])
def delete_artist(artist_id):
  if request.method == 'POST':
    try:
      artist_to_delete = db.session.query(Artist).get_or_404(artist_id, description="There is no venue with ID {}".format(artist_id))
      db.session.delete(artist_to_delete)
      db.session.commit()
      flash(f'The artist was successfully deleted!')
    except Exception:
      print(sys.exc_info())
      db.session.rollback()
      flash(f'Artist could not be deleted')
    finally:
      db.session.close()
  else:
    flash(f'Error!')
  return redirect(url_for('index', artists=artists, venues=venues))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  
  shows = Show.query.all()
  show_list = []
  for show in shows:
    show_dic = {
      "venue_id" : show.venue_id,
      "venue_name" : show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%m-%d-%Y %H:%M:%S')
    }
    show_list.append(show_dic)
  
  return render_template('pages/shows.html', shows=show_list)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  form = ShowForm(request.form, meta={'csrf':False})
  # Get the artist and venue who have the show
  artist=db.session.query(Artist).get(form.artist_id.data)
  venue=db.session.query(Venue).get(form.venue_id.data)

  if  form.validate() and form.check_validshow(form.artist_id.data, form.venue_id.data):
    try:
      show = Show(
        start_time = form.start_time.data, 
        artist=artist, 
        venue=venue
      )
      # How can I use the association_proxy safely, to have for example, artist.venues.append(venue) 

      # print('The shows of the artist '+ artist.name)
      # for assoc in artist.shows:
      #   print("Start time: ")
      #   print(assoc.start_time)
      #   print("The venue: ")
      #   print( assoc.venue.name)
      
      # print('The shows at the venue '+ venue.name)
      # for assoc in venue.shows:
      #   print("Start time: ")
      #   print(assoc.start_time)
      #   print("The artist: ")
      #   print( assoc.artist.name)

      db.session.add(show)
      db.session.commit()
      flash(f'Show was successfully listed!', 'success')

    except Exception:
      print(sys.exc_info())
      db.session.rollback()
      flash(f'An error occurred. Show could not be listed!', 'error')
    finally:
      db.session.close()

    return redirect(url_for('index', artists=artists, venues=venues))
  else:
    flash(f'An error occurred with the validation. Check your inputs!','error')
    flash_errors(form)
    form=ShowForm()
    return render_template('forms/new_show.html', form=form)
  

@app.errorhandler(404)
def not_found_error(description):
  #Is there a way I can add more description of the error, like in the case of the get_or_404()
  return render_template('errors/404.html', description=description), 404

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
