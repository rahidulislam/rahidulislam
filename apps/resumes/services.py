from .pdf import build_cv
from .presentation import resume_context


def generate_cv() -> bytes:
    data = resume_context()
    return build_cv(data["cv_profile"], data["cv_projects"])
