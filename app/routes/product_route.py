from flask import Blueprint, Flask, jsonify
from sqlalchemy import create_engine, select, and_,text,or_, desc, literal_column, distinct
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS
from models.models import Store, Product, Productimages, ProductColor
from sqlalchemy import func
from dotenv import load_dotenv
from routes import filters_route # Import your Blueprint
from routes.filters_route import filter_bp
from services.database_service import startSession
from flask import request
from services.product_service import getAllProducts
from services import product_service
from flask import request
from sqlalchemy import func
import os

product_bp = Blueprint('products', __name__)

@filter_bp.route("/getAllProducts")
def getAllProducts():
    try:
        products = product_service.getAllProducts()
        # Format the data for the frontend
        return jsonify(products), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500