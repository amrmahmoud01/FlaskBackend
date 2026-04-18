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
import os

app = Flask(__name__)
CORS(app)


load_dotenv()


engine = create_engine(
            f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@"
            f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
            echo=False,
            pool_pre_ping=True,
            pool_recycle=280,
)


SessionLocal = sessionmaker(bind=engine)

@app.route("/")
def index():
    return jsonify({"message": "Drink"})

from flask import request

from flask import request
from sqlalchemy import func

@app.route("/getAllProducts", methods=["GET"])
def get_all_products():
    session = SessionLocal()
    try:
        # 1. Params and Pagination
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 21))
        store = request.args.getlist("store")
        priceMin = request.args.get("priceMin")
        priceMax=   request.args.get("priceMax")
        category = request.args.getlist("category")
        search = request.args.get("search")
        onSale = request.args.get("onSale", False)
        offset = (page - 1) * limit

        # 2. Build the Select Statement
        # Notice we select Product, then the raw URL string, then the colors string
        stmt = (
            select(
                Product, 
                func.any_value(Productimages.URL).label("img_url"), 
                func.group_concat(distinct(ProductColor.color)).label("colors"),
                Store
            )
            .join(Productimages, Product.productId == Productimages.productId)
            .join(Store, Store.id == Product.storeId)
            .outerjoin(ProductColor, ProductColor.productId == Product.productId)
            .group_by(Product.productId)
            .offset(offset)
            .limit(limit)
        )
        
        conditions = []
        params = {}

        # 3. Apply Search Logic (Matching your exact SQL intent)
        if store:
            conditions.append(Store.storeName.in_(store))
        
        if category:
            conditions.append(Product.type.in_(category))
        
        if priceMin:
            conditions.append(Product.price>=priceMin)

        if priceMax:
            conditions.append(Product.price<=priceMax)

        if onSale:
            conditions.append(Product.salePrice>0)

        if search:
            escaped_search = search.replace("'", "''")
            search_words = search.split()

            # WHERE: Multiple Boolean Matches
            for word in search_words:
                conditions.append(
                    text(f"(MATCH(product.name) AGAINST('{word}' IN BOOLEAN MODE) "
                         f"OR MATCH(productcolors.color) AGAINST('{word}' IN BOOLEAN MODE))")
                )

            # RELEVANCE: Calculated Ranking
            # We use MAX() on the color match to satisfy ONLY_FULL_GROUP_BY
            relevance_sql = literal_column(
                f"MATCH(product.name) AGAINST('{escaped_search}') + "
                f"MAX(MATCH(productcolors.color) AGAINST('{escaped_search}'))"
            )
            
            stmt = stmt.add_columns(relevance_sql.label("relevance"))
            stmt = stmt.order_by(desc(literal_column("relevance")))

        # 4. Filter and Count
        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Re-use conditions for total count
        total_count_stmt = (
            select(func.count(distinct(Product.productId)))
            .select_from(Product)
            .join(Store, Store.id == Product.storeId)
            .outerjoin(ProductColor, ProductColor.productId == Product.productId)
        )
        total_count_stmt = total_count_stmt.where(and_(*conditions))

        

        total_count = session.execute(total_count_stmt).scalar()
        results = session.execute(stmt).mappings().all()

        # 5. The Result Builder (The Fix for the 'str' error)
        products = []
        for row in results:
            # row[0] = Product model, row[1] = img_url string, row[2] = colors string
            p = row['Product']
            img_url = row['img_url']
            colors_str = row['colors']
            store = row['Store']

            products.append({
                "id": p.productId,
                "name": p.name,
                "store":store.storeName,
                "price": p.price,
                "link": p.productLink,
                "image": img_url,  # Access directly, it's already a string!
                "salePrice": p.salePrice,
                "colors": colors_str.split(",") if colors_str else []
            })
            

        total_pages = (total_count + limit - 1) // limit

        hasNext = page < total_pages

        return jsonify({
            "page": page,
            "total_count": total_count,
            "total_pages": total_pages,
            "products": products,
            "hasNext":hasNext,
        }), 200

    except Exception as e:
        session.rollback()
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()

@app.route("/getStores")
def get_stores():
    session = SessionLocal()
    try:
        stmt = select(Store)
        results = session.scalars(stmt).all()
        result = [{"name": s.storeName} for s in results]
        return jsonify(result), 200
    except SQLAlchemyError as e:
        session.rollback()
        print("❌ Database error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()


# @app.route("/getCats")
# def getCategories():
#     session = SessionLocal()
#     try:
#         stmt = select(Product.type).distinct()
#         results = session.scalars(stmt).all()
#         result = [{"category": type} for type in results]
#         return jsonify(result), 200
    
#     except SQLAlchemyError as e:

#         session.rollback()
#         print("❌ Database error:", e)
#         return jsonify({"error": str(e)}), 500
    
#     finally:

#         session.close()

app.register_blueprint(filter_bp)


@app.route("/getGenders")
def getGenders():
    
    session=SessionLocal()

    try:
        stmt = select(Product.gender).distinct()
        results = session.scalars(stmt).all()
        result = [{"gender": gender}for gender in results]
        return jsonify(result),200
    
    except SQLAlchemyError as e:
        session.rollback()
        print("❌ Database error:", e)
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000, threaded=False)
