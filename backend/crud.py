# backend/crud.py
from sqlalchemy.orm import Session
from passlib.context import CryptContext

import models
import schemas
import security

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_account_by_username(db: Session, username: str):
    return db.query(models.Account).filter(models.Account.username == username).first()

def get_accounts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Account).offset(skip).limit(limit).all()

def create_account(db: Session, account: schemas.AccountCreate):
    encrypted_password = security.encrypt_password(account.password)
    db_account = models.Account(
        username=account.username,
        encrypted_password=encrypted_password
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

# THIS IS THE MISSING FUNCTION
def delete_account(db: Session, account_id: int):
    db_account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if db_account:
        db.delete(db_account)
        db.commit()
        return db_account
    return None

# Add these functions to the end of backend/crud.py

def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Post).offset(skip).limit(limit).all()

def create_post(db: Session, post: schemas.PostCreate):
    db_post = models.Post(content=post.content, scheduled_at=post.scheduled_at)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post