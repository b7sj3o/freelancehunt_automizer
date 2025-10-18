from db.models.project import Project
from db import Session

def remove_all_projects():
    with Session() as session:
        session.query(Project).delete()
        session.commit()

if __name__ == "__main__":
    remove_all_projects()
