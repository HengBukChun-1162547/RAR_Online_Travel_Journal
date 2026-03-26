from flask import render_template, request, redirect, url_for, flash, session, current_app
from app import Utils, flask_bcrypt
from app.user import user
import re
import os
from app.auth.view import requires_permission, has_permission
from app.model import *
from app.gamification.view import gamification_service

"""Register a new user, validate the input, and store the user in the database."""
@user.route('/register', methods=['GET', 'POST'])
def register():
    errors = {}
    
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form and 'firstname' in request.form and 'lastname' in request.form and 'location' in request.form:
        username = request.form['username'].strip().capitalize()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']  
        firstname = request.form['firstname'].strip().capitalize()
        lastname = request.form['lastname'].strip().capitalize()
        location = request.form['location'].strip()

        user_input = {'username': username, 'email': email, 'firstname': firstname, 'lastname': lastname, 'location': location}

        email_regex = current_app.config['EMAIL_REGEX']
        email_length = int(current_app.config['EMAIL_LENGTH'])
        if len(email) > email_length or not re.match(email_regex, email):
            errors['email'] = "Invalid email format or exceeds 50 characters."

        if len(password) < 8:
            errors['password'] = "Password must be at least 8 characters long."
        elif not any(char.isdigit() for char in password):
            errors['password'] = "Password must contain at least one number."
        elif not any(char.islower() for char in password):
            errors['password'] = "Password must contain at least one lowercase letter."
        elif not any(char.isupper() for char in password):
            errors['password'] = "Password must contain at least one uppercase letter."
        elif not any(char in current_app.config['PASSWORD_CHAR'] for char in password):
            errors['password'] = "Password must contain at least one special character."

    
        if password != confirm_password:
            errors['confirm'] = "Password and confirm password do not match!"
    
        password_hash = flask_bcrypt.generate_password_hash(password).decode('utf-8')

        user_exists_username = UserRepository.get_user(username=username)
        user_exists_email = UserRepository.get_user(email=email, username=username)
        if user_exists_username:
            errors['username'] = "Username already exists!"
        if user_exists_email:
            errors['email'] = "Email already exists!"
        
        if errors:
            return render_template('register.html', user_input=user_input, errors=errors)
        
        role_id = AuthorityRepository.get_role_id(current_app.config['DEFAULT_USER_ROLE'])
        user_data = {'username': username, 'email': email, 'password_hash': password_hash, 'first_name': firstname, 'last_name': lastname, 'location': location, 'role_id': role_id, 'status': current_app.config['DEFAULT_USER_STATUS']}
        result = UserRepository.add_user(user_data)
        if result > 0:
            flash('Registration successful! You can now log in.', 'success')
        
        return redirect(url_for('auth.login'))

    return render_template('register.html', errors=errors) 

""" Method renders the user profile page for the current user, if the user is not logged in,
    requests will redirect to the login page. """
@user.route('/profile')
@requires_permission('view_own_profile')
def profile():
    user_id = session['user_id']
    profile = UserRepository.get_user(user_id=user_id)
    
    if not profile:
        flash('Profile not found.', 'danger')
        return render_template('access_denied.html'), 403
    
    achievements = gamification_service.get_achievement_types()
    user_achievements = gamification_service.get_user_achievement_progress_dict(user_id)
    return render_template('profile.html', profile=profile, achievements=achievements, user_achievements=user_achievements)

@user.route('/profile/<int:selected_user_id>')
@requires_permission('view_others_public_profile')
def view_other_profile(selected_user_id):
    """ Method renders the user profile page for another user. 
    """
    page = request.args.get('page', None)
    view_mode = request.args.get('view_mode', None)
    user_id = session['user_id']
    profile = UserRepository.get_user(user_id=selected_user_id)

    is_following_user = FollowRepository.view_follow_user(user_id, selected_user_id)

    is_staff = has_permission('view_others_profile')

    # If view_mode is 'achievements', force public view even for staff
    if view_mode == 'achievements':
        is_staff = False

    if not is_staff and page == "UserManagement":
        return render_template('access_denied.html'), 403
    
    if is_staff and page == "LeaderBoard":
        is_staff = False

    if not profile:
        flash('Profile not found.', 'danger')
        return render_template('access_denied.html'), 403
    
    achievements = gamification_service.get_achievement_types()
    user_achievements = gamification_service.get_user_achievement_progress_dict(selected_user_id)
    return render_template('profile.html', profile=profile, selected_user_id=selected_user_id, is_following_user=is_following_user, achievements=achievements, user_achievements=user_achievements, is_staff=is_staff)


