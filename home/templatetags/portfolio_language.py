from django import template
register = template.Library()

TRANSLATIONS = {
    'Projects': 'প্রজেক্ট', 'Projects.': 'প্রজেক্টসমূহ।', 'Experience': 'অভিজ্ঞতা',
    'Skills': 'দক্ষতা', 'About': 'পরিচিতি', 'Articles': 'লেখালেখি', 'Let’s talk': 'যোগাযোগ করুন',
    'Project library': 'প্রজেক্ট লাইব্রেরি', 'Selected projects.': 'নির্বাচিত প্রজেক্ট।',
    'Search projects': 'প্রজেক্ট খুঁজুন', 'Search by name, topic or technology': 'নাম, বিষয় বা প্রযুক্তি দিয়ে খুঁজুন',
    'Work type': 'কাজের ধরন', 'All types': 'সব ধরনের', 'Backend': 'ব্যাকএন্ড', 'Frontend': 'ফ্রন্টএন্ড', 'Full-stack': 'ফুল-স্ট্যাক',
    'Technology': 'প্রযুক্তি', 'All technologies': 'সব প্রযুক্তি', 'Apply filters': 'ফিল্টার করুন', 'Reset': 'রিসেট',
    'No projects match these filters.': 'এই ফিল্টারে কোনো প্রজেক্ট পাওয়া যায়নি।',
    'Read case study': 'বিস্তারিত দেখুন', 'View all projects': 'সব প্রজেক্ট দেখুন',
    'Engineering articles': 'প্রযুক্তি বিষয়ক লেখা', 'Engineering notes from my projects.': 'আমার প্রজেক্ট থেকে প্রযুক্তি বিষয়ক অভিজ্ঞতা।',
    'Read article': 'লেখা পড়ুন', 'Back to articles': 'সব লেখায় ফিরুন', 'Source code': 'সোর্স কোড',
    'Professional experience.': 'পেশাগত অভিজ্ঞতা।', 'Responsibilities and contributions': 'দায়িত্ব ও অবদান',
    'View experience': 'অভিজ্ঞতা দেখুন', 'All experience': 'সব অভিজ্ঞতা', 'Related work': 'সংশ্লিষ্ট কাজ',
    'Project screenshots': 'প্রজেক্টের স্ক্রিনশট', 'Architecture overview': 'সিস্টেমের গঠন', 'Demo walkthrough': 'ডেমো ভিডিও',
    'Public architecture diagram': 'সিস্টেমের গঠনচিত্র', 'Testimonials': 'সহকর্মী ও ক্লায়েন্টের মতামত',
    'Feedback shared with permission.': 'অনুমতি নিয়ে প্রকাশিত মতামত।',
    'Start a conversation': 'কথা শুরু করুন', 'Send message': 'বার্তা পাঠান',
    'Name': 'নাম', 'Email': 'ইমেইল', 'Subject': 'বিষয়', 'Message': 'বার্তা',
    'Your details and message are stored so I can respond to your enquiry.': 'আপনার প্রশ্নের উত্তর দেওয়ার জন্য তথ্য ও বার্তা সংরক্ষণ করা হবে।',
    'Download CV': 'সিভি ডাউনলোড', 'View case studies': 'প্রজেক্টের বিস্তারিত দেখুন',
    'Open to relocation to Germany and remote opportunities': 'জার্মানিতে স্থানান্তর ও রিমোট কাজের সুযোগে আগ্রহী',
    'Python & Django engineer building secure business systems': 'Python ও Django দিয়ে নিরাপদ ব্যবসায়িক সফটওয়্যার তৈরি করি',
    'I build REST APIs and operational software for recruitment, document management, and hospitality. Based in Bangladesh and open to relocation to Germany and remote opportunities.': 'নিয়োগ, ডকুমেন্ট ব্যবস্থাপনা ও হোটেল পরিচালনার জন্য REST API ও সফটওয়্যার তৈরি করি। বাংলাদেশে থাকি; জার্মানিতে স্থানান্তর ও রিমোট কাজে আগ্রহী।',
    'Let’s discuss': 'আলোচনা করি', 'your next role.': 'আপনার পরবর্তী সুযোগ নিয়ে।',
    'All projects': 'সব প্রজেক্ট', 'My role': 'আমার ভূমিকা', 'The problem': 'সমস্যা',
    'Technical decisions': 'প্রযুক্তিগত সিদ্ধান্ত', 'Validation': 'যাচাই', 'Overview': 'পরিচিতি',
    'Constraints': 'সীমাবদ্ধতা', 'What the project delivers': 'প্রজেক্টে যা তৈরি হয়েছে',
    'Lessons and next steps': 'শেখা ও পরবর্তী কাজ', 'Technical focus': 'প্রযুক্তিগত দিক',
    'Live project': 'লাইভ প্রজেক্ট', 'Close image': 'ছবি বন্ধ করুন', 'Previous image': 'আগের ছবি', 'Next image': 'পরের ছবি',
}

