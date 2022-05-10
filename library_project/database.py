from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from library_project import app, db


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column('name', db.String(50), unique=True, nullable=False)
    email = db.Column('email', db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(50), nullable=False, default='default.jpg')
    password = db.Column('password', db.String(50), unique=True, nullable=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


class Bibliography(db.Model):
    __tablename__ = 'library_project'
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(250))
    title = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
