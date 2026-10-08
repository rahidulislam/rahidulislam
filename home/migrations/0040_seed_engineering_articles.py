from django.db import migrations

ARTICLES = [{'body': 'The portfolio contact form validates a Django ModelForm, saves a Contact record, then '
          'attempts an email notification. Persistence comes first because email availability '
          'should not decide whether an enquiry is accepted.\n'
          '\n'
          'The notification function sets a delivery status of sent or failed. A failure leaves '
          'the enquiry available in the admin inbox, where a staff member can retry failed '
          'notifications. The email uses a configured sender and puts the visitor address in '
          'Reply-To instead of impersonating that address.\n'
          '\n'
          'The form also includes a honeypot and an IP-based submission limit. Both the original '
          'home POST and the dedicated contact route reuse the same form and request context. '
          'Neither field validation nor delivery failures should erase an accepted message.\n'
          '\n'
          'For this small application the email attempt has a short timeout and happens '
          'synchronously after saving. A larger service could use a durable queue to reduce '
          'request latency, with idempotency and delivery observation tested separately. Tests '
          'cover successful delivery, mail-server failure and saved-message state.',
  'body_bn': 'এই পোর্টফোলিওতে Django ModelForm যাচাই করে প্রথমে Contact record সংরক্ষণ করা হয়। '
             'এরপর ইমেইল notification পাঠানোর চেষ্টা করা হয়। মেইল সার্ভারের অবস্থা দিয়ে visitor-এর '
             'বার্তা গ্রহণের সিদ্ধান্ত নেওয়া উচিত নয়।\n'
             '\n'
             'Notification-এর ফল sent বা failed হিসেবে রাখা হয়। ব্যর্থ হলেও বার্তা admin inbox-এ '
             'থাকে এবং staff পুনরায় notification পাঠাতে পারেন। ইমেইলের sender configuration থেকে '
             'আসে; visitor-এর ঠিকানা Reply-To-তে থাকে।\n'
             '\n'
             'ফর্মে honeypot ও IP অনুযায়ী submission limit আছে। Home POST এবং আলাদা contact route '
             'একই form ব্যবহার করে। Validation ও notification-এর ব্যর্থতা আলাদাভাবে পরিচালিত হয়।\n'
             '\n'
             'এই ছোট application-এ সংরক্ষণের পর স্বল্প timeout দিয়ে সরাসরি email পাঠানোর চেষ্টা '
             'হয়। বড় service-এ durable queue ব্যবহার করে request-এর সময় কমানো যেতে পারে; সেখানে '
             'idempotency ও delivery observation আলাদাভাবে পরীক্ষা করতে হবে। Tests-এ সফল delivery, '
             'mail-server failure ও সংরক্ষিত বার্তার অবস্থা যাচাই করা হয়েছে.',
  'is_published': True,
  'published_at': '2026-10-08',
  'slug': 'django-contact-storage-before-email',
  'source_url': 'https://github.com/rahidulislam/rahidulislam',
  'summary': 'A contact form should keep a visitor’s message even when the mail server fails.',
  'summary_bn': 'মেইল সার্ভার ব্যর্থ হলেও যোগাযোগ ফর্মে পাঠানো বার্তা সংরক্ষিত থাকা উচিত।',
  'title': 'Persist the enquiry before sending email',
  'title_bn': 'ইমেইল পাঠানোর আগে বার্তা সংরক্ষণ করুন',
  'topic': 'Django · Reliability'},
 {'body': 'This portfolio uses admin-managed Project records alongside source-backed defaults. '
          'Defaults help a fresh installation show useful content, while a matching database '
          'record takes precedence. An unpublished managed project suppresses its default, so '
          'editorial decisions remain effective.\n'
          '\n'
          'The library normalizes both sources into project cards with a name, summary, work type '
          'and technology tags. Search, work-type filtering and technology filtering run against '
          'this combined catalog on the server. That makes direct URLs shareable and keeps '
          'filtering available without JavaScript.\n'
          '\n'
          'Backend, frontend and full-stack describe the contribution, not the product category. '
          'Technology tags can be edited in the admin; known defaults are used only when explicit '
          'tags are absent. Search terms and selected filters remain visible after submission, and '
          'Reset returns to the complete catalog.\n'
          '\n'
          'The important tests check combinations of filters, an empty result, managed overrides '
          'and hidden drafts. A green search-box test alone would not establish that every content '
          'source is included.',
  'body_bn': 'এই পোর্টফোলিওতে admin-managed Project record এবং source-backed defaults একসঙ্গে আছে। '
             'নতুন installation-এ defaults content দেখায়; একই নামের database record থাকলে সেটি '
             'অগ্রাধিকার পায়। Unpublished managed project থাকলে তার default-ও দেখানো হয় না।\n'
             '\n'
             'Library দুই source-কে একই project card-এ রূপান্তর করে। সেখানে নাম, summary, কাজের '
             'ধরন ও technology tags থাকে। Search এবং একাধিক filter এই সম্মিলিত catalog-এ server '
             'থেকে চলে। তাই URL share করা যায় এবং JavaScript ছাড়াও filtering কাজ করে।\n'
             '\n'
             'Backend, frontend ও full-stack দিয়ে কাজের অবদান বোঝানো হয়; এটি product category নয়। '
             'Admin থেকে technology tags পরিবর্তন করা যায়। ফর্ম submit করার পর search ও নির্বাচিত '
             'filter দৃশ্যমান থাকে; Reset সব প্রজেক্টে ফিরিয়ে নেয়।\n'
             '\n'
             'Tests-এ combined filters, empty result, managed overrides ও hidden drafts যাচাই করা '
             'প্রয়োজন। শুধু search box দেখা যাচ্ছে—এটি সব source অন্তর্ভুক্ত হওয়ার প্রমাণ নয়.',
  'is_published': True,
  'published_at': '2026-10-08',
  'slug': 'one-project-catalog-managed-and-fallback',
  'source_url': 'https://github.com/rahidulislam/rahidulislam',
  'summary': 'A shared project representation keeps search useful across database content and '
             'source-backed defaults.',
  'summary_bn': 'Database content ও source-backed defaults একই কাঠামোতে রাখলে সব প্রজেক্টে search '
                'কাজ করে।',
  'title': 'One searchable catalog for managed and fallback projects',
  'title_bn': 'Managed ও fallback প্রজেক্টের জন্য একই searchable catalog',
  'topic': 'Django · Content'},
 {'body': 'Ilmora is a React and TypeScript madrasha-management frontend. Its public site and '
          'workspace support Bangla and English. The management areas include admissions, '
          'students, attendance, fees, funds and administration.\n'
          '\n'
          'The delivered demo stores academic-session records in the browser and uploads in '
          'IndexedDB. Demo roles illustrate the interface; they are not server-enforced '
          'authentication. A typed service boundary and API adapter define the path toward Django '
          'integration without presenting the demo as an already connected backend.\n'
          '\n'
          'Session-scoped data lets users explore different academic years separately. Monetary '
          'values use integer paisa, and date-only values keep calendar dates distinct from '
          'timestamps. These choices improve consistency at the presentation and service '
          'boundary.\n'
          '\n'
          'The next server phase needs authenticated endpoints, server-side permissions, file '
          'handling and documented validation before API mode can be enabled. Frontend completion '
          'proves the delivered interface and demo workflows; it does not prove production '
          'payment, SMS or biometric integration.',
  'body_bn': 'Ilmora একটি React ও TypeScript দিয়ে তৈরি madrasha-management frontend। Public site ও '
             'management workspace বাংলা এবং ইংরেজি সমর্থন করে। এতে ভর্তি, শিক্ষার্থী, হাজিরা, ফি, '
             'ফান্ড ও প্রশাসনের কাজ রয়েছে।\n'
             '\n'
             'বর্তমান demo academic-session records browser-এ এবং uploads IndexedDB-তে রাখে। Demo '
             'role দিয়ে interface বোঝানো হয়; এটি server-enforced authentication নয়। Typed service '
             'boundary ও API adapter ভবিষ্যৎ Django integration-এর পথ নির্ধারণ করে।\n'
             '\n'
             'Session অনুযায়ী data আলাদা থাকায় বিভিন্ন academic year আলাদাভাবে দেখা যায়। অর্থের '
             'মান integer paisa হিসেবে রাখা হয়; date-only value দিয়ে calendar date ও timestamp '
             'আলাদা রাখা হয়।\n'
             '\n'
             'API mode চালুর আগে authenticated endpoints, server-side permissions, file handling ও '
             'validation implement করতে হবে। Frontend সম্পন্ন হওয়ার অর্থ interface ও demo '
             'workflows তৈরি হয়েছে; production payment, SMS বা biometric integration সম্পন্ন হওয়ার '
             'দাবি নয়.',
  'is_published': True,
  'published_at': '2026-10-08',
  'slug': 'ilmora-demo-and-api-boundary',
  'source_url': 'https://madrasha-backend.vercel.app/',
  'summary': 'Ilmora demonstrates complete management screens while keeping its current browser '
             'demo and planned server integration distinct.',
  'summary_bn': 'Ilmora-র management screens সম্পন্ন; বর্তমান browser demo ও পরিকল্পিত server '
                'integration-এর সীমা আলাদা।',
  'title': 'Keep demo persistence separate from the API contract',
  'title_bn': 'Demo persistence ও API contract আলাদা রাখুন',
  'topic': 'React · Integration'}]

def seed_articles(apps, schema_editor):
    Article = apps.get_model('home', 'Article')
    for article in ARTICLES:
        Article.objects.using(schema_editor.connection.alias).get_or_create(slug=article['slug'], defaults=article)

class Migration(migrations.Migration):
    dependencies = [('home', '0039_article_alter_contact_options_contact_created_at_and_more')]
    operations = [migrations.RunPython(seed_articles, migrations.RunPython.noop)]
