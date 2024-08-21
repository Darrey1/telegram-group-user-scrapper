from sqlmodel import SQLModel, Field, Column
from uuid import UUID,uuid4
from sqlalchemy.dialects.mysql import CHAR
from datetime import datetime
from typing import Optional,Any

class Books(SQLModel, table=True):
    __tablename__ = "Books"
    id:UUID = Field(
        sa_column=Column(type_=CHAR(36),
                         default=lambda: str(uuid4()),
                         primary_key=True, 
                         unique=True
                         
                         ) )
    title:str
    author:str
    isbn:str
    descriptions:str
    created_at:datetime= Field(default_factory=datetime.now)
    updated_at:datetime = Field(default_factory=datetime.now)
    # def __repr__(self) -> str:
    #     return f"table Books created successfully!"
    
    
class Registration(SQLModel,table= True):
    
    __tablename__ = "Registration"
    # id:UUID = Books.id
    username:str = Field(
        primary_key=True
    )
    hashed_password:str
    email:str
    full_name:str
    disabled:bool 
    