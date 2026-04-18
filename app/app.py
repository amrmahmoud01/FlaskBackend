from flask import Flask, jsonify
from sqlalchemy import create_engine, select, and_,text,or_, desc, literal_column, distinct
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS
from models.models import Store, Product, Productimages, ProductColor
from sqlalchemy import func
from dotenv import load_dotenv
from routes import filters_route # Import your Blueprint
from routes.filters_route import filter_bp
from routes.product_route import product_bp
from services.database_service import startSession
from flask import request

from flask import request
from sqlalchemy import func
import os

app = Flask(__name__)
CORS(app)


load_dotenv()

@app.route("/")
def index():
    """Initial Tester API"""
    return jsonify({"message": "Drink"})

app.register_blueprint(filter_bp)
app.register_blueprint(product_bp)




if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000, threaded=True)
