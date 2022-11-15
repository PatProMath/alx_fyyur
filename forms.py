from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField, 
    SelectMultipleField,
    TextAreaField, 
    DateTimeField, 
    BooleanField,
    SubmitField,
    ValidationError
)
from enums import Genre, State
import re
from wtforms.validators import DataRequired, ValidationError, URL

# state_choices=[
#     ('AL', 'AL'),
#     ('AK', 'AK'),
#     ('AZ', 'AZ'),
#     ('AR', 'AR'),
#     ('CA', 'CA'),
#     ('CO', 'CO'),
#     ('CT', 'CT'),
#     ('DE', 'DE'),
#     ('DC', 'DC'),
#     ('FL', 'FL'),
#     ('GA', 'GA'),
#     ('HI', 'HI'),
#     ('ID', 'ID'),
#     ('IL', 'IL'),
#     ('IN', 'IN'),
#     ('IA', 'IA'),
#     ('KS', 'KS'),
#     ('KY', 'KY'),
#     ('LA', 'LA'),
#     ('ME', 'ME'),
#     ('MT', 'MT'),
#     ('NE', 'NE'),
#     ('NV', 'NV'),
#     ('NH', 'NH'),
#     ('NJ', 'NJ'),
#     ('NM', 'NM'),
#     ('NY', 'NY'),
#     ('NC', 'NC'),
#     ('ND', 'ND'),
#     ('OH', 'OH'),
#     ('OK', 'OK'),
#     ('OR', 'OR'),
#     ('MD', 'MD'),
#     ('MA', 'MA'),
#     ('MI', 'MI'),
#     ('MN', 'MN'),
#     ('MS', 'MS'),
#     ('MO', 'MO'),
#     ('PA', 'PA'),
#     ('RI', 'RI'),
#     ('SC', 'SC'),
#     ('SD', 'SD'),
#     ('TN', 'TN'),
#     ('TX', 'TX'),
#     ('UT', 'UT'),
#     ('VT', 'VT'),
#     ('VA', 'VA'),
#     ('WA', 'WA'),
#     ('WV', 'WV'),
#     ('WI', 'WI'),
#     ('WY', 'WY'),
# ]

# genre_choices=[
#     ('Alternative', 'Alternative'),
#     ('Blues', 'Blues'),
#     ('Classical', 'Classical'),
#     ('Country', 'Country'),
#     ('Electronic', 'Electronic'),
#     ('Folk', 'Folk'),
#     ('Funk', 'Funk'),
#     ('Hip-Hop', 'Hip-Hop'),
#     ('Heavy Metal', 'Heavy Metal'),
#     ('Instrumental', 'Instrumental'),
#     ('Jazz', 'Jazz'),
#     ('Musical Theatre', 'Musical Theatre'),
#     ('Pop', 'Pop'),
#     ('Punk', 'Punk'),
#     ('R&B', 'R&B'),
#     ('Reggae', 'Reggae'),
#     ('Rock n Roll', 'Rock n Roll'),
#     ('Soul', 'Soul'),
#     ('Other', 'Other'),
# ]
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
    delete = SubmitField(
        'delete'
    )

class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()], choices=State.choices
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
        """To the reviewer: The guide was very helpful! Thank you!"""
        'genres', validators=[DataRequired()],
        coerce=str,
        choices=Genre.choices,
        validate_choice=True
    )

    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )

    website_link = StringField(
        'website_link', validators=[URL()]
    )

    image_link = StringField(
        'image_link', validators=[DataRequired(), URL()]
    )

    seeking_talent = BooleanField('seeking_talent' )

    seeking_description = TextAreaField(
        'seeking_description'
    )

    """Deprecated!"""
    # def validate_venuephone(self, phone):
    #     phone = self.phone.data
    #     pattern=re.compile("[0-9]{3}[-\s]?[0-9]{3}[-\s]?[0-9]{3}")
    #     if pattern.match(phone):
    #         return True
    #     else:
    #         print(self.form_errors)
    #         self.phone.errors += (ValidationError('Invalid phone number.'),)
    #         return False

    def check_for_venuename(self, a_name):
        from models import Venue
        a_name = self.name.data
        existing_venues = Venue.query.filter_by(name=a_name).all()
        if existing_venues:
            self.name.errors += (ValidationError('Venue Name "' + a_name+ '" is already in use!'),)
            return False
        else:
            return True   

    def validate(self):
        """Define a custom validate method in your Form:"""
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if not is_valid_phone(self.phone.data):
            self.phone.errors.append('Invalid phone.')
            return False
        if not set(self.genres.data).issubset(dict(Genre.choices()).keys()):
            self.genres.errors.append('Invalid genres.')
            return False
        if self.state.data not in dict(State.choices()).keys():
            self.state.errors.append('Invalid state.')
            return False
        # if entries pass validation
        return True        
                

#  !Personal Note to self: If what has been implemted doesn't pass as required, check out resources in WTForms Bookmarks.

class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired()], choices=State.choices
    )
    phone = StringField(
        'phone', validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired()],
        coerce=str,
        choices=Genre.choices,
        validate_choice=True
    )

    facebook_link = StringField(
        # TODO implement enum restriction! I still don't get how I'm supposed to do this with a facebook link
        'facebook_link', validators=[URL()]
    )

    website_link = StringField(
        'website_link', validators=[URL()]
    )

    seeking_venues = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
    )

    """Deprecated code below. Found something more efficient from Udacity reviews! Check below'"""
    # def validate_artistphone(self, phone):
    #     phone = self.phone.data
    #     pattern=re.compile("[0-9]{3}[-\s]?[0-9]{3}[-\s]?[0-9]{3}")
    #     if pattern.match(phone):
    #         return True
    #     else:
    #         print(self.form_errors)
    #         self.phone.errors += (ValidationError('Invalid phone number.'),)
    #         return False


    def check_for_artistname(self, a_name):
        from models import Artist
        a_name = self.name.data
        existing_artists = Artist.query.filter_by(name=a_name).all()
        print(existing_artists)
        if existing_artists:
            print(existing_artists)
            self.name.errors += (ValidationError('Artist Name "' + a_name+ '" is already in use!'),)
            return False
        else:
            return True

    def validate(self):
        """Define a custom validate method in your Form:"""
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if not is_valid_phone(self.phone.data):
            self.phone.errors.append('Invalid phone.')
            return False
        if not set(self.genres.data).issubset(dict(Genre.choices()).keys()):
            self.genres.errors.append('Invalid genres.')
            return False
        if self.state.data not in dict(State.choices()).keys():
            self.state.errors.append('Invalid state.')
            return False
        # if entries pass validation
        return True

def is_valid_phone(number): ##From Udacity Review 4. Really helpful
    """ Validate phone numbers like:
    1234567890 - no space
    123.456.7890 - dot separator
    123-456-7890 - dash separator
    123 456 7890 - space separator

    Patterns:
    000 = [0-9]{3}
    0000 = [0-9]{4}
    -.  = ?[-. ]

    Note: (? = optional) - Learn more: https://regex101.com/
    """
    regex = re.compile('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
    return regex.match(number)
    