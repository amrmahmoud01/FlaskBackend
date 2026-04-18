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
        categories = filter_service.getCategories()
        # Format the data for the frontend
        return jsonify(categories)
    except SQLAlchemyError as e:
        session.rollback()
        # Keep the log for you, return a clean message for the user
        print(f"❌ Database error: {e}")
        return jsonify({"error": str(e)}), 500
    
    finally:
        session.close()