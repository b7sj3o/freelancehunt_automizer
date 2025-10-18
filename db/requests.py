from sqlalchemy import select

from core.loggers import requests_logger as logger
from db import Session
from db.models import Project
from schemas.project import CreateProjectSchema, UpdateProjectSchema

def get_all_projects() -> list[Project]:
    with Session() as session:
        return session.scalars(select(Project)).all()


def get_active_projects() -> list[Project]:
    with Session() as session:
        return session.scalars(
            select(Project)
            .where(Project.is_bid_placed.is_(False))
            .where(Project.is_bid_skipped.is_(False))
        ).all()

def get_project(link: str) -> Project|None:
    with Session() as session:
        return session.scalars(select(Project).where(Project.link == link)).first()


def create_projects(data: list[CreateProjectSchema]) -> list[Project]:
    with Session() as session:
        try:
            projects = [Project(**project.model_dump()) for project in data]
            session.add_all(projects)
            session.commit()
            for project in projects:
                session.refresh(project)

            logger.info(f"Projects created: {[project.title for project in projects]}")
            return projects
        except Exception as e:
            logger.error(f"Error creating projects: {e}")


def update_project(project_id: int, data: UpdateProjectSchema) -> Project:
    with Session() as session:
        project = session.scalars(select(Project).where(Project.id == project_id)).first()


        if not project:
            logger.error(f"Project with id {project_id} not found")
            raise ValueError(f"Project with id {project_id} not found")

        data_dict = data.model_dump(exclude_none=True, exclude_unset=True)

        for key, value in data_dict.items():
            setattr(project, key, value)

        session.commit()
        session.refresh(project)
        
        logger.info(f"Project updated: {project.title}, data: {data_dict}")

        return project