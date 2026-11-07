from app.dtos1 import TaskSchema
from sqlalchemy.orm import Session
from app.models1 import TaskModel
from app.models import Mess
from app.schemas import MessResponse
from datetime import datetime
def create_task(body:TaskSchema,db:Session):
    data=(body.model_dump())
    new_task=TaskModel(title=data["title"],
                       description=data["description"],
                       is_completed=data["is_completed"]
                       )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return {"Staus":"Task created succesfully..","data":new_task}

def create_items(body:MessResponse,db:Session):
    data=(body.model_dump())
    new_item=MessResponse(name=data["item"],
                          is_active=1,
                          created_at=datetime.now()
                          )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return{"Status":"Item added succesfully",data:new_item}