from pydantic import BaseModel


class AgentStatusResponse(BaseModel):

    name: str

    status: str