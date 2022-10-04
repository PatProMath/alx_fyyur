from datetime import datetime
from statistics import mode
from unicodedata import name
from flask_wtf import FlaskForm
from wtforms import (
    StringField, 
    IntegerField,
    SelectField, 
    SelectMultipleField,
    TextAreaField, 
    DateTimeField, 
    BooleanField,
    ValidationError
)
import phonenumbers, re
from phonenumbers.phonenumberutil import NumberParseException
from wtforms.fields import TelField
from wtforms.validators import DataRequired, InputRequired, ValidationError, URL, AnyOf

class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id', validators=[DataRequired()]
    )
    venue_id = StringField(
        'venue_id', validators=[DataRequired()]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.now()
    )

    def check_validshow(self, a_id, v_id):

        from models import Artist, Venue
        a_id = self.artist_id.data
        v_id = self.venue_id.data
        artist = Artist.query.filter_by(id=a_id).all()
        venue = Venue.query.filter_by(id=v_id).all()
        if artist and venue:
            return True
        elif artist:
            self.venue_id.errors += (ValidationError('Venue ID ' + v_id + ' does not exist!'),)
            return False
        elif venue:
            self.artist_id.errors += (ValidationError('Artist ID ' + a_id + ' does not exist!'),)
            return False
        else:
            self.artist_id.errors += (ValidationError('Artist ID ' + a_id + ' does not exist!'),)
            self.venue_id.errors += (ValidationError('Venue ID ' + v_id + ' does not exist!'),)
            return False

class DeleteForm(FlaskForm):
    # import models
    # venues = list(models.Venue.query.with_entities(models.Venue.id).all())
    # artists = list(models.Artist.query.with_entities(models.Artist.id).all())

    artist_id = IntegerField(
        'artist-id', validators= [DataRequired()] #, AnyOf(values=venues)
    )
    venue_id = IntegerField(
        'venue-id', validators= [DataRequired()] #, AnyOf(values=artists)
    )

class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()],
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ]
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction. 
        # I have implemented this to the best of my understanding and research on the matter, 
        # using coerce=str and validate_choice
        #Nevertheless, perhaps some indication or directive to this in the review would help. Thnak you.
        'genres', validators=[DataRequired()],
        coerce=str,
        choices=[
            ('Alternative', 'Alternative'),
            ('Blues', 'Blues'),
            ('Classical', 'Classical'),
            ('Country', 'Country'),
            ('Electronic', 'Electronic'),
            ('Folk', 'Folk'),
            ('Funk', 'Funk'),
            ('Hip-Hop', 'Hip-Hop'),
            ('Heavy Metal', 'Heavy Metal'),
            ('Instrumental', 'Instrumental'),
            ('Jazz', 'Jazz'),
            ('Musical Theatre', 'Musical Theatre'),
            ('Pop', 'Pop'),
            ('Punk', 'Punk'),
            ('R&B', 'R&B'),
            ('Reggae', 'Reggae'),
            ('Rock n Roll', 'Rock n Roll'),
            ('Soul', 'Soul'),
            ('Other', 'Other'),
        ],
        validate_choice=True
    )

    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )

    website_link = StringField(
        'website_link', validators=[DataRequired(), URL()]
    )

    image_link = StringField(
        'image_link', validators=[DataRequired(), URL()]
    )

    seeking_talent = BooleanField('seeking_talent' )

    seeking_description = TextAreaField(
        'seeking_description'
    )

    def validate_venuephone(self, phone):
        phone = self.phone.data
        pattern=re.compile("[0-9]{3}[-\s]?[0-9]{3}[-\s]?[0-9]{3}")
        if pattern.match(phone):
            return True
        else:
            print(self.form_errors)
            self.phone.errors += (ValidationError('Invalid phone number.'),)
            return False

    def check_for_venuename(self, a_name):
        from models import Venue
        a_name = self.name.data
        existing_venues = Venue.query.filter_by(name=a_name).all()
        print(existing_venues)
        if existing_venues:
            print(existing_venues)
            self.name.errors += (ValidationError('Venue Name ' + a_name+ ' is already in use!'),)
            return True
        else:
            return False           
                

