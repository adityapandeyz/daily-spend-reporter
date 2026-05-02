from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This is a placeholder - we will eventually 
# pull this from our AWS SSM logic!
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# 1. Create the Engine
# 'check_same_thread' is only needed for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 2. Create a Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. The Base class for our models
Base = declarative_base()