"""Edit Profile Method allows users to edit their profile information. When the user submits the form, 
    the data is validated and updated in the database. If there are any errors, they are displayed to the user.
"""
@user.route('/profile/edit', methods=['GET', 'POST'])
@requires_permission('edit_own_profile')
def edit_profile():
    user_id = session['user_id']
    profile_data = UserRepository.get_user(user_id=user_id)
    errors = {}
    user_input = {}
    if request.method == 'POST':
        first_name = request.form['first_name'].strip().capitalize() if 'first_name' in request.form else None
        last_name = request.form['last_name'].strip().capitalize() if 'last_name' in request.form else None
        email = request.form['email'].strip()
        location = request.form['location'].strip()
        description = request.form['description'].strip().capitalize()
        user_input = {'first_name': first_name, 'last_name': last_name, 'email': email, 'location': location, 'description': description}
        # Field Validations
        email_regex = current_app.config['EMAIL_REGEX']
        check_email = UserRepository.get_user(email=email)
        if len(email) > 50 or not re.match(email_regex, email):
            errors['email'] = "Invalid email format or exceeds 50 characters."
        elif check_email and check_email['user_id'] != user_id:
            errors['email'] = "Email is already in use."

        if first_name:
            if len(first_name) < 2 or len(first_name) > 50:
                errors['first_name'] = "First name must be between 2 and 50 characters."
        
        if last_name:
            if len(last_name) < 2 or len(last_name) > 50:
                errors['last_name'] = "Last name must be between 2 and 50 characters."
        
        if description:
            if len(description) > 300:
                errors['description'] = "Description must not exceed 300 characters."

        if not errors:
            user_data_new = {'first_name': first_name, 'last_name': last_name, 'email': email, 'location': location, 'description': description}
            result = UserRepository.update_user_data(user_id, user_data_new)
            if result > 0:
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('user.profile'))
            elif result == 0:
                flash('No changes were made to your profile.', 'info')
                return redirect(url_for('user.profile'))
            else:
                flash(f"Error updating profile!", 'danger')
    return render_template('edit.html', profile=profile_data, errors=errors, user_input=user_input)

