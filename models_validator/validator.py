import re
from pydantic import BaseModel, Field, field_validator


from pydantic import BaseModel
class DateValidator(BaseModel):
    date: str = Field(description="Date in DD-MM-YYYY format")
    @field_validator('date')
    def validate_date(cls, v):
        pattern = r'^\d{2}-\d{2}-\d{4}$'
        if not re.match(pattern, v):
            raise ValueError('Date must be in DD-MM-YYYY format')
        return v
    
    
class DateTimeModel(BaseModel):
    date_time:str=Field(description="Date and Time in DD-MM-YYYY HH:MM format")
    @field_validator('date_time')
    def validate_date_time(cls,v):
        if not re.match(r'^\d{2}-\d{2}-\d{4} \d{2}:\d{2}$', v):
            raise ValueError('DateTime must be in DD-MM-YYYY HH:MM format')
        return v

class IdentifiactionNumberValidator(BaseModel):
    id:int = Field(description="Identification number consisting of 7 to 8 digits")
    @field_validator('id')
    def id_validator(cls,v):
        """it has only digits and length is 7 t0 8"""
        pattern=r'^\d{7,8}$'
        if not re.match(pattern,v):
            raise ValueError('ID must be 7 to 8 digits')
        return v