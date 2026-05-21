from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from database.db import Base
from datetime import datetime

class DoorLog(Base):
    __tablename__ = "door_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"))
    device_id = Column(Integer, ForeignKey("device.id", ondelete="SET NULL"))
    action = Column(String(50))
    status = Column(String(50))
    time = Column(DateTime, default=datetime.now)

