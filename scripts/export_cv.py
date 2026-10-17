"""Optional snapshot export using the same live data as the website download."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rahidulislam.settings")


def main():
    import django

    django.setup()
    from apps.resumes.pdf import build_cv
    from apps.resumes.presentation import resume_context as get_portfolio_data

    data = get_portfolio_data()
    output = ROOT / "output/pdf/Rahidul_Islam_Python_Developer_CV.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(build_cv(data["cv_profile"], data["cv_projects"]))
    print(output)


if __name__ == "__main__":
    main()
