from flask import Flask, jsonify
from sqlalchemy import create_engine, select, and_,text,or_, desc, literal_column, distinct
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS
from models.models import Store, Product, Productimages, ProductColor
from sqlalchemy import func

app = Flask(__name__)
CORS(app)

engine = create_engine(
    "mysql+pymysql://avnadmin:AVNS_45tjPT5Um3BBzKuFKTB@wassup-shopping-amrsallam2001-038e.l.aivencloud.com:20553/wassup_testing",
    echo=True,
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
        search = request.args.get("search")
        # ... other args like store, category, price ...
        offset = (page - 1) * limit

        # 2. Build the Select Statement
        # Notice we select Product, then the raw URL string, then the colors string
        stmt = (
            select(
                Product, 
                func.any_value(Productimages.URL).label("img_url"), 
                func.group_concat(distinct(ProductColor.color)).label("colors")
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
        if conditions:
            total_count_stmt = total_count_stmt.where(and_(*conditions))

        total_count = session.execute(total_count_stmt).scalar()
        results = session.execute(stmt).all()

        # 5. The Result Builder (The Fix for the 'str' error)
        products = []
        for row in results:
            # row[0] = Product model, row[1] = img_url string, row[2] = colors string
            p = row[0]
            img_url = row[1]
            colors_str = row[2]

            products.append({
                "id": p.productId,
                "name": p.name,
                "price": p.price,
                "link": p.productLink,
                "image": img_url,  # Access directly, it's already a string!
                "salePrice": p.salePrice,
                "colors": colors_str.split(",") if colors_str else []
            })

        total_pages = (total_count + limit - 1) // limit
        return jsonify({
            "page": page,
            "total_count": total_count,
            "total_pages": total_pages,
            "products": products
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


@app.route("/getCats")
def getCategories():
    session = SessionLocal()
    try:
        stmt = select(Product.type).distinct()
        results = session.scalars(stmt).all()
        result = [{"category": type} for type in results]
        return jsonify(result), 200
    
    except SQLAlchemyError as e:

        session.rollback()
        print("❌ Database error:", e)
        return jsonify({"error": str(e)}), 500
    
    finally:

        session.close()


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
