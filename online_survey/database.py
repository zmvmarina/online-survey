from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'surveys.db')

engine = create_engine(f'sqlite:////{DB_PATH}', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from .models import Question, Answer, Survey
    Base.metadata.create_all(bind=engine)
