from sqlalchemy import false
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base

DB_URL = "postgresql+psycopg2://admin:secretpassword@localhost:5433/tickets_db"

engine= create_engine(DB_URL)
Base = declarative_base()
Session_local = sessionmaker(autocommit = False , autoflush=False , bind=engine)
