from flask import Flask, jsonify
from sqlalchemy import create_engine, select, and_,text,or_, desc, literal_column, distinct
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS
from models.models import Store, Product, Productimages, ProductColor
from sqlalchemy import func
from dotenv import load_dotenv
from .database_service import startSession
import os



load_dotenv()


def getCategories():

    session = startSession()
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

def get_stores():
    session = startSession()
    try:
        stmt = select(Store)
        results = session.scalars(stmt).all()
        result = [{"name": s.storeName} for s in results]
        return result
    except SQLAlchemyError as e:
        session.rollback()
        print("❌ Database error:", e)
        return e
    finally:
        session.close()

def getGenders():
    session = startSession()
    try:
        stmt = select(Product.gender).distinct()
        results = session.scalars(stmt).all()
        result = [{"gender": gender}for gender in results]
        return result
    
    except SQLAlchemyError as e:
        session.rollback()
        print("❌ Database error:", e)
        return e