#  !Personal Note to self: If what has been implemted doesn't pass as required, check out resources in WTForms Bookmarks.

class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        # TODO implement validation logic for state
        'state', validators=[DataRequired()],
        coerce=str,
        choices=[
            ('AL', 'AL'),
            ('AK', 'AK'),
            ('AZ', 'AZ'),
            ('AR', 'AR'),
            ('CA', 'CA'),
            ('CO', 'CO'),
            ('CT', 'CT'),
            ('DE', 'DE'),
            ('DC', 'DC'),
            ('FL', 'FL'),
            ('GA', 'GA'),
            ('HI', 'HI'),
            ('ID', 'ID'),
            ('IL', 'IL'),
            ('IN', 'IN'),
            ('IA', 'IA'),
            ('KS', 'KS'),
            ('KY', 'KY'),
            ('LA', 'LA'),
            ('ME', 'ME'),
            ('MT', 'MT'),
            ('NE', 'NE'),
            ('NV', 'NV'),
            ('NH', 'NH'),
            ('NJ', 'NJ'),
            ('NM', 'NM'),
            ('NY', 'NY'),
            ('NC', 'NC'),
            ('ND', 'ND'),
            ('OH', 'OH'),
            ('OK', 'OK'),
            ('OR', 'OR'),
            ('MD', 'MD'),
            ('MA', 'MA'),
            ('MI', 'MI'),
            ('MN', 'MN'),
            ('MS', 'MS'),
            ('MO', 'MO'),
            ('PA', 'PA'),
            ('RI', 'RI'),
            ('SC', 'SC'),
            ('SD', 'SD'),
            ('TN', 'TN'),
            ('TX', 'TX'),
            ('UT', 'UT'),
            ('VT', 'VT'),
            ('VA', 'VA'),
            ('WA', 'WA'),
            ('WV', 'WV'),
            ('WI', 'WI'),
            ('WY', 'WY'),
        ], 
        validate_choice=True
    )
    phone = StringField(
        'phone', validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        choices=[
            ('Alternative', 'Alternative'),
            ('Blues', 'Blues'),
            ('Classical', 'Classical'),
            ('Country', 'Country'),
            ('Electronic', 'Electronic'),
            ('Folk', 'Folk'),
            ('Funk', 'Funk'),
            ('Hip-Hop', 'Hip-Hop'),
            ('Heavy Metal', 'Heavy Metal'),
            ('Instrumental', 'Instrumental'),
            ('Jazz', 'Jazz'),
            ('Musical Theatre', 'Musical Theatre'),
            ('Pop', 'Pop'),
            ('Punk', 'Punk'),
            ('R&B', 'R&B'),
            ('Reggae', 'Reggae'),
            ('Rock n Roll', 'Rock n Roll'),
            ('Soul', 'Soul'),
            ('Other', 'Other'),
        ],
        validate_choice=True
     )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[URL()]
     )

    website_link = StringField(
        'website_link'
     )

    seeking_venues = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
    )

    def validate_artistphone(self, phone):
        phone = self.phone.data
        pattern=re.compile("[0-9]{3}[-\s]?[0-9]{3}[-\s]?[0-9]{3}")
        if pattern.match(phone):
            return True
        else:
            print(self.form_errors)
            self.phone.errors += (ValidationError('Invalid phone number.'),)
            return False


    def check_for_artistname(self, a_name):
        from models import Artist
        a_name = self.name.data
        existing_artist = Artist.query.filter_by(name=a_name).all()
        print(existing_artist)
        if existing_artist:
            print(existing_artist)
            self.name.errors += (ValidationError('Artist Name ' + a_name + ' is already in use!'),)
            return True
        else:
            return False

    