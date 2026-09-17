from django.db import migrations


PROJECTS = {
    'TalentBridge': {
        'short_desc': 'Django REST backend for recruitment workflows.',
        'description': 'A public engineering case study of a Django REST recruitment platform. Customer workflows, policy rules, record relationships, and operating thresholds are intentionally omitted.',
        'problem': 'Recruitment software combines connected work with strict organizational boundaries. The backend needed maintainable interfaces and dependable processing without publishing private domain behavior.',
        'contribution': 'As a Mid Level Python Developer, I contributed backend endpoints, integration contracts, reliability improvements, documentation, and deployment support.',
        'technical_decisions': 'Django REST Framework provides a consistent API layer with documented contracts. Layered backend controls and asynchronous execution are used where appropriate. Permission formulas, record relationships, workflow transitions, and operating thresholds are not disclosed.',
        'outcome': 'The work strengthened the documented backend foundation and clarified responsibility boundaries. No production scale, customer outcome, or internal policy claim is made.',
        'lessons': 'Access boundaries work best as system-wide invariants, and API documentation is most useful when it evolves with implementation and validation.',
        'architecture_summary': 'A layered Django backend separates the public API, application responsibilities, data access, and supporting background work. Detailed authorization and domain rules remain private.',
        'features': 'Documented API contracts\nLayered backend controls\nAsynchronous execution where appropriate\nEnvironment-specific configuration',
        'challenges': [
            ('Maintaining access boundaries', 'Connected product data needs consistent separation.', 'Use layered backend controls and keep private policy details outside the public interface.', 'Validation focused on representative permitted and rejected requests.'),
            ('Separating longer-running work', 'Some processing does not belong in the request-response path.', 'Use asynchronous execution where appropriate while keeping the public API contract stable.', 'Validation focused on the boundary between request handling and background execution.'),
        ],
    },
    'Smart Document Vault': {
        'short_desc': 'Multi-tenant document API with secure isolation.',
        'description': 'A public engineering case study of a tenant-aware document service. Customer identifiers, policy rules, storage paths, security configuration, and recovery procedures are intentionally omitted.',
        'problem': 'A shared document platform must preserve customer isolation and handle document processing safely without exposing private policy or infrastructure details.',
        'contribution': 'I contributed tenant-aware design, secure processing, contract-aligned API behavior, and isolation-focused validation.',
        'technical_decisions': 'The design applies defense-in-depth to access and processing, with isolation enforced by the backend and asynchronous execution used where appropriate. Storage design, security configuration, and failure policies remain private.',
        'outcome': 'The project provides a security-conscious foundation for document management. It does not claim a public launch, customer volume, or security certification.',
        'lessons': 'Isolation and processing safety are strongest when treated as system-wide concerns rather than isolated endpoint checks.',
        'architecture_summary': 'The Django backend applies defense-in-depth to customer isolation, document access, and supporting processing. Policy evaluation, storage design, and failure handling remain private.',
        'features': 'Tenant-aware design\nDefense-in-depth\nAsynchronous processing\nDocumented API behavior',
        'challenges': [
            ('Maintaining customer isolation', 'Shared infrastructure must preserve separation between customer contexts.', 'Apply defense-in-depth in the backend without exposing policy mechanics publicly.', 'Validation focused on representative same-context and cross-context requests.'),
            ('Handling document processing safely', 'Document processing must preserve privacy and predictable API behavior.', 'Separate processing concerns from public access while keeping private failure policies undisclosed.', 'Validation focused on public availability behavior across processing outcomes.'),
        ],
    },
    'HotelMotel': {
        'short_desc': 'Django API foundation for hotel operations.',
        'description': 'A public engineering case study of a modular hotel-operations backend. Pricing, availability, staff procedures, state transitions, and internal model relationships are intentionally omitted.',
        'problem': 'Hotel operations connect several responsibilities that must remain consistent and appropriately authorized.',
        'contribution': 'I contributed backend APIs, modular domain organization, lifecycle handling, access controls, and automated checks.',
        'technical_decisions': 'The Django backend separates operational concerns into maintainable modules and validates access and consistency at server-controlled boundaries. State rules, pricing calculations, availability logic, and staff procedures remain private.',
        'outcome': 'The work established a maintainable API foundation with clearer responsibility and authorization boundaries. No production or commercial outcome is claimed.',
        'lessons': 'Operational systems are easier to change when responsibilities have clear ownership and shared behavior is validated at module boundaries.',
        'architecture_summary': 'A modular Django API separates major operational responsibilities while shared application services coordinate cross-domain work. Sensitive actions remain behind explicit server-side authorization.',
        'features': 'Modular Django domains\nExplicit action authorization\nConsistent lifecycle handling\nAutomated behavior checks',
        'challenges': [
            ('Keeping operational concerns maintainable', 'Connected hotel operations can become tightly coupled.', 'Separate responsibilities into focused modules with clear ownership.', 'Validation focused on the public behavior of connected modules.'),
            ('Controlling sensitive actions', 'Authenticated access alone is not sufficient for every operation.', 'Apply server-side authorization while keeping staff procedures private.', 'Validation focused on representative permitted and rejected actions.'),
        ],
    },
    'Portfolio Website': {
        'short_desc': 'Django portfolio with shared website and CV content.',
        'description': 'A Django portfolio designed to keep project, experience, and downloadable CV content consistent while applying explicit publication and privacy controls.',
        'problem': 'Website and CV content can drift when they are maintained separately, while draft and private material require explicit publication control.',
        'contribution': 'I designed and built the Django application, content workflow, generated CV, responsive interface, contact protections, and public-visibility tests.',
        'technical_decisions': 'Django admin owns structured content and publication status. Website pages and the generated PDF use the same provider, while canonical slugs and filtered public queries keep delivery predictable.',
        'outcome': 'Visitors can browse structured case studies and download a CV generated from current published content. The site also includes responsive navigation, metadata, and contact abuse protection.',
        'lessons': 'A small content system benefits more from one authoritative data path and tested publication rules than from additional infrastructure.',
        'architecture_summary': 'Django models and admin provide the content source. Public views filter publication state, templates render the website, and ReportLab produces the CV from the same provider.',
        'features': 'Database-backed content\nShared website and PDF provider\nExplicit publication controls\nResponsive and accessibility checks',
        'challenges': [
            ('Preventing content drift', 'Maintaining website and CV content independently creates inconsistent information.', 'Use one content provider for both HTML and generated PDF output.', 'Automated checks compare the content supplied to both outputs.'),
            ('Controlling public visibility', 'Editorial content needs a safe path from draft to public display.', 'Apply explicit publication controls before rendering public output.', 'Validation focused on draft and published visibility behavior.'),
        ],
    },
    'TheProperty': {
        'short_desc': 'Role-aware Django property marketplace.',
        'description': 'A public engineering case study of a property marketplace with controlled publication and protected private capabilities. Review criteria, ranking behavior, document details, and commercial rules are intentionally omitted.',
        'problem': 'A marketplace must support public discovery while keeping private workspaces and administrative responsibilities outside the public surface.',
        'contribution': 'I contributed the Django foundation, private workspaces, service boundaries, production configuration, and automated safeguards.',
        'technical_decisions': 'Public discovery, private management, and administrative responsibilities are separated through application boundaries and publishing controls. Review criteria, ranking behavior, document details, and commercial rules remain private.',
        'outcome': 'The project demonstrates a maintainable marketplace foundation with controlled publishing and protected private capabilities. No transaction volume or commercial outcome is claimed.',
        'lessons': 'Publishing state, authorization, and administrative traceability should reinforce one another rather than rely on interface visibility.',
        'architecture_summary': 'A server-rendered Django application separates public discovery, private workspaces, and administrative responsibilities. Review criteria and commercial rules remain private.',
        'features': 'Controlled publishing\nPrivate workspaces\nMaintainable service boundaries\nProduction-oriented safeguards',
        'challenges': [
            ('Separating discovery from management', 'Public browsing and private management have different visibility needs.', 'Keep public and private capabilities behind distinct application boundaries.', 'Validation focused on representative public and authenticated paths.'),
            ('Keeping publishing controlled', 'Content should appear publicly only after the appropriate internal decision.', 'Use explicit publishing controls without disclosing review criteria or state rules.', 'Validation focused on public visibility before and after publication.'),
        ],
    },
    'Homeopathic Management API': {
        'short_desc': 'Role-aware Django API for clinic operations.',
        'description': 'A public engineering case study of a clinic-management API. Patient data, medical decision rules, billing calculations, inventory formulas, and workflow transitions are intentionally omitted.',
        'problem': 'A clinic platform connects clinical and administrative responsibilities while requiring strong privacy and role boundaries.',
        'contribution': 'I contributed authenticated APIs, permission boundaries, clinical workflow support, inventory integration, and billing foundations.',
        'technical_decisions': 'Django REST Framework provides a documented, role-aware API with cohesive service responsibilities. Patient data, medical rules, billing calculations, inventory formulas, and workflow transitions remain private.',
        'outcome': 'The repository demonstrates an integrated clinic-management API while keeping medical, billing, and operational rules private. No healthcare outcome is claimed.',
        'lessons': 'In sensitive domains, privacy and data minimization should shape the API contract from the beginning.',
        'architecture_summary': 'A documented Django REST API separates authenticated access, clinical responsibilities, and administrative services. Medical rules and record structures remain private.',
        'features': 'Role-aware API design\nPrivacy-conscious boundaries\nCohesive service responsibilities\nDocumented API behavior',
        'challenges': [
            ('Protecting sensitive context', 'Clinical and administrative capabilities have different privacy needs.', 'Use role-aware backend boundaries without publishing medical or policy rules.', 'Validation focused on representative permitted and rejected access.'),
            ('Keeping connected areas cohesive', 'Several clinic responsibilities must cooperate without becoming one tightly coupled module.', 'Keep service responsibilities explicit and expose a consistent public API.', 'Validation focused on the documented contract between public API areas.'),
        ],
    },
}


def complete_case_studies(apps, schema_editor):
    Project = apps.get_model('home', 'Project')
    Challenge = apps.get_model('home', 'EngineeringChallenge')
    database = schema_editor.connection.alias
    for name, content in PROJECTS.items():
        for project in Project.objects.using(database).filter(name__iexact=name):
            Project.objects.using(database).filter(pk=project.pk).update(**{
                key: value for key, value in content.items() if key != 'challenges'
            })
            for order, (title, problem, approach, verification) in enumerate(content['challenges']):
                Challenge.objects.using(database).update_or_create(
                    project_id=project.pk, title=title,
                    defaults={
                        'problem': problem, 'approach': approach, 'solution': '',
                        'trade_offs': '', 'verification': verification,
                        'source_url': '', 'is_published': True, 'order': order,
                    },
                )


class Migration(migrations.Migration):
    dependencies = [('home', '0032_tighten_public_project_copy')]
    operations = [migrations.RunPython(complete_case_studies, migrations.RunPython.noop)]
