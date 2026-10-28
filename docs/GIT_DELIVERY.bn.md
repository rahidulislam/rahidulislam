# এক স্ক্রিপ্টে checks → commit → push → PR

`git-deliver.py` একটি সাধারণ Python স্ক্রিপ্ট। Django, React, Node বা অন্য
যেকোনো **GitHub repository**-তে ব্যবহার করা যাবে। প্রজেক্টভেদে শুধু base branch
ও validation commands কনফিগার করতে হবে। GitLab/Bitbucket-এর PR/MR API এতে নেই।

## ১. একবার কম্পিউটারে ইনস্টল করুন

প্রয়োজন: Python 3.10+, Git এবং GitHub CLI (`gh`)। আলাদা Python package লাগে না।
এই repository-এর root থেকে চালান:

```bash
mkdir -p "$HOME/.local/bin"
cp scripts/git-deliver.py "$HOME/.local/bin/git-deliver"
chmod +x "$HOME/.local/bin/git-deliver"
export PATH="$HOME/.local/bin:$PATH"

gh auth login
git-deliver --help
```

প্রতিটি নতুন terminal-এ PATH পেতে আপনার shell-এর startup file-এ এই লাইনটি যোগ করুন:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

কোম্পানির GitHub Enterprise হলে সেই host-এ `gh auth login --hostname HOST` করুন।
স্ক্রিপ্ট PR-এর repository নির্ধারণে কনফিগার করা remote URL ব্যবহার করে।

## ২. প্রতিটি প্রজেক্টে একবার সেটআপ করুন

প্রজেক্টের Git repository-তে গিয়ে:

```bash
cd /absolute/path/to/project
git-deliver --init --base dev
```

যেসব প্রজেক্টে সরাসরি `main`-এ feature PR যায়, সেখানে:

```bash
git-deliver --init --base main
```

এতে `.git-deliver.json` তৈরি হবে। বিদ্যমান ফাইল overwrite করবে না।
Django quality-gate script বা package.json-এর পরিচিত scripts থাকলে checks
প্রস্তাব করবে। **প্রথমবার ফাইলটি দেখে সঠিক commands নিশ্চিত করুন।**

আপনার portfolio-এর মতো Django প্রজেক্টের উদাহরণ:

```json
{
  "base": "dev",
  "remote": "origin",
  "checks": [
    ["python", "scripts/check_backend.py"]
  ]
}
```

Python environment আগে activate করুন। যে command Playwright বা অন্য development
dependencies ব্যবহার করে, সেগুলোও ইনস্টল থাকতে হবে। Git global user.name ও
user.email কনফিগার থাকতে হবে।

Node প্রজেক্টের উদাহরণ; scripts আপনার package.json-এ থাকতে হবে:

```json
{
  "base": "main",
  "remote": "origin",
  "checks": [
    ["npm", "run", "lint"],
    ["npm", "run", "typecheck"],
    ["npm", "run", "test", "--", "--run"],
    ["npm", "run", "build"]
  ]
}
```

উপরের `--run` Vitest-এর উদাহরণ; Jest বা অন্য runner-এর উপযুক্ত CI/non-watch
arguments ব্যবহার করুন। pnpm/yarn হলে command-এর প্রথম শব্দ বদলান।
Checks অবশ্যই argument array হবে; `&&`, pipes বা shell expansion চলে না।
প্রয়োজনে আলাদা check script লিখে সেটি চালান। Checks ফাঁকা থাকলে delivery থামবে।

নতুন config তৈরি করলে কাজ শুরুর আগে সেটি আপনার setup branch-এ review/commit
করুন, অথবা বর্তমান task-এর নির্বাচিত ফাইল হিসেবে অন্তর্ভুক্ত করুন।
`--start` নতুন branch তৈরির সময় clean worktree চায়।

## ৩. আমাকে বারবার নির্দেশ না দিতে AGENTS.md আপডেট করুন

এই প্রজেক্টে নির্দেশনাটি ইতিমধ্যে `AGENTS.md`-এ যুক্ত আছে। অন্য প্রজেক্টের
জন্য সেখানকার `Automatic Git delivery` অংশটি নতুন প্রজেক্টের `AGENTS.md`-এ যোগ করুন। বিদ্যমান নির্দেশনা না মুছে শেষদিকে যোগ করবেন। AGENTS.md না
থাকলে সেটি নতুন করে তৈরি করতে পারেন।

এতে পরবর্তী implementation task-এ assistant নিজে থেকেই checks, commit,
push ও PR তৈরি/আপডেট করবে। এই repository-তে `AGENTS.md`-এর নির্দেশনাটি পরবর্তী কাজেও প্রযোজ্য।
অন্য প্রজেক্টে একই আচরণ চাইলে ব্যবহারকারীর অনুমতি অনুযায়ী সেখানে নির্দেশনাটি
যুক্ত করুন। নির্দিষ্ট task-এ "push করবেন না" বললে সেটিই অগ্রাধিকার পাবে।

স্ক্রিপ্টটি নিজে background-এ চলে না। Assistant নির্দেশনা অনুযায়ী এটি চালাবে,
অথবা আপনি terminal থেকে চালাতে পারবেন।

## ৪. নিয়মিত ব্যবহার

নতুন কাজের **আগে**, clean checkout থেকে:

