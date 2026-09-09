"""Case-study copy grounded in the local project repositories; no inferred metrics."""
CASE_STUDIES = {
    "TalentBridge": {
        "problem": "Recruitment involves connected records: candidates, employers, vacancies, shortlists, and interviews. The backend needs to represent that workflow together with milestones and audit events.",
        "contribution": "Mid Level Python Developer at TalentBridge, working remotely with the Germany-based team since June 2026.",
        "technical_decisions": "Django REST Framework exposes the recruitment domain through an API, with drf-spectacular providing its OpenAPI contract. This gives frontend integration a documented interface.\n\nRedis and Celery support asynchronous jobs and scheduled tasks alongside the web service. Running workers separately adds operational dependencies that must be configured with the application.\n\nPostgreSQL is used in shared environments, while SQLite supports local work. Environment-specific configuration separates development setup from deployment.",
        "outcome": "The repository contains the recruitment API, background-job infrastructure, API documentation, and Docker deployment configuration.",
    },
    "Smart Document Vault": {
        "problem": "A document service must keep each workspace’s files separate and prevent unscanned uploads from becoming downloadable. These boundaries affect both data queries and file storage.",
        "technical_decisions": "Requests select workspace context through X-Workspace-ID. Workspace-scoped access and policy-based authorization provide the boundaries for document operations.\n\nUploads remain in private quarantine until ClamAV scanning succeeds. Celery handles scanning work; unavailable workers or scanners leave files unavailable for download. This favors controlled access over immediate file availability.\n\nDocument and version uploads support idempotency keys, so retries can replay an existing response rather than repeat the operation.",
        "outcome": "Authentication, workspace, folder, and document routes are mounted. The repository also contains tenant-isolation tests and an OpenAPI contract. Sharing, subscriptions, and other supporting modules remain outside the completed launch scope.",
    },
    "HotelMotel": {
        "problem": "Hotel operations need to connect reservations, guests, rooms, prices, and actual stays while controlling who may perform sensitive booking actions.",
        "technical_decisions": "Booking, BookingRoom, and Stay are separate models. BookingRoom connects a reservation to rooms and nightly prices; Stay records actual check-in and check-out independently of planned dates.\n\nExplicit permissions cover actions such as confirmation, cancellation, check-in, refunds, and price access. This provides finer authorization vocabulary than a single general editing permission.\n\nSeparate Django applications organize bookings, rooms, guests, billing, and housekeeping, giving each domain a clear place in the backend.",
        "outcome": "The backend includes reservation and stay records, room associations, monetary fields, and booking-action permission definitions. These form the foundation for the hotel operations API.",
    },
    "Portfolio Website": {
        "problem": "Project details and a downloadable CV need to stay consistent as experience and work samples change. Maintaining a separate PDF by hand creates duplicate editing work.",
        "technical_decisions": "Django admin manages published projects, case-study text, and ordered image and video galleries. Draft projects are excluded from public pages and the generated CV.\n\nThe website and PDF share a content provider. ReportLab renders the CV on request, so published project updates flow into the download.\n\nThe homepage highlights selected work, while a dedicated projects index and detail pages provide room for technical explanations.",
        "outcome": "Visitors can browse projects and download a CV generated from current content. The portfolio includes a saved theme preference, project publishing controls, and automated tests for public visibility and content rendering.",
    },
}
