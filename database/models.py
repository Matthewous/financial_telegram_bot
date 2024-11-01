from sqlalchemy import Column, Integer, String, Float, ForeignKey, BigInteger, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Промежуточная таблица для связи "многие ко многим" между User и Portfolio
user_portfolio = Table(
    'user_portfolio', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('portfolio_id', Integer, ForeignKey('portfolios.id'), primary_key=True)
)

# Таблица пользователей
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)

    portfolios = relationship("Portfolio", secondary=user_portfolio, back_populates="users")


# Таблица портфелей
class Portfolio(Base):
    __tablename__ = 'portfolios'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)

    users = relationship("User", secondary=user_portfolio, back_populates="portfolios")
    stocks = relationship("Portfolio_Stocks", back_populates="portfolio")


# Таблица для тикеров
class Stock(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False, unique=True)
    
    portfolios = relationship("Portfolio_Stocks", back_populates="stock")


# Таблица связи портфелей и акций с указанием долей
class Portfolio_Stocks(Base):
    __tablename__ = 'portfolio_stocks'
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'))
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    share = Column(Float)

    portfolio = relationship("Portfolio", back_populates="stocks")
    stock = relationship("Stock", back_populates="portfolios")
