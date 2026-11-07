from sqlalchemy import Column,String,Integer,Boolean
from app.db import Base

class TaskModel(Base):
    __tablename__="test"
    id=Column(Integer,primary_key=True)
    title=Column(String)
    description=Column(String)
    is_completed=Column(Boolean,default=False)