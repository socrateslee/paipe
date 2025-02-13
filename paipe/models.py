from pydantic import BaseModel, Field


class PaipeContext(BaseModel):
    profile: str = Field(default='default', description='The profile name')
    system_prompt: str | None = Field(default=None, description='The system prompt')
    stream: bool = Field(default=True, description='Enable stream mode')
    input_text: str = Field(default='', description='The input text')
    prompt: str = Field(default='', description='The prompt')
    attachments: list = Field(default=[], description='The attachments')