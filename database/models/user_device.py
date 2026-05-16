
from database.db import Base
from sqlalchemy import Column, Integer, ForeignKey

class UserDevice(Base):
    __tablename__ = "user_device"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"))
    device_id = Column(Integer, ForeignKey("device.id", ondelete="CASCADE"), index=True)

