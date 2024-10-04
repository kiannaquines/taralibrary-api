from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    first_name = Column(String(50))
    last_name = Column(String(50))
    register_date = Column(
        DateTime(timezone=True),
        index=True,
        server_default=func.current_timestamp(),
    )
    update_date = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.now(),
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), index=True)
    date_added = Column(
        DateTime(timezone=True),
        index=True,
        server_default=func.current_timestamp(),
    )

    def __repr__(self):
        return f"<Like(id={self.id}, user_id={self.user_id}, zone_id={self.zone_id}, date_added={self.date_added})>"


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, unique=True)
    year = Column(String(50))
    college = Column(String(255))
    course = Column(String(255))
    date_added = Column(
        DateTime(timezone=True),
        index=True,
        server_default=func.current_timestamp(),
    )
    update_date = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.now(),
    )

    def __repr__(self):
        return f"<Profile(id={self.id}, user_id={self.user_id}, year={self.year})>"


zone_category_association = Table(
    "zone_category",
    Base.metadata,
    Column("zone_id", Integer, ForeignKey("zones.id")),
    Column("category_id", Integer, ForeignKey("categories.id")),
)

class Zones(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255))
    description = Column(String(555))

    images = relationship("ZoneImage", back_populates="zone")
    date_added = Column(DateTime(timezone=True), index=True, default=func.now())
    update_date = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.now(),
    )

    categories = relationship("Category", secondary=zone_category_association, back_populates="zones")

    def __repr__(self):
        return f"<Zone(id={self.id}, name={self.name})>"


class ZoneImage(Base):
    __tablename__ = "zone_images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_url = Column(String(255))
    zone_id = Column(Integer, ForeignKey("zones.id"))

    zone = relationship("Zones", back_populates="images")

    def __repr__(self):
        return f"<ZoneImage(id={self.id}, zone_id={self.zone_id}, image_url={self.image_url})>"


class Comment(Base):

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), index=True)
    comment = Column(String(555))
    date_added = Column(
        DateTime(timezone=True),
        index=True,
        server_default=func.current_timestamp(),
    )
    update_date = Column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.now(),
    )


    def __repr__(self):
        return f"<Comment(id={self.id}, user_id={self.user_id}, zone_id={self.zone_id}, comment={self.comment}, date_added={self.date_added})>"
    

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(255), index=True)
    date_added = Column(DateTime(timezone=True), index=True, server_default=func.current_timestamp())
    update_date = Column(DateTime(timezone=True), server_default=func.current_timestamp(), onupdate=func.now())

    zones = relationship("Zones", secondary=zone_category_association, back_populates="categories")

    def __repr__(self):
        return f"<Category(id={self.id}, category={self.category})>"

