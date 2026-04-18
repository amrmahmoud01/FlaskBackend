from flask import Flask, jsonify
from sqlalchemy import create_engine, select, and_,text,or_, desc, literal_column, distinct
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS
from models.models import Store, Product, Productimages, ProductColor
from sqlalchemy import func
from dotenv import load_dotenv
import os



load_dotenv()


def getCategories():

    #TODO Modularize DB engine creation

    engine = create_engine(
                f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@"
                f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
                echo=False,
                pool_pre_ping=True,
                pool_recycle=280,
    )


    SessionLocal = sessionmaker(bind=engine)

    session = SessionLocal()


    
    try:
        stmt = select(Product.type).distinct()
        results = session.scalars(stmt).all()
        result = [{"category": type} for type in results]
        return result
    
    except SQLAlchemyError as e:

        session.rollback()
        print("❌ Database error:", e)
        return e
    
    finally:

        session.close()
