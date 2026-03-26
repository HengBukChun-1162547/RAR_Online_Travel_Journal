from .config import Config
import os
from werkzeug.utils import secure_filename
from flask import flash, session
from app.model import AuthorityRepository

class Utils:
    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    @staticmethod
    def upload_file(file, upload_folder, newname):
        try:
            if file and Utils.allowed_file(file.filename):
                filename = secure_filename(newname)
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                return file_path
            else:
                return False
        except Exception as e:
            flash(f"Error uploading file: {e}")
            return False
    
    @staticmethod
    def remove_file(file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            flash(f"Error removing file: {e}")
            return False
        
    @staticmethod
    def move_file(source_path, destination_path):
        """Move a file from source to destination"""
        try:
            if os.path.exists(source_path):
                # Create destination directory if it doesn't exist
                destination_dir = os.path.dirname(destination_path)
                os.makedirs(destination_dir, exist_ok=True)
                
                # Move the file
                if os.path.exists(destination_path):
                    os.remove(destination_path)
                os.rename(source_path, destination_path)
                return True
            else:
                flash("Source file does not exist")
                return False
        except Exception as e:
            flash(f"Error moving file: {e}")
            return False
        
    @staticmethod
    def rename_file(file_path, new_name):
        """Rename a file in the same directory"""
        try:
            if os.path.exists(file_path):
                # Get the directory and original extension
                directory = os.path.dirname(file_path)
                original_filename = os.path.basename(file_path)
                
                # Keep the original extension if new_name doesn't have one
                if '.' in original_filename and '.' not in new_name:
                    original_ext = original_filename.rsplit('.', 1)[1]
                    new_filename = secure_filename(f"{new_name}.{original_ext}")
                else:
                    new_filename = secure_filename(new_name)
                
                new_path = os.path.join(directory, new_filename)
                
                # Check if new filename already exists
                if os.path.exists(new_path):
                    flash("A file with the new name already exists")
                    return False
                
                # Rename the file
                os.rename(file_path, new_path)
                return new_path
            else:
                flash("File does not exist")
                return False
        except Exception as e:
            flash(f"Error renaming file: {e}")
            return False

class Pagination:
        def __init__(self, page, per_page, total_count):
            self.page = page
            self.per_page = per_page
            self.total_count = total_count
            self.pages = int((total_count - 1) / per_page) + 1

        @property
        def has_prev(self):
            return self.page > 1

        @property
        def has_next(self):
            return self.page < self.pages

        @property
        def prev_num(self):
            return self.page - 1

        @property
        def next_num(self):
            return self.page + 1

        def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
            last = 0
            for num in range(1, self.pages + 1):
                if num <= left_edge or \
                   (num > self.page - left_current - 1 and num < self.page + right_current) or \
                   num > self.pages - right_edge:
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num


"""
    A function that checks if a user has the required permission in html templates.
"""     
def register_template_utils(app):
    @app.context_processor
    def utility_processor():
        def has_permission(permission_name, user_id=None):
            if user_id is None:
                permissions = session.get('permissions', [])
            else:
                permissions = AuthorityRepository.get_user_permissions(user_id)
            if permissions is None:
                permissions = []
            return permission_name in permissions
        return dict(has_permission=has_permission)
    
    @app.template_global()
    def get_config(key):
        return app.config.get(key)