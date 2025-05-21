from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, field_validator, ConfigDict # Added ConfigDict
from uuid import UUID 
from datetime import datetime

from .database import get_db
from .models import Prompt
from .ai_service import AIService

router = APIRouter()
ai_service = AIService()

class GenerateRequest(BaseModel):
    user_id: str
    query: str
    # If this model had a Config class, update it to model_config = ConfigDict(...)

class GenerateResponse(BaseModel):
    casual_response: str
    formal_response: str
    # If this model had a Config class, update it to model_config = ConfigDict(...)

class PromptResponse(BaseModel):
    id: str
    user_id: str
    query: str
    casual_response: str
    formal_response: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True) # New way, at the class level

    @field_validator("id", mode='before')
    @classmethod
    def coerce_id_to_string(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v


@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest, db: Session = Depends(get_db)):
    try:
        responses = ai_service.generate_responses(request.query)
        new_prompt = Prompt(
            user_id=request.user_id,
            query=request.query,
            casual_response=responses["casual_response"],
            formal_response=responses["formal_response"]
        )
        db.add(new_prompt)
        db.commit()
        db.refresh(new_prompt)
        return responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[PromptResponse])
def get_history(user_id: str, db: Session = Depends(get_db)):
    prompts = (
        db.query(Prompt)
        .filter(Prompt.user_id == user_id)
        .order_by(Prompt.created_at.desc())
        .all()
    )
    return [PromptResponse.model_validate(prompt) for prompt in prompts]