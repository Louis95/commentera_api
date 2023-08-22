"""badges mode"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from modules.utilities.database import Base


class Badge(Base):
    """
    Badge model.
    """

    __tablename__ = "badges"
    id = Column(Integer, primary_key=True, index=True)
    badge_name = Column(String, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user = relationship("User", back_populates="badges")
