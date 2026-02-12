from pydantic import BaseModel, Field


class SuggestRequest(BaseModel):
    text: str = Field(min_length=1, max_length=8000)


class SuggestItem(BaseModel):
    branch: str
    commit: str
