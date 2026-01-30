from pydantic import BaseModel

class IngestRequest(BaseModel):
    subject: str
    filename: str
    use_llamaparse: bool = False  # default to False if not sent