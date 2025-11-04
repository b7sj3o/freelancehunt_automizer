from sqlalchemy.orm import Mapped, mapped_column
from db import Base
from schemas.project import MarketplaceEnum
from sqlalchemy.types import Enum as SQLEnum

class Project(Base):
    __tablename__ = "projects"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[int] = mapped_column(nullable=True)
    currency: Mapped[str] = mapped_column(nullable=True, default="UAH")
    marketplace: Mapped[MarketplaceEnum] = mapped_column(SQLEnum(MarketplaceEnum), nullable=False)

    bid_message: Mapped[str] = mapped_column(nullable=True)

    is_bid_placed: Mapped[bool] = mapped_column(default=False)
    is_bid_skipped: Mapped[bool] = mapped_column(default=False)

    def __repr__(self):
        return f"Project(id={self.id}, title={self.title}, link={self.link}, price={self.price})"