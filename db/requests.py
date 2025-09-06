from sqlalchemy import select

from core.logger_config import setup_logger
from db import Session
from db.models import Project
from schemas.project import ProjectSchema, CreateProjectSchema


logger = setup_logger(name="requests", log_file="requests.log")

def get_projects() -> list[ProjectSchema]:
    with Session() as session:
        return session.scalars(select(Project)).all()


def get_project(name: str) -> ProjectSchema|None:
    with Session() as session:
        return session.scalars(select(Project).where(Project.name == name)).first()


def create_project(data: CreateProjectSchema) -> ProjectSchema:
    with Session() as session:
        try:
            project = Project(**data.model_dump())
            session.add(project)
            session.commit()
            session.refresh(project)

            logger.info(f"Project created: {project.title}")
            return ProjectSchema(**project.model_dump())
        except:
            logger.exception("Error creating project")