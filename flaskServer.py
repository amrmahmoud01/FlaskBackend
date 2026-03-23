from flask import Flask, jsonify
from sqlalchemy import create_engine, select, and_,text,or_, desc, literal_column
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
        # Pagination params
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 21))
        store = request.args.getlist("store")
        priceMin = request.args.get("priceMin")
        priceMax=   request.args.get("priceMax")
        category = request.args.getlist("category")
        search = request.args.get("search")
        onSale = request.args.get("onSale", False)
        offset = (page - 1) * limit

        # Get total number of products
        total_stmt = select(func.count(Product.productId))
        total_count = session.execute(total_stmt).scalar()


        # Query products with images

        conditions = []
        stmt = (
                select(Product, Productimages, ProductColor)
                .join(Productimages, Product.productId == Productimages.productId)
                .join(Store, Store.id == Product.storeId)
                .outerjoin(ProductColor, ProductColor.productId == Product.productId)
                .offset(offset)
                .limit(limit)
            )
        
        params = {}

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
            search_words = search.split()
            escaped_search = search.replace("'", "''")  


            params["search"] = search

            raw_words = search.split()
            search_words = [word.replace("'", "''") for word in raw_words]


            for word in search_words:
                conditions.append(
                    text(f"(MATCH(product.name) AGAINST('{escaped_search}' IN BOOLEAN MODE) "
                    f"OR MATCH(productcolors.color) AGAINST('{escaped_search}' IN BOOLEAN MODE))")
                    )
            relevance_sql = (
                f"MATCH(product.name) AGAINST('{escaped_search}') + "
                f"MATCH(productcolors.color) AGAINST('{escaped_search}')"
            )
            stmt = stmt.add_columns(literal_column(relevance_sql).label("relevance"))
            stmt = stmt.order_by(desc(literal_column("relevance")))
        

        total_count_stmt = select(func.count(Product.productId)).join(Store, Store.id == Product.storeId).outerjoin(ProductColor,ProductColor.productId==Product.productId)
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
            total_count_stmt = total_count_stmt.where(and_(*conditions))
            total_count = session.execute(total_count_stmt, params).scalar()


        
        results = session.execute(stmt,params).all()

        # Build result list
        products = [
            {
                "id": p.productId,
                "name": p.name,
                "price": p.price,
                "link": p.productLink,
                "image": img.URL,
                "salePrice": p.salePrice,
                "color": pc.color if pc else None
            }
            for p, img, pc, *rest in results
        ]

        total_pages = (total_count + limit - 1) // limit  # ceil division
        has_next = page < total_pages

        return jsonify({
            "page": page,
            "limit": limit,
            "count": len(products),
            "total_count": total_count,
            "total_pages": total_pages,
            "hasNext": has_next,
            "products": products
        }), 200

    except SQLAlchemyError as e:
        session.rollback()
        print("❌ Database error:", e)
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
