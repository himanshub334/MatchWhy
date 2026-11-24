from pydantic import BaseModel,Field
class ProfileIn(BaseModel):
    name:str="Demo candidate"
    wants:list[str]=Field(default_factory=list)
    skills:list[str]=Field(default_factory=list)
    preferred_locations:list[str]=Field(default_factory=list)
    target_levels:list[str]=Field(default_factory=list)
    excluded_terms:list[str]=Field(default_factory=list)
    minimum_retrieval_score:float=0.0
class FeedbackIn(BaseModel):
    recommendation_id:int
    kind:str
    cause:str="other"
    note:str=""
