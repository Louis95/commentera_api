from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from modules.database.models import TimeStampMixin
from modules.utilities.database import Base


class User(Base, TimeStampMixin):
    """
    Represents a user model.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    customer_id = Column(String)

    badges = relationship("Badge", back_populates="user")
