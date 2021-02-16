from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import (
    StringField, 
    SelectField, 
    SelectMultipleField, 
    DateTimeField,
    BooleanField
    )
from wtforms.fields.core import BooleanField
from wtforms.validators import DataRequired, URL
from enums import Genre, State

class VenueForm(Form):
    name = StringField(
        'name', 
        validators=[DataRequired()]
    )
    city = StringField(
        'city', 
        validators=[DataRequired()]
    )
    state = SelectField(
        'state', 
        validators=[DataRequired()],
        choices=State.choices()
    )
    address = StringField(
        'address', 
        validators=[DataRequired()]
    )
    phone = StringField(
        'phone',
        validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link'
    )
    website = StringField(
        'website',
    )
    seeking_talent = BooleanField(
        'seeking_talent', 
        validators=[DataRequired()]
    )    
    seeking_description = StringField(
        'seeking_description',
        validators=[DataRequired()]
    )
    genres = SelectMultipleField(
        'genres', 
        validators=[DataRequired()],
        choices=Genre.choices(),
    )
    facebook_link = StringField(
        'facebook_link',
    )

    def validate(self):
        """Define a custom validate method in your Form:"""
        rv = Form.validate(self)
        if not rv:
            return False
        if not set(self.genres.data).issubset(dict(Genre.choices()).keys()):
            self.genres.errors.append('Invalid genre.')
            return False
        if self.state.data not in dict(State.choices()).keys():
            self.state.errors.append('Invalid state.')
            return False
        # if pass validation
        return True

class ArtistForm(Form):
    name = StringField(
        'name', 
        validators=[DataRequired()]
    )
    city = StringField(
        'city', 
        validators=[DataRequired()]
    )
    state = SelectField(
        'state', 
        validators=[DataRequired()],
        choices=State.choices()
    )
    phone = StringField(
        'phone', 
        validators=[DataRequired()]
    )
    website = StringField(
        'website', 
        validators=[DataRequired()]
    )    
    seeking_venue = BooleanField(
        'seeking_venue', 
        validators=[DataRequired()],
        )
    seeking_description = StringField(
        'seeking_description', 
        validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link', 
        validators=[DataRequired()]
    )
    genres = SelectMultipleField(
        'genres', 
        validators=[DataRequired()],
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', 
        validators=[URL()]
    )

    def validate(self):
        """Define a custom validate method in your Form:"""
        rv = Form.validate(self)
        if not rv:
            return False
        if not set(self.genres.data).issubset(dict(Genre.choices()).keys()):
            self.genres.errors.append('Invalid genre.')
            return False
        if self.state.data not in dict(State.choices()).keys():
            self.state.errors.append('Invalid state.')
            return False
        # if pass validation
        return True

class ShowForm(Form):
    artist_id = StringField(
        'artist_id', 
        validators=[DataRequired()]
    )
    venue_id = StringField(
        'venue_id', 
        validators=[DataRequired()]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )