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

    load_dotenv()





    try:
        categories = filter_service.getCategories()
        # Format the data for the frontend
        return jsonify(categories)
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500
