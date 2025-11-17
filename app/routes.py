from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Room, Booking, Review
from app.forms import RegistrationForm, LoginForm, RoomForm, BookingForm, ReviewForm
from datetime import datetime ,date
from app.forms import ProfileForm  ,ResetPasswordForm
import os


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def register_context_processor(app):
    @app.context_processor
    def utility_processor():
        def pending_bookings_count():
            if current_user.is_authenticated and current_user.role == 'owner':
                owner_rooms = Room.query.filter_by(owner_id=current_user.id).all()
                room_ids = [room.id for room in owner_rooms]
                return Booking.query.filter(
                    Booking.room_id.in_(room_ids), 
                    Booking.status == 'pending'
                ).count()
            return 0
        return dict(pending_bookings_count=pending_bookings_count)


def register_routes(app):

    register_context_processor(app)

    @app.route('/')
    def index():
        rooms = Room.query.filter_by(status='approved').order_by(Room.created_at.desc()).limit(6).all()
        return render_template('index.html', rooms=rooms)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(
                name=form.name.data,
                email=form.email.data,
                role=form.role.data,
                phone=form.phone.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()

            if user and user.check_password(form.password.data):
                login_user(user)
                flash(f'Welcome back, {user.name}!', 'success')

                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))

            else:
                flash('Invalid email or password', 'danger')

        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        role = current_user.role  

        if role == 'admin':
            pending_rooms = Room.query.filter_by(status='pending').all()
            total_users = User.query.count()
            total_rooms = Room.query.count()
            total_bookings = Booking.query.count()

            return render_template(
                'admin_panel.html',
                pending_rooms=pending_rooms,
                total_users=total_users,
                total_rooms=total_rooms,
                total_bookings=total_bookings,
                user=current_user,
                role=role
            )

        if role == 'owner':
            my_rooms = Room.query.filter_by(owner_id=current_user.id).all()
            return render_template(
                'dashboard.html',
                rooms=my_rooms,
                user=current_user,
                role=role
            )
        
        if role == 'viewer':
            my_bookings = Booking.query.filter_by(renter_id=current_user.id).all()
            return render_template(
                'viewer_booking.html',
                bookings=my_bookings,
                user=current_user,
                role=role
            )

    @app.route('/add_room', methods=['GET', 'POST'])
    @login_required
    def add_room():
        if current_user.role not in ['owner']:
            flash('Only room owners can add rooms.', 'danger')
            return redirect(url_for('index'))

        form = RoomForm()
        if form.validate_on_submit():
            filename = 'default_room.jpg'

            if form.image.data and allowed_file(form.image.data.filename):
                file = form.image.data
                filename = secure_filename(file.filename)
                filename = f"{int(datetime.now().timestamp())}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            room = Room(
                owner_id=current_user.id,
                title=form.title.data,
                location=form.location.data,
                rent_price=form.rent_price.data,
                room_type=form.room_type.data,
                description=form.description.data,
                image_filename=filename,
                available_from=form.available_from.data,
                available_to=form.available_to.data,
                status='pending' if current_user.role != 'admin' else 'approved'
            )

            db.session.add(room)
            db.session.commit()

            flash('Room listing submitted successfully!', 'success')
            return redirect(url_for('dashboard'))

        return render_template('add_room.html', form=form)

    @app.route('/rooms')
    def room_list():
        location = request.args.get('location', '')
        room_type = request.args.get('room_type', '')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)

        query = Room.query.filter_by(status='approved')

        if location:
            query = query.filter(Room.location.contains(location))
        if room_type:
            query = query.filter_by(room_type=room_type)
        if min_price:
            query = query.filter(Room.rent_price >= min_price)
        if max_price:
            query = query.filter(Room.rent_price <= max_price)

        rooms = query.all()
        return render_template('room_list.html', rooms=rooms)

    @app.route('/room/<int:room_id>')
    def room_details(room_id):
        room = Room.query.get_or_404(room_id)
        reviews = Review.query.filter_by(room_id=room_id).order_by(Review.created_at.desc()).all()
        
        existing_bookings = Booking.query.filter(
            Booking.room_id == room_id,
            Booking.status.in_(['confirmed'])
        ).all()
        
        return render_template('room_details.html', room=room, reviews=reviews, existing_bookings=existing_bookings)

    @app.route('/book/<int:room_id>', methods=['GET', 'POST'])
    @login_required
    def book_room(room_id):
        if current_user.role != 'viewer':
            flash('Only renters can book rooms.', 'danger')
            return redirect(url_for('room_details', room_id=room_id))

        room = Room.query.get_or_404(room_id)
        form = BookingForm()

        existing_bookings = Booking.query.filter(
            Booking.room_id == room_id,
            Booking.status.in_(['confirmed'])
        ).all()
        min_date = date.today().isoformat()
        if form.validate_on_submit():
           
            if form.validate(room_id=room_id):
                days = (form.end_date.data - form.start_date.data).days
                total = round(days * (room.rent_price / 30))

                booking = Booking(
                    room_id=room_id,
                    renter_id=current_user.id,
                    start_date=form.start_date.data,
                    end_date=form.end_date.data,
                    total_price=total,
                    status='pending'
                )

                db.session.add(booking)
                db.session.commit()
                flash('Booking request submitted! Waiting for owner approval.', 'success')
                return redirect(url_for('dashboard'))
            else:
              
                flash('Cannot book room for the selected dates. Please check the errors below.', 'danger')

        return render_template('booking.html', room=room, form=form, existing_bookings=existing_bookings ,min_date=min_date)

    @app.route('/review/<int:room_id>', methods=['GET', 'POST'])
    @login_required
    def add_review(room_id):
        room = Room.query.get_or_404(room_id)

        existing = Review.query.filter_by(room_id=room_id, reviewer_id=current_user.id).first()
        if existing:
            flash('You already reviewed this room.', 'warning')
            return redirect(url_for('room_details', room_id=room_id))

        form = ReviewForm()

        if form.validate_on_submit():
            review = Review(
                room_id=room_id,
                reviewer_id=current_user.id,
                rating=form.rating.data,
                comment=form.comment.data
            )
            db.session.add(review)
            db.session.commit()

            flash('Review added!', 'success')
            return redirect(url_for('room_details', room_id=room_id))

        return render_template('reviews.html', room=room, form=form)

    @app.route('/approve/<int:room_id>')
    @login_required
    def approve_room(room_id):
        if current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))

        room = Room.query.get_or_404(room_id)
        room.status = 'approved'
        db.session.commit()

        flash(f'Room "{room.title}" approved!', 'success')
        return redirect(url_for('dashboard'))

    @app.route('/reject/<int:room_id>')
    @login_required
    def reject_room(room_id):
        if current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))

        room = Room.query.get_or_404(room_id)
        room.status = 'rejected'
        db.session.commit()

        flash(f'Room "{room.title}" rejected.', 'warning')
        return redirect(url_for('dashboard'))

    @app.route('/delete_room/<int:room_id>')
    @login_required
    def delete_room(room_id):
        room = Room.query.get_or_404(room_id)

        if current_user.role != 'admin' and room.owner_id != current_user.id:
            flash('You do not have permission to delete this room.', 'danger')
            return redirect(url_for('dashboard'))

        db.session.delete(room)
        db.session.commit()

        flash('Room deleted successfully.', 'success')
        return redirect(url_for('dashboard'))

    @app.route('/cancel_booking/<int:booking_id>')
    @login_required
    def cancel_booking(booking_id):
        booking = Booking.query.get_or_404(booking_id)

        if booking.renter_id != current_user.id:
            flash('You can only cancel your own bookings.', 'danger')
            return redirect(url_for('dashboard'))

        booking.status = 'cancelled'
        db.session.commit()

        flash('Booking cancelled.', 'info')
        return redirect(url_for('dashboard'))

    @app.route('/edit_room/<int:room_id>', methods=['GET', 'POST'])
    @login_required
    def edit_room(room_id):
        room = Room.query.get_or_404(room_id)

        if current_user.role != 'admin' and room.owner_id != current_user.id:
            flash('You do not have permission to edit this room.', 'danger')
            return redirect(url_for('dashboard'))

        form = RoomForm(obj=room)

        if form.validate_on_submit():
            room.title = form.title.data
            room.location = form.location.data
            room.rent_price = form.rent_price.data
            room.room_type = form.room_type.data
            room.description = form.description.data
            room.available_from = form.available_from.data
            room.available_to = form.available_to.data

            if form.image.data and allowed_file(form.image.data.filename):
                file = form.image.data
                filename = secure_filename(file.filename)
                filename = f"{int(datetime.now().timestamp())}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                room.image_filename = filename

            db.session.commit()
            flash('Room updated successfully!', 'success')

            return redirect(url_for('dashboard'))

        return render_template('edit_room.html', form=form, room=room)

    @app.route('/owner/bookings')
    @login_required
    def owner_bookings():
        if current_user.role != 'owner':
            flash('Only room owners can access this page.', 'danger')
            return redirect(url_for('dashboard'))
        
        owner_rooms = Room.query.filter_by(owner_id=current_user.id).all()
        
        room_ids = [room.id for room in owner_rooms]
        bookings = Booking.query.filter(Booking.room_id.in_(room_ids)).order_by(Booking.created_at.desc()).all()
        
        return render_template('owner_bookings.html', bookings=bookings)

    @app.route('/owner/booking/<int:booking_id>/approve')
    @login_required
    def approve_booking(booking_id):
        if current_user.role != 'owner':
            flash('Only room owners can manage bookings.', 'danger')
            return redirect(url_for('dashboard'))
        
        booking = Booking.query.get_or_404(booking_id)
        
        if booking.room.owner_id != current_user.id:
            flash('You are not authorized to manage this booking.', 'danger')
            return redirect(url_for('owner_bookings'))
        
        if booking.status != 'pending':
            flash('This booking is no longer pending.', 'warning')
            return redirect(url_for('owner_bookings'))
        
        booking.status = 'confirmed'
        booking.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Booking approved successfully!', 'success')
        return redirect(url_for('owner_bookings'))

    @app.route('/owner/booking/<int:booking_id>/reject')
    @login_required
    def reject_booking(booking_id):
        if current_user.role != 'owner':
            flash('Only room owners can manage bookings.', 'danger')
            return redirect(url_for('dashboard'))
        
        booking = Booking.query.get_or_404(booking_id)
        
        if booking.room.owner_id != current_user.id:
            flash('You are not authorized to manage this booking.', 'danger')
            return redirect(url_for('owner_bookings'))
        
        if booking.status != 'pending':
            flash('This booking is no longer pending.', 'warning')
            return redirect(url_for('owner_bookings'))
        
        booking.status = 'rejected'
        booking.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Booking rejected.', 'info')
        return redirect(url_for('owner_bookings'))
    



    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        form = ProfileForm(obj=current_user)
        
        if request.method == 'POST':
          
            if 'photo' in request.files:
                file = request.files['photo']
                
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    filename = f"{int(datetime.now().timestamp())}_{filename}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    current_user.profile_image = filename
                    db.session.commit()

                    flash("Profile photo updated successfully!", "success")
                    return redirect(url_for('profile'))
            
            if form.validate_on_submit():
             
                if form.email.data != current_user.email:
                    existing_user = User.query.filter_by(email=form.email.data).first()
                    if existing_user and existing_user.id != current_user.id:
                        flash('This email is already registered. Please use a different one.', 'danger')
                        return render_template('profile.html', user=current_user, form=form)
                
                current_user.name = form.name.data
                current_user.email = form.email.data
                current_user.phone = form.phone.data
                
                db.session.commit()
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('profile'))

        return render_template('profile.html', user=current_user, form=form)
    
    @app.route('/user/profile/<int:user_id>')
    @login_required
    def view_user_profile(user_id):
        """View another user's profile (for room owners to see guest profiles)"""
        user = User.query.get_or_404(user_id)
       
        return render_template('view_user_profile.html', user=user)

    @app.route('/view_room/<int:room_id>')
    @login_required
    def view_room(room_id):
        """View room details for users"""
        room = Room.query.get_or_404(room_id)
        
        if room.status != 'approved' and current_user.id != room.owner_id and current_user.role != 'admin':
            flash('This room is not available for viewing.', 'danger')
            return redirect(url_for('room_list'))
        
       
        reviews = Review.query.filter_by(room_id=room_id).order_by(Review.created_at.desc()).all()
        
        existing_bookings = Booking.query.filter(
            Booking.room_id == room_id,
            Booking.status.in_(['confirmed'])
        ).all()
        
        user_booking = None
        if current_user.role == 'viewer':
            user_booking = Booking.query.filter_by(
                room_id=room_id,
                renter_id=current_user.id
            ).order_by(Booking.created_at.desc()).first()
        
        return render_template('view_room.html', 
                            room=room, 
                            reviews=reviews, 
                            existing_bookings=existing_bookings,
                            booking=user_booking)
    
    @app.route('/about')
    def about_us():
        return render_template('about_us.html')
    
    @app.route('/term')
    def term():
        return render_template('term_services.html')
    
    @app.route('/privacy')
    def privacy_policy():
        return render_template('privacy_policy.html')
    

    @app.route('/reset_password', methods=['GET', 'POST'])
    def reset_password():
        form = ResetPasswordForm()
        
        if form.validate_on_submit():
            
            current_user.set_password(form.new_password.data)
            db.session.commit()
            
            flash('Your password has been reset successfully!', 'success')
            return redirect(url_for('profile')) 
        
        return render_template('reset_password.html', form=form)
