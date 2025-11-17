from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, TextAreaField, FloatField, DateField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, NumberRange
from app.models import User, Booking
from datetime import date
from flask_login import current_user

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Register as', choices=[('viewer', 'Renter'), ('owner', ' Owner')], validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=7, max=20)])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=7, max=20)])
    submit = SubmitField('Save Changes')

    def validate_email(self, email):
        
        if current_user.is_authenticated:
            user = User.query.filter_by(email=email.data).first()
            if user and user.id != current_user.id:
                raise ValidationError('This email is already registered. Please use a different one.')

class RoomForm(FlaskForm):
    title = StringField('Room Title', validators=[DataRequired(), Length(max=200)])
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])
    rent_price = FloatField('Monthly Rent (Rs)', validators=[DataRequired(), NumberRange(min=0)])
    room_type = SelectField('Room Type', choices=[
        ('Single Room', 'Single Room'),
        ('Attached Room', 'Attached Room'),
        ('Apartment', 'Apartment'),
        ('Single Room and Kitchen Room', 'Single Room and Kitchen Room')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=1000)])
    image = FileField('Room Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    available_from = DateField('Available From', validators=[DataRequired()])
    available_to = DateField('Available To (Optional)')
    submit = SubmitField('Add Room')

class BookingForm(FlaskForm):
    start_date = DateField('Check-in Date', validators=[DataRequired()])
    end_date = DateField('Check-out Date', validators=[DataRequired()])
    submit = SubmitField('Confirm Booking')
    
    def validate(self, **kwargs):
        
        room_id = kwargs.get('room_id')
        
        
        if not super().validate():
            return False
            
        
        if self.start_date.data >= self.end_date.data:
            self.end_date.errors.append('Check-out date must be after check-in date')
            return False
            
        
        if self.start_date.data < date.today():
            self.start_date.errors.append('Check-in date cannot be in the past')
            return False
            

        if room_id:
            existing_booking = Booking.query.filter(
                Booking.room_id == room_id,
                Booking.status.in_(['pending', 'confirmed']), 
                Booking.start_date <= self.end_date.data,
                Booking.end_date >= self.start_date.data
            ).first()
            
            if existing_booking:
                
                start_str = existing_booking.start_date.strftime('%Y-%m-%d')
                end_str = existing_booking.end_date.strftime('%Y-%m-%d')
                
                self.start_date.errors.append(
                    f'Room already booked from {start_str} to {end_str}. Please choose different dates.'
                )
                return False
            
        return True

class ReviewForm(FlaskForm):
    rating = IntegerField('Rating (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField('Your Review', validators=[Length(max=500)])
    submit = SubmitField('Submit Review')

class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
