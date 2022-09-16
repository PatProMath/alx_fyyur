#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json, sys
import dateutil.parser
import babel
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from forms import *
from models import Artist, Venue, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Some Function Helpers.
#----------------------------------------------------------------------------#
def flash_errors(form):
  # """Flashes form errors"""   From StackOverflow
  for field, errors in form.errors.items():
    for error in errors:
        flash(u"Error in the %s field - %s" % (
          getattr(form, field).label.text,
          error
        ), 'error')

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
  # I will implement Marshmallow extension in another version, if I have the interest.
  # class VenueSchema(Schema):
  #   id = fields.Integer()
  #   name = fields.String()
  #   num_upcoming_shows = fields.Integer()

  # class LocationSchema(Schema):
  #   city = fields.String()
  #   state = fields.String() 
  #   venues = fields.List(fields.Nested(VenueSchema, many=True))

  def upcoming_shows(id, city, state):
    num_of_shows = Venue.query\
      .with_entities(Venue.id, Show.start_time)\
      .join(Show, id == Show.venue_id)\
      .join(Artist, Artist.id == Show.artist_id)\
      .filter( (Show.start_time > datetime.now()) & 
        (Venue.city==city) &
        (Venue.state==state) )\
      .count()
    return num_of_shows

  dist_locale=Venue.query.with_entities((Venue.id), (Venue.city) , (Venue.state) )\
    .distinct().order_by(Venue.city).order_by(Venue.state).all()
  print(dist_locale)

  all_locations = []
  for result in dist_locale:
    venues = []
    id = result.id
    city = result.city
    state = result.state

    all_venues=Venue.query.filter(Venue.city==city, Venue.state==state).all()

    for a_venue in all_venues:
      if result.city==a_venue.city and result.state==a_venue.state: #My issue is getting another result set of all venues for me to compare their location against.
        num_upcoming_shows = upcoming_shows(id, city, state)
        a_venue_dict = {
          'id': a_venue.id,
          'name': a_venue.name,
          'upcoming_shows': num_upcoming_shows
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
    if location in all_locations: # Check if data of Shows in 'location' is already in 'all_locations' list
      location={}
    else:
      all_locations.append(location)
 
  return render_template('pages/venues.html', areas=all_locations);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  def upcoming_shows(id):
    num_of_shows = Venue.query\
      .with_entities(Venue.id, Show.start_time)\
      .join(Show, id == Show.venue_id)\
      .join(Artist, Artist.id == Show.artist_id)\
      .filter( (Show.start_time > datetime.now()))\
      .count()
    return num_of_shows

  search_term=request.form.get('search_term', '')

  search = Venue.query.filter(Venue.name.ilike(r"%{}%".format(search_term))   |
                        Venue.city.ilike(r"%{}%".format(search_term))    |
                        Venue.state.ilike(r"%{}%".format(search_term))).order_by(Venue.id)
  search_results = search.all()
  count_of_results = search.count()

  data_list = []
  for find in search_results:
    id = find.id
    name = find.name
    data = {
      'id': id,
      'name': name,
      'num_upcoming_shows': upcoming_shows(id)
    }
    data_list.append(data)

  results = {
    "count": count_of_results,
    "data": data_list
  }

  return render_template('pages/search_venues.html', results=results, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  id = venue_id
  venue = Venue.query.get(id)
  venue_dict_data = venue._asdict()

  shows_list = list(
    Show.query.with_entities(Show.artist_id, Artist.name.label('artist_name'), Artist.image_link.label('image_link'), Show.start_time)\
      .filter(Show.artist_id == Artist.id, Show.venue_id == id)
      .all()
  )
# shows_list = list(
#     Venue.query.with_entities(Venue.id, Artist.id, Artist.name, Artist.image_link,Show.start_time)\
#       .join(Show, venue.id == Show.venue_id)
#       .join(Artist, Artist.id == Show.artist_id).all()
#   ) ERROR: sqlalchemy.exc.InvalidRequestError: Can't determine which FROM clause to join from, there are multiple FROMS which can join to this entity. Please use the .select_from() method to establish an explicit left side, as well as providing an explicit ON clause if not present already to help resolve the ambiguity.
# sqlalchemy.exc.ProgrammingError: (psycopg2.errors.DuplicateAlias) table name "artists" specified more than once
# GIVES ISSUES, BUT I DON'T KNOW WHY! What are the BEST PRACTICES IN FLASK-SQLALCHEMY?

  get_past_shows = list(filter(lambda show: show.start_time < datetime.now(), shows_list))
  past_shows_count = len(get_past_shows)
  past_shows = []
  for a_show in get_past_shows:
    show_dict = {
      "artist_id": a_show.artist_id,
      "artist_name": a_show.artist_name,
      "artist_image_link": a_show.image_link,
      "start_time": a_show.start_time.strftime('%m-%d-%Y %H:%M:%S')
    }
    past_shows.append(show_dict)
  

  get_upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(), shows_list))
  upcoming_shows_count = len(get_upcoming_shows)
  upcoming_shows = []
  for a_show in get_upcoming_shows:
    show_dict = {
      "artist_id": a_show.artist_id,
      "artist_name": a_show.artist_name,
      "artist_image_link": a_show.image_link,
      "start_time": a_show.start_time.strftime('%m-%d-%Y %H:%M:%S')
    }
    upcoming_shows.append(show_dict)
  


  iterated_new_key_values=(
    ('past_shows', past_shows),
    ('upcoming_shows', upcoming_shows),
    ('past_shows_count', past_shows_count),
    ('upcoming_shows_count', upcoming_shows_count)
  )
  venue_dict_data.update(iterated_new_key_values)

  return render_template('pages/show_venue.html', venue=venue_dict_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
    
  if form.validate_venuephone(form.phone.data)!=False or \
     form.check_for_venuename(form.name.data)==True or \
      form.validate_on_submit()==False:
    
    flash(f'An error occurred with the validation. Check your inputs!','error')
    flash_errors(form)

    return render_template('forms/new_venue.html', form=form)

  else: #If there are no errors from the validations

    try:
      venue=Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data,
        genres = request.form.getlist('genres'),
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
    return render_template('pages/home.html')
  # see: https://flask.palletsprojects.com/en/2.2.x/patterns/flashing/
  # return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET','DELETE'])
def delete_venue(venue_id):
  try:
    venue_to_delete = Venue.query.get_or_404(venue_id, description="There is no venue with ID {}".format(venue_id))
    db.session.delete(venue_to_delete)
    db.session.commit()
    flash(f'The venue was successfully deleted!')
  except Exception:
    print(sys.exc_info())
    db.session.rollback()
    flash(f'Venue could not be deleted')
  finally:
    db.session.close()
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
  def upcoming_shows(id):
    num_of_shows = Artist.query\
      .with_entities(Artist.id, Show.start_time)\
      .join(Show, id == Show.artist_id)\
      .join(Venue, Venue.id == Show.venue_id)\
      .filter( (Show.start_time > datetime.now())) \
      .count()
    return num_of_shows

  search_term=request.form.get('search_term', '')

  search = Artist.query.filter(Artist.name.ilike(r"%{}%".format(search_term))     | 
                Artist.city.ilike(r"%{}%".format(search_term))  |  
                Artist.state.ilike(r"%{}%".format(search_term))).order_by(Artist.id)
  search_results = search.all()
  count_of_results = search.count()

  data_list = []
  for find in search_results:
    id = find.id
    name = find.name
    data = {
      'id': id,
      'name': name,
      'num_upcoming_shows': upcoming_shows(id)
    }
    data_list.append(data)

  all_results = {
    "count": count_of_results,
    "data": data_list
  }
  return render_template('pages/search_artists.html', results=all_results, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  id = artist_id
  artist = Artist.query.get(id)
  artist_dict_data = artist._asdict()

  shows_list = list(
    Show.query.with_entities(Show.venue_id, Show.artist_id, Venue.name.label('venue_name'), Venue.image_link.label('image_link'), Show.start_time)\
      .join(Venue, Venue.id == Show.venue_id )
      .filter(Show.artist_id == id, Show.venue_id == Venue.id)
      .all()
  )


  get_past_shows = list(filter(lambda show: show.start_time < datetime.now(), shows_list))
  past_shows_count = len(get_past_shows)
  past_shows = []
  for a_show in get_past_shows:
    show_dict = {
      "venue_id": a_show.venue_id,
      "venue_name": a_show.venue_name,
      "venue_image_link": a_show.image_link,
      "start_time": a_show.start_time.strftime('%m-%d-%Y %H:%M:%S')
    }
    past_shows.append(show_dict)
  

  get_upcoming_shows = list(filter(lambda show: show.start_time > datetime.now(), shows_list))
  upcoming_shows_count = len(get_upcoming_shows)
  upcoming_shows = []
  for a_show in get_upcoming_shows:
    show_dict = {
      "venue_id": a_show.venue_id,
      "venue_name": a_show.venue_name,
      "venue_image_link": a_show.image_link,
      "start_time": a_show.start_time.strftime('%m-%d-%Y %H:%M:%S')
    }
    upcoming_shows.append(show_dict)
  


  iterated_new_key_values=(
    ('past_shows', past_shows),
    ('upcoming_shows', upcoming_shows),
    ('past_shows_count', past_shows_count),
    ('upcoming_shows_count', upcoming_shows_count)
  )
  artist_dict_data.update(iterated_new_key_values)

  return render_template('pages/show_artist.html', artist=artist_dict_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  get_artist = Artist.query.get_or_404(artist_id, description='There is no artist data with the ID {}'.format(artist_id))
  artist_dict = get_artist._asdict()

  form = ArtistForm(data=artist_dict) # Or we can have form = ArtistForm(obj=get_artist)
  #  https://wtforms.readthedocs.io/en/2.3.x/forms/#:~:text=obj%20%E2%80%93%20If%20formdata,are%20not%20present.
  
  return render_template('forms/edit_artist.html', form=form, artist=artist_dict)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  id=artist_id
  artist=Artist.query.get(id)
  form = ArtistForm(obj=artist)
  if request.method == 'POST': # Adding this check for a POST method proved to be the only 
    #way to ensure that the application would accept the updated value instead of the old one.
    if form.validate_on_submit()==False or form.validate_artistphone(form.phone.data) == False:
    
      flash(f'An error occurred with the validation. Check your inputs!','error')
      flash_errors(form)
      #Found this as the way to keep the form data from the user's first edit, in case there was some other error with what he had inputted!
      #Had some help about this from here: https://stackoverflow.com/questions/56904775/how-to-redirect-while-keeping-form-data-using-flask-and-wtforms#:~:text=7,for%20redirect.
      #https://wtforms.readthedocs.io/en/3.0.x/forms/?highlight=forms#:~:text=If%20there%20is%20no%20POST%20data%2C%20or%20the%20data%20fails%20to%20validate%2C%20then%20the%20view%20%E2%80%9Cfalls%20through%E2%80%9D%20to%20the%20rendering%20portion.%20The%20Form%20object%20can%20be%20passed%20into%20the%20template%20and%20its%20attributes%20can%20be%20used%20to%20render%20the%20fields%20and%20also%20for%20displaying%20errors%3A
      return render_template('forms/edit_artist.html', form=form, artist=artist) 
    else: #If there are no errors from the validations

      try:
        
        form.populate_obj(artist) # Found out about this function and thought to try it out. 
        #https://wtforms.readthedocs.io/en/3.0.x/crash_course/?highlight=obj#editing-existing-objects
        #But it can be destructive.
        db.session.commit()
        flash(f'Artist ' + form.name.data + ' was successfully edited!', 'success')
      except Exception:
        print(sys.exc_info())
        db.session.rollback()
        flash(f'An error occurred. Artist ' + request.form['name'] + ' was not updated.', 'error')
      finally:
        db.session.close()
      return redirect(url_for('show_artist', artist_id=id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  get_venue = Venue.query.get_or_404(venue_id)
  
  form = VenueForm(obj=get_venue)

  return render_template('forms/edit_venue.html', form=form, venue=get_venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue=Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  if request.method == 'POST': 
    if form.validate_on_submit()==False or form.validate_venuephone(form.phone.data) == False:
    
      flash(f'An error occurred with the validation. Check your inputs!','error')
      flash_errors(form)
      
      return render_template('forms/edit_venue.html', form=form, venue=venue) 
    else: #If there are no errors from the validations

      try:
        
        form.populate_obj(venue)
        db.session.commit()
        flash(f'Artist ' + form.name.data + ' was successfully edited!', 'success')
      except Exception:
        print(sys.exc_info())
        db.session.rollback()
        flash(f'An error occurred. Venue ' + request.form['name'] + ' was not updated.', 'error')
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
  form = ArtistForm()

  if form.validate_artistphone(form.phone.data)==False or \
  form.check_for_artistname(form.name.data)==True or \
    form.validate_on_submit()==False:
  
    flash(f'An error occurred with the validation. Check your inputs!','error')
    flash_errors(form)
    return render_template('forms/new_artist.html', form=form)

  else: #If there are no errors from the validations

    try:
      artist=Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        genres = request.form.getlist('genres'),
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
    return render_template('pages/home.html')

#  Delete Artist
#  ----------------------------------------------------------------

@app.route('/artists/<artist_id>/delete', methods=['GET','DELETE'])
def delete_artist(artist_id):
  try:
    artist_to_delete = Artist.query.get_or_404(artist_id, description="There is no venue with ID {}".format(venue_id))
    db.session.delete(artist_to_delete)
    db.session.commit()
    flash(f'The artist was successfully deleted!')
  except Exception:
    print(sys.exc_info())
    db.session.rollback()
    flash(f'Artist could not be deleted')
  finally:
    db.session.close()
  return redirect(url_for('index', artists=artists, venues=venues))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  
  results = Show.query\
    .with_entities(Show.venue_id, Venue.name.label('venue_name'), Show.artist_id, \
      Artist.name.label('artist_name'), Artist.image_link, Show.start_time)\
    .join(Artist, Show.artist_id == Artist.id)\
    .join(Venue, Show.venue_id == Venue.id).all()

  show_list = []
  for show in results:
    show_dic = {
      "venue_id" : show.venue_id,
      "venue_name" : show.venue_name,
      "artist_id": show.artist_id,
      "artist_name": show.artist_name,
      "artist_image_link": show.image_link,
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
  form = ShowForm()

  if  form.validate_on_submit() == True and \
    form.check_validshow(form.artist_id.data, form.venue_id.data) == True:
    try:

      show = Show(
        artist_id =  form.artist_id.data,
        venue_id =  form.venue_id.data,
        start_time = form.start_time.data
      )
      db.session.add(show)
      db.session.commit()
      flash(f'Show was successfully listed!', 'success')

    except Exception:
      print(sys.exc_info())
      db.session.rollback()
      flash(f'An error occurred. Show could not be listed!', 'error')
    finally:
      db.session.close()

    return render_template('pages/home.html')
  else:
    flash(f'An error occurred with the validation. Check your inputs!','error')
    flash_errors(form)
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
