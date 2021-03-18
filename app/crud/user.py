from sqlalchemy.orm import Session

from app.db import models
from app.models import user
from app.utils.security import generate_salt, get_password_hash


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_name(db: Session, name: str):
    return db.query(models.User).filter(models.User.name == name).first()


def get_users(db: Session, skip: int = 0, limit: int = 20):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user_count(db: Session):
    return db.query(models.User).count()


def create_user(db: Session, user_item: user.UserCreate):
    salt = generate_salt()
    hashed_password = get_password_hash(salt + user_item.password)
    db_user = models.User(name=user_item.name, hashed_password=hashed_password, salt=salt, is_admin=user_item.is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, password: str):
    db_user = get_user(db, user_id=user_id)
    salt = generate_salt()
    db_user.salt = salt
    db_user.hashed_password = get_password_hash(salt + password)
    db.commit()
    db.refresh(db_user)
    return db_user
