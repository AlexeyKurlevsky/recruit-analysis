from datetime import datetime

from sqlalchemy import ARRAY, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base

from src.config import engine


Base = declarative_base()


class Coworkers(Base):
    __tablename__ = "coworkers"
    id = Column(Integer, primary_key=True)
    # TODO: запрос get a coworker не ищет по id из get all coworkes
    # member = Column(Integer, comment="User ID", nullable=False)
    name = Column(String(100), comment="Coworker name")
    type = Column(String(100), comment="Coworker type (role)")


class AllVacancies(Base):
    __tablename__ = "all_vacancies"
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
    date_last_log = Column(DateTime(), comment="date last log")


class ApplicantsStatus(Base):
    __tablename__ = "applicants_status"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, comment="name of status")


class VacStatInfo(Base):
    __tablename__ = "vacancy_stat_info"
    id = Column(Integer, primary_key=True)
    vac_id = Column(Integer, ForeignKey("all_vacancies.id"), comment="Vacancy id", nullable=False)
    status_id = Column(
        Integer,
        ForeignKey("applicants_status.id"),
        nullable=False,
        comment="Applicant status id",
    )
    value = Column(Integer, comment="value of applicants by status")
    date = Column(DateTime(), default=datetime.now().date(), comment="Date when registrate status")


class CurrentApplicantValueByStatus(Base):
    __tablename__ = "current_applicant_value_by_status"
    id = Column(Integer, primary_key=True)
    vac_id = Column(Integer, ForeignKey("all_vacancies.id"), comment="Vacancy id", nullable=False)
    status_id = Column(
        Integer,
        ForeignKey("applicants_status.id"),
        nullable=False,
        comment="Applicant status id",
    )
    value = Column(Integer, comment="current value of applicants by status")
    date = Column(DateTime(), default=datetime.now().date(), comment="Date when registrate status")


class NewVacancies(Base):
    __tablename__ = "new_vacancies"
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
