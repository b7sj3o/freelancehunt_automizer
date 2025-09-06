from pydantic import BaseModel


class ProjectSchema(BaseModel):
    # id: int
    title: str
    link: str
    bids: int
    # price: int = 0

    # is_bid_placed: bool = False
    # is_bid_skipped: bool = False


class CreateProjectSchema(BaseModel):
    title: str
    link: str
    price: int = 0

    is_bid_placed: bool = False
    is_bid_skipped: bool = False

