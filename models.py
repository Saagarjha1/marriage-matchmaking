from sqlalchemy import Column, Integer, String, JSON
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer, nullable=True)  # Optional field
    gender = Column(String, nullable=True)  # Optional field
    email = Column(String, unique=True, index=True)
    city = Column(String, index=True, nullable=True)  # Optional field
    interests = Column(JSON, nullable=True)  # Optional field
    password = Column(String)  # This should store the hashed password

    def __repr__(self):
        return f"<User(name={self.name}, email={self.email}, city={self.city})>"
