from pydantic import BaseModel


class IssueRequest(BaseModel):
    message: str


class TicketResponse(BaseModel):
    ticket_id: str
    message: str
    category: str
    priority: str
    reply: str
    status: str

    class Config:
        from_attributes = True


class StatusUpdate(BaseModel):
    status: str