from flask import Flask, jsonify
from sqlalchemy import create_engine, select, and_,text,or_, desc, literal_column, distinct
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS
from models.models import Store, Product, Productimages, ProductColor
from sqlalchemy import func
from dotenv import load_dotenv
import os
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

load_dotenv()

engine = create_engine(
                f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@"
                f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
                echo=False,
                pool_pre_ping=True,
                pool_recycle=280,
    )

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def startSession():
    return Session()
