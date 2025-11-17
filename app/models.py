from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable= False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='viewer')  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_image = db.Column(db.String(255), default='default-user.jpg')


 
    rooms = db.relationship('Room', backref='owner', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='renter', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='reviewer', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    rent_price = db.Column(db.Float, nullable=False)
    room_type = db.Column(db.String(50), nullable=False)  
    description = db.Column(db.Text)
    image_filename = db.Column(db.String(255), default='default_room.jpg')
    available_from = db.Column(db.Date, nullable=False)
    available_to = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    
    bookings = db.relationship('Booking', backref='room', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='room', lazy=True, cascade='all, delete-orphan')

    def average_rating(self):
        if not self.reviews:
            return 0
        return sum(review.rating for review in self.reviews) / len(self.reviews)

    def __repr__(self):
        return f'<Room {self.title}>'

class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    renter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending') 
    total_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

    def __repr__(self):
        return f'<Booking {self.id} for Room {self.room_id}>'

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.id} for Room {self.room_id}>'