""" Edit Profile Image Method allows users to upload a new profile image.
    The uploaded image is validated, saved to the server, and the database is updated.
"""
@user.route('/profile/edit_image', methods=['GET', 'POST'])
@requires_permission('edit_own_profile')
def edit_profile_image():
    user_id = session['user_id']
    profile_data = UserRepository.get_user(user_id=user_id)
    errors = {}
    if request.method == 'POST':
        try:
            # Check if remove image button was clicked
            if 'remove_image' in request.form:
                # If there's an existing image, delete the file
                if profile_data['profile_image']:
                    Utils.remove_file(os.path.join(current_app.static_folder, profile_data['profile_image']))
                    # Update the database
                    UserRepository.update_user(user_id, image_path="NULL")
                flash('Profile image removed successfully!', 'success')
                return redirect(url_for('user.profile'))
            
            # Handle image upload
            profile_image = request.files.get('profile_image')
            if profile_image and profile_image.filename:
                if Utils.allowed_file(profile_image.filename):
                    # Check file size
                    profile_image.seek(0, os.SEEK_END)
                    file_size = profile_image.tell()
                    profile_image.seek(0)  # Reset file pointer
                       
                    if file_size > current_app.config['MAX_FILE_SIZE']:
                        errors['profile_image'] = "File size exceeds the 5MB limit."
                        return render_template('edit_image.html', profile=profile_data, errors=errors)
                                      
                    # Delete previous image if exists
                    if profile_data['profile_image']:
                        old_file_path = os.path.join(current_app.static_folder, profile_data['profile_image'])
                        result = Utils.remove_file(old_file_path)
                    
                    # Save the file
                    newname = f"{user_id}.{profile_image.filename.rsplit('.', 1)[1].lower()}"
                    upload_folder = os.path.join(current_app.static_folder, current_app.config['UPLOAD_FOLDER_PROFILE'])
                    result = Utils.upload_file(profile_image, upload_folder, newname)
                    if result == False:
                        errors['profile_image'] = "Error uploading file."
                        return render_template('edit_image.html', profile=profile_data, errors=errors)
                        
                    
                    # Update database
                    image_path=f"{current_app.config['UPLOAD_FOLDER_PROFILE']}/{newname}"
                    if image_path != profile_data['profile_image']:
                        result = UserRepository.update_user(user_id, image_path=image_path)
                    if result:
                        flash('Profile image updated successfully!', 'success')
                    else:
                        errors['profile_image'] = "Error updating profile image in database."
                        return render_template('edit_image.html', profile=profile_data, errors=errors)
                    return redirect(url_for('user.profile'))
                else:
                    # Build list of allowed extensions for error message
                    allowed_ext_list = ', '.join(current_app.config['ALLOWED_EXTENSIONS']).upper()
                    errors['profile_image'] = f"Invalid file type. Supported formats: {allowed_ext_list}"
            elif request.method == 'POST' and (not profile_image or not profile_image.filename):
                errors['profile_image'] = "Please select an image file to upload."
        
        except Exception as e:
            errors['profile_image'] = f"Error updating profile image: {e}"
    
    return render_template('edit_image.html', profile=profile_data, errors=errors)

""" Change Password Method allows users to change their password,
    the data is validated and updated in the database. If there are any errors, they are displayed to the user. 
"""
@user.route('/profile/change_password', methods=['GET', 'POST'])
@requires_permission('change_own_password')
def change_password():
    user_id = session['user_id']
    errors = {}

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Password Validations
        user = UserRepository.get_user(user_id=user_id)
        if user:
            stored_password_hash = user['password_hash']

            # Validate Current Password
            if not current_password:
                errors['current_password_invalid'] = "Current password is required."
            elif not flask_bcrypt.check_password_hash(stored_password_hash, current_password):
                errors['current_password_invalid'] = "Password doesn't match."

            # Validate New Password
            if not new_password:
                errors['password_invalid'] = "New password is required."
            elif len(new_password) < 8:
                errors['password_invalid'] = "Password must be at least 8 characters long."
            elif new_password == current_password:
                errors['password_invalid'] = "New password cannot be the same as the current password."
            elif not any(char.isdigit() for char in new_password):
                errors['password_invalid'] = "Password must contain at least one number."
            elif not any(char.islower() for char in new_password):
                errors['password_invalid'] = "Password must contain at least one lowercase letter."
            elif not any(char.isupper() for char in new_password):
                errors['password_invalid'] = "Password must contain at least one uppercase letter."
            elif not any(char in "!@#$%^&*()_+[]{}|;:,.<>?/~" for char in new_password):
                errors['password_invalid'] = "Password must contain at least one special character."

            # Validate Confirm Password
            if new_password != confirm_password:
                errors['confirm_password_invalid'] = "Password and confirm password do not match."
        else:
            errors['general_error'] = "User not found."

        if not errors:
            try:
                hashed_password = flask_bcrypt.generate_password_hash(new_password).decode('utf-8')
                UserRepository.update_user(user_id, password_hash=hashed_password)
                # Update password successfully, so logout the user
                session.clear()
                flash('Password changed successfully! Please login again.', 'success')
                return redirect(url_for('auth.login'))

            except Exception as e:
                errors['general_error'] = f"Error changing password: {e}"

        return render_template('change_password.html', errors=errors)
    
    return render_template('change_password.html', errors=errors)