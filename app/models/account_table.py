from sqlalchemy import Column, String, Float
from app.database.db import Base


class AccountTable(Base):
    __tablename__ = "accounts"

    user_id = Column(String, primary_key=True, index=True)
    balance = Column(Float, default=0.0)