"""User model"""

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from modules.utilities.database import Base


class User(Base):
    """
    Represents a user model.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    customer_id = Column(String)

    badges = relationship("Badge", back_populates="user")
