from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, DateTime, ForeignKey, Numeric, Boolean, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

from src.config import engine

Base = declarative_base()


class AllVacancies(Base):
    __tablename__ = 'all_vacancies'
    id = Column(Integer, primary_key=True)
    account_division = Column(Integer, comment="Region ID")
    account_region = Column(Integer, comment="Region ID")
    position = Column(String(100), nullable=False, comment="The name of the vacancy (occupation)")
    company = Column(String(100), comment="Department (ignored if the DEPARTMENTS are enabled)")
    money = Column(String(100), comment="Salary")
    priority = Column(Integer, comment="The priority of a vacancy (0 for usual or 1 for high")
    hidden = Column(Boolean, comment="Is the vacancy hidden from the colleagues?")
    state = Column(String(50), comment="The state of a vacancy")
    created = Column(DateTime(), comment="Date and time of creating a vacancy")
    additional_fields_list = Column(ARRAY(String(50)), comment="List of additional field names")
    multiple = Column(Boolean, comment="Flag indicating if this vacancy is a multiple")
    parent = Column(Boolean, comment="Flag indicating if this vacancy is a multiple")
    account_vacancy_status_group = Column(Integer, comment="Recruitment status group ID")
    flg_close_recruiter = Column(Boolean, comment="True if the vacancy was filled by a recruit")
    coworkers_id = Column(Integer, ForeignKey("coworkers.id"), comment="id reason")
    date_closed = Column(DateTime(), comment="date closed vacancy")


class Coworkers(Base):
    __tablename__ = 'coworkers'
    id = Column(Integer, primary_key=True)
    # TODO: запрос get a coworker не ищет по id из get all coworkes
    # member = Column(Integer, comment="User ID", nullable=False)
    name = Column(String(100), comment="Coworker name")
    type = Column(String(100), comment="Coworker type (role)")


class StatusReasons(Base):
    __tablename__ = 'status_reasons'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), comment="Reason name")


class ApplicantsStatus(Base):
    __tablename__ = 'applicants_status'
    id = Column(String, primary_key=True)
    name = Column(String, comment='name of status')


class VacStatInfo(Base):
    __tablename__ = 'vacancy_stat_info'
    id = Column(Integer, primary_key=True)
    vac_id = Column(Integer, comment='Vacancy id', nullable=False)
    # all_vac = relationship('all_vacancies', backref='vacancy_stat_info', uselist=False)
    status_id = Column(String, nullable=False, comment='Applicant status id')
    # applicant_status = relationship('applicants_status', backref='vacancy_stat_info', uselist=False)
    value = Column(Integer, comment='value of applicants by status')
    date = Column(DateTime(), default=datetime.now(), comment='Date when registrate status')


class NewVacancies(Base):
    __tablename__ = 'new_vacancies'
    __table_args__ = {"schema": "tmp_data"}
    id = Column(Integer, primary_key=True)
    account_division = Column(Integer, comment="Region ID")
    account_region = Column(Integer, comment="Region ID")
    position = Column(String(100), nullable=False, comment="The name of the vacancy (occupation)")
    company = Column(String(100), comment="Department (ignored if the DEPARTMENTS are enabled)")
    money = Column(String(100), comment="Salary")
    priority = Column(Integer, comment="The priority of a vacancy (0 for usual or 1 for high")
    hidden = Column(Boolean, comment="Is the vacancy hidden from the colleagues?")
    state = Column(String(50), comment="The state of a vacancy")
    created = Column(DateTime(), comment="Date and time of creating a vacancy")
    additional_fields_list = Column(ARRAY(String(50)), comment="List of additional field names")
    multiple = Column(Boolean, comment="Flag indicating if this vacancy is a multiple")
    parent = Column(Boolean, comment="Flag indicating if this vacancy is a multiple")
    account_vacancy_status_group = Column(Integer, comment="Recruitment status group ID")


Base.metadata.create_all(engine)
