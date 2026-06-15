from sqlalchemy import Column, String, Float, DateTime
from datetime import datetime
from app.database.db import Base


class TransactionTable(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    sender_id = Column(String)
    receiver_id = Column(String)
    amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)