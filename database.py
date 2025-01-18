from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc

# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Automatically create all tables
try:
    Base.metadata.create_all(bind=engine)
except exc.SQLAlchemyError as e:
    print(f"Error creating tables: {e}")
