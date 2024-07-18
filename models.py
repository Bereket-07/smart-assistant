from flask_sqlalchemy import SQLAlchemy

# initializes a SQLAlchemy object
db = SQLAlchemy()

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.BigInteger, primary_key=True)
    question_text = db.Column(db.Text)
    questionarie_id = db.Column(db.BigInteger, db.ForeignKey('questionares.id'))
    questionare = db.relationship('Questionares' , back_populates='questions')
    choices = db.relationship('Choices', backref='questions', lazy=True)
    answers = db.relationship('Answers', backref='questions', lazy=True)

class Questionares(db.Model):
    __tablename__ = 'questionares'
    id = db.Column(db.BigInteger , primary_key=True)
    title = db.Column(db.String(255))
    description=db.Column(db.String(255))
    topic = db.Column(db.String(255))
    total_audience = db.Column(db.BigInteger)
    questions = db.relationship('Question', back_populates='questionare')

class Choices(db.Model):
    __tablename__='choices'
    id=db.Column(db.BigInteger,primary_key=True)
    question_id = db.Column(db.BigInteger,db.ForeignKey('questions.id')) 
    choice_text = db.Column(db.String(255))
    
class Answers(db.Model):
    __tablename__='answers'
    id = db.Column(db.BigInteger , primary_key=True)
    answer = db.Column(db.String(255))
    question_id = db.Column(db.BigInteger , db.ForeignKey('questions.id'))
    user_id = db.Column(db.BigInteger , db.ForeignKey('users.id'))
    user = db.relationship('Users', backref='answers', lazy=True)

class Users(db.Model):
    __tablename__='users'
    id = db.Column(db.BigInteger , primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))        