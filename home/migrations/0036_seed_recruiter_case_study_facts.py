from django.db import migrations


FACTS = {
    'TalentBridge': {
        'project_type': 'Recruitment platform backend', 'project_role': 'Mid Level Python Developer',
        'collaboration': 'Product engineering team', 'development_status': 'Ongoing development',
        'contribution_areas': 'Backend endpoints\nAPI contracts and documentation\nReliability improvements\nDeployment support',
        'constraints': 'Organizational data required strict separation. Frontend integrations needed predictable contracts, and longer-running work could not make normal API requests unreliable.',
        'validation': 'Validation focused on representative permitted and rejected requests, documented response behavior, and the boundary between request handling and background execution.',
    },
    'Smart Document Vault': {
        'project_type': 'Multi-tenant document SaaS backend', 'project_role': 'Backend Developer',
        'collaboration': 'Backend-focused project', 'development_status': 'Development repository',
        'contribution_areas': 'Tenant-aware design\nDocument-processing safety\nAPI contract alignment\nIsolation-focused validation',
        'constraints': 'Customer contexts required reliable separation, document processing needed privacy-conscious handling, and public documentation could not expose security configuration or storage design.',
        'validation': 'Validation focused on representative same-context and cross-context requests, public availability behavior, and documented API responses.',
    },
    'HotelMotel': {
        'project_type': 'Hotel operations backend', 'project_role': 'Backend Developer',
        'collaboration': 'Backend implementation project', 'development_status': 'Foundation implemented',
        'contribution_areas': 'Backend APIs\nModular domain organization\nAccess boundaries\nAutomated behavior checks',
        'constraints': 'Connected operational responsibilities needed consistent behavior while pricing, availability, staff procedures, and state rules remained private.',
        'validation': 'Validation focused on public API behavior, representative permission outcomes, and interactions between maintainable modules.',
    },
    'Portfolio Website': {
        'project_type': 'Django portfolio and CV platform', 'project_role': 'Designer and Full-stack Developer',
        'collaboration': 'Independent project', 'development_status': 'Active',
        'contribution_areas': 'Django application and content model\nResponsive interface\nGenerated PDF CV\nPublishing and contact protections',
        'constraints': 'Website and CV content needed one source of truth, drafts could not become public, and the site needed to remain maintainable without a large CMS.',
        'validation': 'Automated checks cover shared website and CV content, draft visibility, contact protection, canonical project routes, and responsive behavior.',
    },
    'TheProperty': {
        'project_type': 'Server-rendered property marketplace', 'project_role': 'Django Developer',
        'collaboration': 'Independent product project', 'development_status': 'First-release foundation',
        'contribution_areas': 'Django foundation\nPrivate workspaces\nService boundaries\nProduction configuration',
        'constraints': 'Public discovery and private management required different visibility boundaries. Review criteria, document details, ranking behavior, and commercial rules could not be published.',
        'validation': 'Validation focused on representative public and authenticated paths, publication visibility, and protected private capabilities.',
    },
    'Homeopathic Management API': {
        'project_type': 'Clinic management API', 'project_role': 'Backend Developer',
        'collaboration': 'Backend implementation project', 'development_status': 'API foundation implemented',
        'contribution_areas': 'Authenticated APIs\nPrivacy-aware boundaries\nClinical workflow support\nAdministrative service integration',
        'constraints': 'Patient context and clinical responsibilities required careful privacy boundaries. Medical rules, billing calculations, inventory formulas, and workflow states could not be disclosed.',
        'validation': 'Validation focused on documented API behavior, representative role boundaries, and the public contract between connected service areas.',
    },
}


TRADE_OFFS = {
    'TalentBridge': {
        'Maintaining access boundaries': 'Layered controls require consistent maintenance and broader permission-focused validation.',
        'Separating longer-running work': 'Asynchronous execution adds operational components that must be configured and observed.',
    },
    'Smart Document Vault': {
        'Maintaining customer isolation': 'Defense-in-depth adds implementation and validation work but reduces reliance on any single control.',
        'Handling document processing safely': 'Separating processing improves safety boundaries while adding operational coordination.',
    },
    'HotelMotel': {
        'Keeping operational concerns maintainable': 'Modular ownership improves clarity but requires explicit coordination between responsibilities.',
        'Controlling sensitive actions': 'Narrow authorization is safer than broad access but expands the permission scenarios that need validation.',
    },
    'Portfolio Website': {
        'Preventing content drift': 'A shared provider reduces duplication but requires website and PDF consumers to evolve together.',
        'Controlling public visibility': 'Explicit publishing controls add editorial steps but make public exposure intentional and testable.',
    },
    'TheProperty': {
        'Separating discovery from management': 'Distinct boundaries improve privacy but require careful coordination of shared presentation needs.',
        'Keeping publishing controlled': 'Controlled publishing adds workflow overhead while preventing accidental public visibility.',
    },
    'Homeopathic Management API': {
        'Protecting sensitive context': 'Role-aware boundaries increase permission complexity but reduce unnecessary data exposure.',
        'Keeping connected areas cohesive': 'Separate responsibilities improve maintainability while requiring explicit contracts between services.',
    },
}


def seed_facts(apps, schema_editor):
    Project = apps.get_model('home', 'Project')
    Challenge = apps.get_model('home', 'EngineeringChallenge')
    database = schema_editor.connection.alias
    for name, facts in FACTS.items():
        projects = Project.objects.using(database).filter(name__iexact=name)
        projects.update(**facts)
        for project_id in projects.values_list('pk', flat=True):
            for title, trade_offs in TRADE_OFFS[name].items():
                Challenge.objects.using(database).filter(
                    project_id=project_id, title=title,
                ).update(trade_offs=trade_offs)


class Migration(migrations.Migration):
    dependencies = [('home', '0035_project_recruiter_case_study_facts')]
    operations = [migrations.RunPython(seed_facts, migrations.RunPython.noop)]
