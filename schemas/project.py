from __future__ import annotations

from enum import Enum
from pydantic import BaseModel


class MarketplaceEnum(Enum):
    FREELANCEHUNT = "freelancehunt"
    FREELANCER = "freelancer"
    
class ProjectSchema(BaseModel):
    id: int
    title: str
    link: str
    price: int
    currency: str
    marketplace: MarketplaceEnum

    bid_message: str|None = None

    is_bid_placed: bool = False
    is_bid_skipped: bool = False


class CreateProjectSchema(BaseModel):
    title: str
    link: str
    price: int
    currency: str
    marketplace: MarketplaceEnum

    is_bid_placed: bool = False
    is_bid_skipped: bool = False


class UpdateProjectSchema(BaseModel):
    is_bid_placed: bool|None = None
    is_bid_skipped: bool|None = None
    bid_message: str|None = None

