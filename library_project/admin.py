from flask_admin import Admin
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView
from library_project import app, db
from library_project.database import User, Bibliography

class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.email == 'o.valioniene@gmail.com'

admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(ModelView(Bibliography, db.session))