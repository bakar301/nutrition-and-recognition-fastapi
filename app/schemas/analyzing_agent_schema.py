from pydantic import BaseModel

class AnalyzingAgentSchema(BaseModel):
    image_path: str