from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    marks = db.Column(db.Integer, index=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(350))
    choices = db.Column(db.Text)  # Stores JSON string of choices
    answer = db.Column(db.String(100))  # Can store single "A" or multiple "ABE"
    explanation = db.Column(db.Text)
    topic = db.Column(db.String(100))
    difficulty = db.Column(db.Integer)
    source = db.Column(db.String(255))

    category = db.Column(db.String(64))

    def __repr__(self):
        return '<Question: {}>'.format(self.question)