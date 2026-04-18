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
from flask import request



def getAllProducts():
    
    session = startSession()
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

        return {
            "page": page,
            "total_count": total_count,
            "total_pages": total_pages,
            "products": products,
            "hasNext":hasNext,
        }, 200

    except Exception as e:
        session.rollback()
        print("❌ Error:", e)
        return e
    finally:
        session.close()
