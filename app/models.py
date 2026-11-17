from sqlalchemy import Column, Integer , Float , Boolean , DateTime , String
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer , primary_key=True , index = True)
    is_vip = Column(Boolean ,default=False)
    blacklisted = Column(Boolean,default = False)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key = True , index = True)
    user_id = Column(Integer, index=True)
    item_name = Column(String)
    price = Column(Float)
    status = Column(String, default = "Pending")

