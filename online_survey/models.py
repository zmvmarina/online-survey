
# from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
from .database import Base
##Base = declarative_base()

    
class Survey(Base):
    __tablename__ = 'survey'
    id = Column(Integer, primary_key=True)
    survey = Column(String(150))
    instruction = Column(String(250))
    questions = relationship('Question', backref='survey', lazy=True)
    active = Column(Boolean)
    def __init__(self, survey, questions=None, active=False):
        self.survey = survey
        self.active = False
    def __repr__(self):
        return f"Survey: {self.survey} {self.active}"

    def activate(self):
        self.active = True

class Question(Base):
    __tablename__ = 'question'
    
    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('survey.id'))
    question = Column(String(150))
    answers = relationship('Answer', backref='question', lazy=True)

    def __init__(self, survey_id, question, answers=None):
        self.survey_id = survey_id
        self.question = question
        if answers is not None:
            self.answers = answers

    def __repr__(self):
        return f"\tQ:{self.question}"

class Answer(Base):
    __tablename__ = 'answer'
    id = Column(Integer, primary_key=True)
    question_id = Column(
        Integer, 
        ForeignKey('question.id'))
    answer = Column(String(50))
    def __init__(self, question_id, answer):
        self.question_id = question_id
        self.answer = answer

    def __repr__(self):
        return f"> {self.answer}"

class ResponseSet(Base):
    __tablename__ = 'response_set'
    id = Column(Integer, primary_key=True)
    survey_id = Column(Integer, ForeignKey('survey.id'))
    def __init__(self, survey_id):
        self.survey_id = survey_id

class Response(Base):
    __tablename__ = 'response'
    id = Column(Integer, primary_key=True)
    response_set = Column(
        Integer,
        ForeignKey('survey.id'))
    question_id = Column(
        Integer, 
        ForeignKey('question.id'))
    answer_id = Column(
        Integer, 
        ForeignKey('answer.id'))

    def __init__(self, response_set, question_id, answer_id):
        self.response_set = response_set
        self.question_id = question_id
        self.answer_id = answer_id


