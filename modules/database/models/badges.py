from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from modules.database.models import TimeStampMixin
from modules.utilities.database import Base


class Badge(Base, TimeStampMixin):
    """
    Badge model.
    """
    __tablename__ = "badges"
    id = Column(Integer, primary_key=True, index=True)
    badge_name = Column(String, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="badges")
