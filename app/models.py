from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    total_score = db.Column(db.Integer)
    total_answered = db.Column(db.Integer)
    total_time = db.Column(db.Float)

    assigned_questions = db.Column(db.Text)
    
    # Relationship to user_interactions
    interactions = db.relationship('User_Interactions', backref='user', lazy=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Questions(db.Model):
    __tablename__ = 'questions'
    id = db.Column('question_id', db.Integer, primary_key=True)
    question = db.Column(db.String(350))
    choices = db.Column(db.Text)
    answer = db.Column(db.String(100))
    explanation = db.Column(db.Text)
    topic = db.Column(db.String(100))
    difficulty = db.Column(db.Integer)
    source = db.Column(db.String(255))
    category = db.Column(db.String(64))
    
    # Relationship to user_interactions
    interactions = db.relationship('User_Interactions', backref='question', lazy=True)

    def __repr__(self):
        return '<Question: {}>'.format(self.question)
    

class User_Interactions(db.Model):
    __tablename__ = 'user_interactions'
    
    # Composite Primary Key
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.question_id'), primary_key=True)
    
    correctness = db.Column(db.Integer, nullable=False)
    #add what answers they chose
    selected_choices = db.Column(db.Text)
    individual_question_time = db.Column(db.Float, nullable=False)
    stopped_for = db.Column(db.Float, nullable=False)
    selected_category = db.Column(db.Text)
    selected_difficulty = db.Column(db.Integer)
    is_flagged = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<User_Interaction User:{} Question:{}>'.format(self.user_id, self.question_id)
    