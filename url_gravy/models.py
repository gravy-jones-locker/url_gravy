from sqlalchemy import String, Column, Integer, Date, Index
from datetime import date

from sam_core.database import Base

class Redirect(Base):
    __tablename__ = 'redirect'

    id = Column(Integer, autoincrement=True, primary_key=True)
    suffix = Column(String, nullable=False)
    target = Column(String, nullable=False)
    created_on = Column(Date, default=date.today)

    Index('ix_redirect_suffix', suffix, unique=True)
