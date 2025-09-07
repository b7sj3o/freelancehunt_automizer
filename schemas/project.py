from pydantic import BaseModel


class ProjectSchema(BaseModel):
    id: int
    title: str
    link: str
    price: int

    bid_message: str|None = None

    is_bid_placed: bool = False
    is_bid_skipped: bool = False


class CreateProjectSchema(BaseModel):
    title: str
    link: str
    price: int

    is_bid_placed: bool = False
    is_bid_skipped: bool = False


class UpdateProjectSchema(BaseModel):
    is_bid_placed: bool|None = None
    is_bid_skipped: bool|None = None
    bid_message: str|None = None