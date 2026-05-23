from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    is_premium = Column(Boolean, default=False)

class SystemSettings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True, default=1)
    premium_price = Column(Float, default=49.0)
    payment_address = Column(String, default="0xYourWalletAddress")

class StyleSample(Base):
    __tablename__ = 'style_samples'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    category = Column(String, default="tweet")
    timestamp = Column(DateTime, default=datetime.utcnow)

engine = create_engine('sqlite:///bot.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
