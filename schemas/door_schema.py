from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class LogQuery(BaseModel):
    user_id: Optional[int] = Field(None, description="用户ID（仅管理员可用）")
    device_name: Optional[str] = Field(None, max_length=100, description="设备名称模糊搜索")
    status: Optional[Literal["成功", "失败"]] = Field(None, description="状态：成功/失败")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
