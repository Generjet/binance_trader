# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from email.policy import default
from apps import db
from sqlalchemy.exc import SQLAlchemyError
from apps.exceptions.exception import InvalidUsage
import datetime as dt
from sqlalchemy.orm import relationship
from apps.config import Config
import chromadb
from chromadb.utils import embedding_functions

Currency = Config.CURRENCY
PAYMENT_TYPE = Config.PAYMENT_TYPE

class Product(db.Model):
    __tablename__ = 'products'

    id            = db.Column(db.Integer,      primary_key=True)
    user_id       = db.Column(db.Integer,      default=1)
    name          = db.Column(db.String(128),  nullable=False)
    information   = db.Column(db.String(128),  nullable=False)
    description   = db.Column(db.Text,         nullable=True)
    price         = db.Column(db.Integer,      nullable=False)
    currency      = db.Column(db.String(10),   default=Currency['usd'], nullable=False)
    date_created  = db.Column(db.DateTime,     default=dt.datetime.utcnow())
    date_modified = db.Column(db.DateTime,     default=db.func.current_timestamp(),
                             onupdate=db.func.current_timestamp())
    
    def __init__(self, **kwargs):
        super(Product, self).__init__(**kwargs)

    @classmethod
    def find_by_id(cls, _id: int) -> "Product":
        return cls.query.filter_by(id=_id).first()

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)

    def delete(self) -> None:
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    thumbnail = db.Column(db.String(200), nullable=True)
    vector = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=dt.datetime.utcnow, 
                          onupdate=dt.datetime.utcnow)
    
    author = relationship('Users', backref='blog_posts')
    
    def __init__(self, **kwargs):
        super(BlogPost, self).__init__(**kwargs)
    
    @classmethod
    def find_by_id(cls, _id: int) -> "BlogPost":
        return cls.query.filter_by(id=_id).first()
    
    def save(self) -> None:
        try:
            # First save the post to get an ID
            db.session.add(self)
            db.session.flush()  # Get the ID before commit
            
            # Initialize ChromaDB client with persistent storage
            client = chromadb.PersistentClient(path="chromadb_storage")
            collection = client.get_or_create_collection(
                name="blog_posts",
                metadata={"hnsw:space": "cosine"}
            )
            
            # Generate embedding for content
            embedding_fn = embedding_functions.DefaultEmbeddingFunction()
            embedding = embedding_fn(self.content)
            
            # Store in ChromaDB with error handling
            try:
                collection.upsert(
                    ids=[str(self.id)],
                    embeddings=[embedding],
                    metadatas=[{
                        'title': self.title,
                        'author_id': self.author_id,
                        'category': self.category,
                        'created_at': self.created_at.isoformat()
                    }]
                )
                
                # Store vector in database as JSON
                self.vector = str(embedding)
                
                # Final commit
                db.session.commit()
            except Exception as chroma_error:
                db.session.rollback()
                raise InvalidUsage(f"ChromaDB error: {str(chroma_error)}", 500)
                
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
    
    def delete(self) -> None:
        try:
            # Remove from ChromaDB
            client = chromadb.Client()
            collection = client.get_collection(name="blog_posts")
            collection.delete(ids=[str(self.id)])
            
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)

class Sale(db.Model):
    __tablename__ = 'sales'

    id            = db.Column(db.Integer,     primary_key=True)
    product       = db.Column(db.Integer,     db.ForeignKey("products.id", ondelete="cascade"), nullable=False)
    product_id    = relationship(Product,     uselist=False, backref="sales")
    state         = db.Column(db.Integer,     nullable=False)
    value         = db.Column(db.Integer,     nullable=False)
    fee           = db.Column(db.Integer,     default=0)
    currency      = db.Column(db.String(10),  default=Currency['usd'], nullable=False)
    client        = db.Column(db.String(128), nullable=True)
    payment_type  = db.Column(db.Integer(),   default=PAYMENT_TYPE['cc'], nullable=False)
    purchase_date = db.Column(db.DateTime,    default=dt.datetime.utcnow())
    creation_date = db.Column(db.DateTime,    default=dt.datetime.utcnow())
    update_date   = db.Column(db.DateTime,    default=db.func.current_timestamp(),
                             onupdate=db.func.current_timestamp())

    @classmethod
    def find_by_id(cls, _id: int) -> "Sale":
        return cls.query.filter_by(id=_id).first()

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)

    def delete(self) -> None:
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise InvalidUsage(error, 422)
