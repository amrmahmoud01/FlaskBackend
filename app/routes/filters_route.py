import os
from dotenv import load_dotenv
from flask import Blueprint, jsonify
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from services.filter_service import getCategories
from services import filter_service


filter_bp = Blueprint('filters', __name__)

@filter_bp.route("/getCats")
def getCategories():

    try:
        categories = filter_service.getCategories()
        # Format the data for the frontend
        return jsonify(categories)
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500

@filter_bp.route("/getStores")
def getStores():
    try:
        stores = filter_service.get_stores()
        return jsonify(stores)
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500