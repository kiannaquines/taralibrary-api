from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    first_name = Column(String(50))
    last_name = Column(String(50))

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, unique=True)
    year = Column(String(50))
    college = Column(String(255))
    course = Column(String(255))

    def __repr__(self):
        return f"<Profile(id={self.id}, user_id={self.user_id}, year={self.year})>"


class Zones(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(String(555))

    images = relationship("ZoneImage", back_populates="zone")

    def __repr__(self):
        return f"<Zone(id={self.id}, name={self.name})>"


class ZoneImage(Base):
    __tablename__ = "zone_images"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String(255))
    zone_id = Column(Integer, ForeignKey("zones.id"))

    zone = relationship("Zones", back_populates="images")

    def __repr__(self):
        return f"<ZoneImage(id={self.id}, zone_id={self.zone_id}, image_url={self.image_url})>"
