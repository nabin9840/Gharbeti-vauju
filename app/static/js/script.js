
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

const registrationForm = document.querySelector('form[action*="register"]');
if (registrationForm) {
    registrationForm.addEventListener('submit', function(e) {
        const password = document.querySelector('input[name="password"]').value;
        const confirmPassword = document.querySelector('input[name="confirm_password"]').value;

        if (password.length < 6) {
            e.preventDefault();
            alert('Password must be at least 6 characters long');
            return false;
        }

        if (password !== confirmPassword) {
            e.preventDefault();
            alert('Passwords do not match');
            return false;
        }
    });
}

const roomForm = document.querySelector('.room-form');
if (roomForm) {
    roomForm.addEventListener('submit', function(e) {
        const title = document.querySelector('input[name="title"]').value;
        const location = document.querySelector('input[name="location"]').value;
        const price = document.querySelector('input[name="rent_price"]').value;
        const availableFrom = document.querySelector('input[name="available_from"]').value;

        if (!title || !location || !price || !availableFrom) {
            e.preventDefault();
            alert('Please fill in all required fields');
            return false;
        }

        if (parseFloat(price) <= 0) {
            e.preventDefault();
            alert('Rent price must be greater than 0');
            return false;
        }
    });
}


const bookingForm = document.querySelector('.booking-form-section form');
if (bookingForm) {
    bookingForm.addEventListener('submit', function(e) {
        const startDate = new Date(document.querySelector('input[name="start_date"]').value);
        const endDate = new Date(document.querySelector('input[name="end_date"]').value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (startDate < today) {
            e.preventDefault();
            alert('Start date cannot be in the past');
            return false;
        }

        if (endDate <= startDate) {
            e.preventDefault();
            alert('End date must be after start date');
            return false;
        }
    });
}


const reviewForm = document.querySelector('.review-form');
if (reviewForm) {
    reviewForm.addEventListener('submit', function(e) {
        const rating = document.querySelector('input[name="rating"]').value;

        if (rating < 1 || rating > 5) {
            e.preventDefault();
            alert('Rating must be between 1 and 5');
            return false;
        }
    });
}


const deleteLinks = document.querySelectorAll('a[href*="delete"]');
deleteLinks.forEach(link => {
    if (!link.hasAttribute('onclick')) {
        link.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
                return false;
            }
        });
    }
});


const cancelLinks = document.querySelectorAll('a[href*="cancel"]');
cancelLinks.forEach(link => {
    if (!link.hasAttribute('onclick')) {
        link.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to cancel this booking?')) {
                e.preventDefault();
                return false;
            }
        });
    }
});


const filterForm = document.querySelector('.filter-form');
if (filterForm) {
    const locationInput = filterForm.querySelector('input[name="location"]');
    const roomTypeSelect = filterForm.querySelector('select[name="room_type"]');

    
    if (roomTypeSelect) {
        roomTypeSelect.addEventListener('change', function() {
            filterForm.submit();
        });
    }
}


const imageInput = document.querySelector('input[name="image"]');
if (imageInput) {
    imageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif'];
            if (!allowedTypes.includes(file.type)) {
                alert('Please upload a valid image file (PNG, JPG, or GIF)');
                this.value = '';
                return;
            }

            const maxSize = 16 * 1024 * 1024;
            if (file.size > maxSize) {
                alert('File size must be less than 16MB');
                this.value = '';
                return;
            }
        }
    });
}

const forms = document.querySelectorAll('form');
forms.forEach(form => {
    form.addEventListener('submit', function() {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing...';
        }
    });
});

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});