TRANSLATIONS.update({'01 / Selected work': '০১ / নির্বাচিত প্রজেক্ট',
 '02 / Experience': '০২ / অভিজ্ঞতা',
 '03 / What I work with': '০৩ / যেসব প্রযুক্তি ব্যবহার করি',
 '04 / A little about me': '০৪ / আমার পরিচিতি',
 '05 / Get in touch': '০৫ / যোগাযোগ',
 'A clear path from request to response.': 'Request থেকে response-এর সুস্পষ্ট পথ।',
 'APIs · authentication · business logic': 'API · পরিচয় যাচাই · business logic',
 'About me.': 'আমার পরিচিতি।',
 'Administrator demo dashboard — session statistics and institutional overview.': 'Administrator '
                                                                                  'demo dashboard '
                                                                                  '— session-এর '
                                                                                  'পরিসংখ্যান ও '
                                                                                  'প্রতিষ্ঠানের '
                                                                                  'সারাংশ।',
 'BACKEND DEVELOPMENT': 'ব্যাকএন্ড ডেভেলপমেন্ট',
 'BASED IN': 'বর্তমান অবস্থান',
 'Back to top': 'উপরে ফিরুন',
 'Bangladesh': 'বাংলাদেশ',
 'Bilingual React frontend for admissions, attendance, fees and madrasha administration.': 'ভর্তি, '
                                                                                           'হাজিরা, '
                                                                                           'ফি ও '
                                                                                           'মাদ্রাসা '
                                                                                           'প্রশাসনের '
                                                                                           'জন্য '
                                                                                           'বাংলা '
                                                                                           'ও '
                                                                                           'ইংরেজি '
                                                                                           'React '
                                                                                           'frontend।',
 'COLLABORATION': 'সহযোগিতা',
 'CONTRIBUTION AREAS': 'আমার অবদানের ক্ষেত্র',
 'Contact': 'যোগাযোগ',
 'Django API foundation for hotel operations.': 'হোটেল পরিচালনার জন্য Django API foundation।',
 'Django REST backend for recruitment workflows.': 'নিয়োগের কাজের জন্য Django REST backend।',
 'Django portfolio site for projects, experience, and contact.': 'প্রজেক্ট, অভিজ্ঞতা ও যোগাযোগের '
                                                                 'জন্য Django portfolio।',
 'Download CV (PDF)': 'সিভি ডাউনলোড (PDF)',
 'ENGINEERING FOCUS': 'কাজের প্রযুক্তিগত ক্ষেত্র',
 'Education': 'শিক্ষা',
 'FOCUS': 'কাজের লক্ষ্য',
 'Fee collection — student search and payment workflow in the demo.': 'ফি আদায় — demo-তে '
                                                                      'শিক্ষার্থী নির্বাচন ও '
                                                                      'payment workflow।',
 'Handcrafted with Python & Django': 'Python ও Django দিয়ে তৈরি',
 'I care about clear boundaries, dependable APIs, and software that is straightforward for another developer to understand. I am preparing for the next stage of my career with a team in Germany or a remote engineering role.': 'সুস্পষ্ট '
                                                                                                                                                                                                                                  'কাজের '
                                                                                                                                                                                                                                  'সীমা, '
                                                                                                                                                                                                                                  'নির্ভরযোগ্য '
                                                                                                                                                                                                                                  'API '
                                                                                                                                                                                                                                  'এবং '
                                                                                                                                                                                                                                  'অন্য '
                                                                                                                                                                                                                                  'developer '
                                                                                                                                                                                                                                  'সহজে '
                                                                                                                                                                                                                                  'বুঝতে '
                                                                                                                                                                                                                                  'পারেন '
                                                                                                                                                                                                                                  'এমন '
                                                                                                                                                                                                                                  'software '
                                                                                                                                                                                                                                  'তৈরি '
                                                                                                                                                                                                                                  'করতে '
                                                                                                                                                                                                                                  'পছন্দ '
                                                                                                                                                                                                                                  'করি। '
                                                                                                                                                                                                                                  'জার্মানির '
                                                                                                                                                                                                                                  'একটি '
                                                                                                                                                                                                                                  'টিম '
                                                                                                                                                                                                                                  'বা '
                                                                                                                                                                                                                                  'রিমোট '
                                                                                                                                                                                                                                  'engineering '
                                                                                                                                                                                                                                  'role-এর '
                                                                                                                                                                                                                                  'মাধ্যমে '
                                                                                                                                                                                                                                  'ক্যারিয়ারের '
                                                                                                                                                                                                                                  'পরবর্তী '
                                                                                                                                                                                                                                  'ধাপের '
                                                                                                                                                                                                                                  'জন্য '
                                                                                                                                                                                                                                  'প্রস্তুতি '
                                                                                                                                                                                                                                  'নিচ্ছি।',
 'I’m open to Python and Django roles with teams in Germany, including relocation, and remote opportunities. Tell me what your team is building.': 'জার্মানির '
                                                                                                                                                   'টিমের '
                                                                                                                                                   'সঙ্গে '
                                                                                                                                                   'Python '
                                                                                                                                                   'ও '
                                                                                                                                                   'Django '
                                                                                                                                                   'developer '
                                                                                                                                                   'হিসেবে '
                                                                                                                                                   'কাজ, '
                                                                                                                                                   'স্থানান্তর '
                                                                                                                                                   'এবং '
                                                                                                                                                   'রিমোট '
                                                                                                                                                   'কাজের '
                                                                                                                                                   'সুযোগে '
                                                                                                                                                   'আগ্রহী। '
                                                                                                                                                   'আপনার '
                                                                                                                                                   'টিম '
                                                                                                                                                   'কী '
                                                                                                                                                   'তৈরি '
                                                                                                                                                   'করছে '
                                                                                                                                                   'জানাতে '
                                                                                                                                                   'পারেন।',
 'Let’s discuss': 'আলোচনা করি',
 'MY ROLE': 'আমার ভূমিকা',
 'Mobile preview — Bengali public website at 390px width.': 'Mobile preview — 390px width-এ বাংলা '
                                                            'public website।',
 'Multi-tenant document-management API with secure isolation.': 'নিরাপদ tenant separation-সহ '
                                                                'document-management API।',
 'NEXT CHAPTER': 'পরবর্তী অধ্যায়',
 'PROJECT TYPE': 'প্রজেক্টের ধরন',
 'Please check the fields below. Your message has not been submitted.': 'নিচের তথ্যগুলো যাচাই '
                                                                        'করুন। আপনার বার্তা এখনও '
                                                                        'পাঠানো হয়নি।',
 'Project facts': 'প্রজেক্টের তথ্য',
 'Public website — Bengali landing page and demo entry.': 'Public website — বাংলা landing page ও '
                                                          'demo প্রবেশপথ।',
 'Python & Django Engineer · Building secure APIs and dependable business systems.': 'Python ও '
                                                                                     'Django '
                                                                                     'Engineer · '
                                                                                     'নিরাপদ API ও '
                                                                                     'নির্ভরযোগ্য '
                                                                                     'ব্যবসায়িক '
                                                                                     'system তৈরি '
                                                                                     'করি।',
 'Recruitment · Documents · Hospitality': 'নিয়োগ · ডকুমেন্ট · হোটেল',
 'Recruitment, document management, education, hospitality, property, and healthcare systems. A selection of the products I build.': 'নিয়োগ, '
                                                                                                                                     'ডকুমেন্ট '
                                                                                                                                     'ব্যবস্থাপনা, '
                                                                                                                                     'শিক্ষা, '
                                                                                                                                     'হোটেল, '
                                                                                                                                     'সম্পত্তি '
                                                                                                                                     'ও '
                                                                                                                                     'চিকিৎসাসেবা—আমার '
                                                                                                                                     'তৈরি '
                                                                                                                                     'কিছু '
                                                                                                                                     'প্রজেক্ট।',
 'Relocation to Germany': 'জার্মানিতে স্থানান্তর',
 'Responsibilities and backend work delivered across product teams.': 'বিভিন্ন product team-এ পালন '
                                                                      'করা দায়িত্ব ও backend কাজ।',
 'Role-aware Django API for clinic operations.': 'Clinic পরিচালনার জন্য role অনুযায়ী access-সহ '
                                                 'Django API।',
 'Role-aware Django property marketplace.': 'Role অনুযায়ী access-সহ Django property marketplace।',
 'STATUS': 'অবস্থা',
 'Secure backend systems': 'নিরাপদ backend system',
 'Skills are grouped by the part of a backend system they support. I only list tools I am prepared to discuss technically.': 'Backend '
                                                                                                                             'system-এর '
                                                                                                                             'কোন '
                                                                                                                             'কাজে '
                                                                                                                             'ব্যবহার '
                                                                                                                             'হয় '
                                                                                                                             'সেই '
                                                                                                                             'অনুযায়ী '
                                                                                                                             'দক্ষতাগুলো '
                                                                                                                             'সাজানো। '
                                                                                                                             'যে '
                                                                                                                             'tools '
                                                                                                                             'নিয়ে '
                                                                                                                             'প্রযুক্তিগত '
                                                                                                                             'আলোচনা '
                                                                                                                             'করতে '
                                                                                                                             'প্রস্তুত, '
                                                                                                                             'সেগুলোই '
                                                                                                                             'এখানে '
                                                                                                                             'রেখেছি।',
 'Source reference': 'সোর্স রেফারেন্স',
 'Structured, connected data': 'কাঠামোবদ্ধ ও সম্পর্কযুক্ত তথ্য',
 'Student attendance — session-aware marking in the demo workspace.': 'শিক্ষার্থীর হাজিরা — demo '
                                                                      'workspace-এ session অনুযায়ী '
                                                                      'marking।',
 'Student directory — demo records, search and class filters.': 'শিক্ষার্থী তালিকা — demo records, '
                                                                'search ও class filter।',
 'Technical skills.': 'প্রযুক্তিগত দক্ষতা।',
 'The starting point': 'শুরুর ধাপ',
 'Web & mobile clients': 'ওয়েব ও মোবাইল client',
 'Your message was saved. Thank you!': 'আপনার বার্তা সংরক্ষিত হয়েছে। ধন্যবাদ!',
 'your next role.': 'আপনার পরবর্তী সুযোগ নিয়ে।'})

@register.filter(name='translate')
def translate(value, language):
    return TRANSLATIONS.get(str(value), value) if language == 'bn' else value


@register.simple_tag(takes_context=True)
def bilingual(context, english, bangla):
    return bangla if context.get('portfolio_language') == 'bn' and bangla else english