```bash
git-deliver --start feature-contact-validation
```

এটি সর্বশেষ base fetch করে `codex/feature-contact-validation` branch তৈরি করে।
বিদ্যমান task branch-এ কাজ চলতে থাকলে এই ধাপ আবার লাগবে না।
কাজ শেষ হলে আগে পরিবর্তন দেখে নিন:

```bash
git-deliver --plan
git diff
```

সুনির্দিষ্ট task files দিয়ে প্রকাশ করুন; paths repository root-এর তুলনায়:

```bash
git-deliver \
  --files apps/contacts/forms.py apps/contacts/tests/test_forms.py \
  --message "fix: preserve contact values after validation errors" \
  --title "Preserve contact form values after validation errors" \
  --body-file /tmp/contact-pr.md
```

`/tmp/contact-pr.md` আগে তৈরি করবেন: সমস্যা, পরিবর্তিত আচরণ ও validation লিখুন।
`--body-file` না দিলে commit subjects ও সত্যিই পাস করা checks থেকে basic
description তৈরি হয়। ভালো reviewer-facing description সরবরাহ করাই উত্তম।

সব পরিবর্তন একই task-এর হলে:

```bash
git-deliver --all --message "feat: add project search filters"
```

অথবা আগে নিজে নির্বাচিত ফাইল stage করে:

```bash
git add apps/contacts/forms.py
git-deliver --message "fix: validate contact subjects"
```

প্রজেক্টের বাইরে থেকেও ব্যবহার করতে পারবেন:

```bash
git-deliver --repo /absolute/path/to/project --plan
```

`--draft` দিলে নতুন PR draft হিসেবে তৈরি হবে। একই branch/base-এর open PR
থাকলে push সেটি আপডেট করবে; duplicate PR হবে না। বিদ্যমান PR-এর description
স্বয়ংক্রিয়ভাবে overwrite করে না; `--body-file` দিলে title/body আপডেট করে।

## ৫. ব্যর্থতা ও সুরক্ষা

- Protected branch বা PR-এর base branch থেকে feature delivery চলে না।
- Conflict বা চলমান merge/rebase থাকলে আগে সেগুলো শেষ করতে বলে।
- শুধু নির্বাচিত ফাইল বা আগে stage করা ফাইল commit হয়। অন্য nonignored কাজ
  থাকলে থামে; আলাদা worktree ব্যবহার করুন।
- Checks-এর আগে stage করে, তারপর যাচাই করে checks ফাইল/index বদলেছে কিনা।
  বদলালে নতুন অবস্থাটি review করে আবার চালাতে হবে।
- Checks ব্যর্থ হলে commit/push/PR হয় না। Staging অক্ষত থাকে।
- Commit হয়ে push বা PR creation ব্যর্থ হলে commit হারায় না; কারণ ঠিক করে
  একই command আবার চালাতে পারবেন।
- `.env`, private-key ফাইল এবং কিছু পরিচিত token pattern আটকায়। এটি পূর্ণাঙ্গ
  secret scanner নয়; diff review ও repository secret scanning চালু রাখুন।
- Force push, admin bypass, auto-merge, PR merge বা deploy করে না।
- Merge অনুমোদন আলাদা। History-sync PR-এর ক্ষেত্রে merge commit প্রয়োজন
  হতে পারে; squash/rebase দিয়ে ancestry sync ঠিক হয় না।
- Remote push rejection বা branch protection থাকলে তা অতিক্রম করবে না।
  Promotion-এর জন্য নিচের `--promote` command ব্যবহার করুন।

## ৬. স্ক্রিপ্টের tests

প্রজেক্টের root থেকে:

```bash
python3 -m unittest discover -s scripts -p test_git_deliver.py -v
```

Tests অস্থায়ী স্থানীয় Git repository ও fake `gh` ব্যবহার করে। আসল GitHub-এ
commit, push, PR বা merge করে না।

## এক কমান্ডে release promotion

```bash
python scripts/git-deliver.py --promote staging
```

এটি সর্বশেষ remote `dev` থেকে `staging`-এ PR তৈরি করে। একই PR খোলা থাকলে
সেটির লিংক দেয়। Branch বদলানো, নতুন commit, push, title বা description লেখা লাগে না।
স্থানীয় পরিবর্তন অক্ষত থাকে। PR-এর CI remote commit যাচাই করবে; এই mode-এ
স্থানীয় checks চালিয়ে remote commit যাচাই হয়েছে বলে দাবি করা হয় না।

Staging-এ merge ও যাচাই করার পরে production promotion:

```bash
python scripts/git-deliver.py --promote main
```

এটি `staging → main` PR তৈরি/পুনর্ব্যবহার করে। অনুমোদিত রুটগুলো config-এ থাকে:

```json
"promotions": {
  "staging": "dev",
  "main": "staging"
}
```

অন্য project-এ reuse করলে তার `.git-deliver.json`-এ এই mapping প্রয়োজন অনুযায়ী
যোগ করুন। Mapping না থাকলে promotion বন্ধ থাকবে। Content একই হলে নতুন PR
তৈরি হবে না। `--promote staging --plan` শুধু পরিকল্পনা দেখায়।
এই command নিজে merge, branch-history sync, protection bypass বা deploy করে না।
