from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Time, Date, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class Company(Base):
    __tablename__ = 'companies'

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(100), nullable=False)
    document_id = mapped_column(String(100), nullable=False)
    busy = relationship('Busy')


class Busy(Base):
    __tablename__ = 'busies'

    id = mapped_column(Integer, primary_key=True)
    start_time = mapped_column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    day_id = Column(Integer, ForeignKey('days.id'))
    day = relationship('Day')
    company_id = Column(Integer, ForeignKey('companies.id'))
    company = relationship('Company')


class Day(Base):
    __tablename__ = 'days'

    id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    vocation = Column(Boolean, nullable=False)
    busy = relationship('Busy')


db.metadata.create_all()
