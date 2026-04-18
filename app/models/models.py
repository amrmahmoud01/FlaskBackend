from typing import List, Optional

from sqlalchemy import DECIMAL, ForeignKeyConstraint, Index, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import decimal

class Base(DeclarativeBase):
    pass


class Store(Base):
    __tablename__ = 'store'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    storeName: Mapped[str] = mapped_column(String(90))
    storeLink: Mapped[str] = mapped_column(String(2083))
    logo: Mapped[Optional[str]] = mapped_column(String(2083))

    product: Mapped[List['Product']] = relationship('Product', back_populates='store')
    


class Product(Base):
    __tablename__ = 'product'
    __table_args__ = (
        ForeignKeyConstraint(['storeId'], ['store.id'], ondelete='CASCADE', onupdate='CASCADE', name='product_ibfk_1'),
        Index('storeId', 'storeId'),
        Index("name", "name", mysql_prefix="FULLTEXT"),

    )

    productId: Mapped[int] = mapped_column(Integer, primary_key=True)
    price: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(10, 2))
    salePrice: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(10, 2))
    type: Mapped[Optional[str]] = mapped_column(String(90))
    productLink: Mapped[Optional[str]] = mapped_column(String(2083))
    name: Mapped[Optional[str]] = mapped_column(String(90))
    storeId: Mapped[Optional[int]] = mapped_column(Integer)
    gender: Mapped[Optional[str]] = mapped_column(String(90))

    store: Mapped[Optional['Store']] = relationship('Store', back_populates='product')
    productimages: Mapped[List['Productimages']] = relationship('Productimages', back_populates='product')
    color:Mapped[List['ProductColor']] = relationship('ProductColor',back_populates='product')


class Productimages(Base):
    __tablename__ = 'productimages'
    __table_args__ = (
        ForeignKeyConstraint(['productId'], ['product.productId'], name='productimages_ibfk_1'),
        Index('productId', 'productId')
    )

    imageId: Mapped[int] = mapped_column(Integer, primary_key=True)
    URL: Mapped[str] = mapped_column(String(2083))
    productId: Mapped[int] = mapped_column(
        ForeignKey("product.productId",onupdate="CASCADE", ondelete="CASCADE"))
    
    product: Mapped['Product'] = relationship('Product', back_populates='productimages')


class ProductColor(Base):
    __tablename__ = "productcolors"

    # In 2.0, mapped_column is the successor to Column
    productId: Mapped[int] = mapped_column(
        ForeignKey("product.productId", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True
    )
    color: Mapped[str] = mapped_column(String(50), primary_key=True)

    # Type-hinted relationship
    product: Mapped["Product"] = relationship('Product',back_populates="color")

    __table_args__ = (
        Index("color", "color", mysql_prefix="FULLTEXT"),
    )