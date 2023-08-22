"""Models defining various utility models."""

from sqlalchemy import Column, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TimeStampMixin(Base):
    """
    Mixin for adding created_at and updated_at timestamps to models.
    """

    __abstract__ = True

    created_at = Column(TIMESTAMP(precision=6), server_default=func.now())
    updated_at = Column(TIMESTAMP(precision=6), server_default=func.now())
