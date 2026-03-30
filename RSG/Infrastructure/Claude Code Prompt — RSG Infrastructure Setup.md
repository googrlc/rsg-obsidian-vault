

Paste this entire prompt into Claude Code.

---

## PROMPT

You are setting up the RSG (Risk Solutions Group) infrastructure repository. This is a two-person insurance agency. You will:

1. Initialize a new GitHub repository called `rsg-infrastructure`
2. Set up Supabase CLI with migration files for 5 tables
3. Configure GitHub Actions to auto-deploy migrations to Supabase on push to main

---

## Step 1 — Initialize the repo

```
mkdir rsg-infrastructure
cd rsg-infrastructure
git init
git branch -M main
```

Create this folder structure:

```
rsg-infrastructure/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── supabase/
│   ├── config.toml
│   └── migrations/
│       ├── 20240001_knowledge_chunks.sql
│       ├── 20240002_documents.sql
│       ├── 20240003_commission_rules.sql
│       ├── 20240004_commission_ledger.sql
│       └── 20240005_carrier_appetite.sql
├── .gitignore
└── README.md
```

---

## Step 2 — Create migration files

### `20240001_knowledge_chunks.sql`

This is the vector brain. Every agent queries this table.

```sql
create extension if not exists vector;

create table if not exists knowledge_chunks (
  id uuid primary key default gen_random_uuid(),
  content text not null,
  embedding vector(1536),
  source_url text,
  source_title text,
  domain text not null check (domain in ('agency', 'ministry', 'personal', 'carrier', 'lob')),
  doc_type text,
  tags text[],
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists knowledge_chunks_embedding_idx
  on knowledge_chunks using ivfflat (embedding vector_cosine_ops)
  with (lists = 100);

create index if not exists knowledge_chunks_domain_idx
  on knowledge_chunks (domain);

-- Semantic search function
create or replace function match_chunks (
  query_embedding vector(1536),
  match_domain text default null,
  match_threshold float default 0.7,
  match_count int default 5
)
returns table (
  id uuid,
  content text,
  source_title text,
  domain text,
  tags text[],
  similarity float
)
language sql stable
as $$
  select
    kc.id,
    kc.content,
    kc.source_title,
    kc.domain,
    kc.tags,
    1 - (kc.embedding <=> query_embedding) as similarity
  from knowledge_chunks kc
  where
    (match_domain is null or kc.domain = match_domain)
    and 1 - (kc.embedding <=> query_embedding) > match_threshold
  order by kc.embedding <=> query_embedding
  limit match_count;
$$;
```

---

### `20240002_documents.sql`

Tracks every file that has been ingested into the knowledge engine.

```sql
create table if not exists documents (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  source_url text,
  source_type text check (source_type in ('google_drive', 'upload', 'url', 'manual')),
  domain text not null check (domain in ('agency', 'ministry', 'personal', 'carrier', 'lob')),
  doc_type text,
  chunk_count int default 0,
  last_ingested_at timestamptz,
  created_at timestamptz default now()
);

create index if not exists documents_domain_idx on documents (domain);
create index if not exists documents_source_type_idx on documents (source_type);
```

---

### `20240003_commission_rules.sql`

Replaces hardcoded commission logic in N8N. Rules live here, N8N looks them up.

```sql
create table if not exists commission_rules (
  id uuid primary key default gen_random_uuid(),
  lob text not null,
  carrier text,
  commission_rate numeric(5,4) not null,
  lamar_split numeric(5,4) not null default 1.0,
  referral_split numeric(5,4) default 0.0,
  min_premium numeric(10,2),
  max_premium numeric(10,2),
  notes text,
  active boolean default true,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Seed default RSG commission rules
insert into commission_rules (lob, commission_rate, lamar_split, notes) values
  ('Commercial Auto',   0.1200, 1.0, 'Standard commercial auto'),
  ('General Liability', 0.1500, 1.0, 'Standard GL'),
  ('Workers Comp',      0.1000, 1.0, 'Standard WC'),
  ('BOP',               0.1500, 1.0, 'Business Owners Policy'),
  ('Umbrella',          0.1500, 1.0, 'Commercial umbrella'),
  ('Personal Auto',     0.1200, 1.0, 'Personal lines auto'),
  ('Homeowners',        0.1500, 1.0, 'Personal lines HO'),
  ('Life Insurance',    0.5000, 1.0, 'First year life commission'),
  ('Medicare',          0.2000, 1.0, 'Medicare supplement'),
  ('Group Benefits',    0.0500, 1.0, 'Group health/benefits');
```

---

### `20240004_commission_ledger.sql`

Every commission record. One row per bound policy.

```sql
create table if not exists commission_ledger (
  id uuid primary key default gen_random_uuid(),
  espocrm_opportunity_id text unique,
  client_name text not null,
  lob text not null,
  carrier text,
  policy_number text,
  annual_premium numeric(10,2) not null,
  commission_rate numeric(5,4) not null,
  gross_commission numeric(10,2) generated always as (annual_premium * commission_rate) stored,
  lamar_split numeric(5,4) not null default 1.0,
  lamar_commission numeric(10,2) generated always as (annual_premium * commission_rate * lamar_split) stored,
  referral_split numeric(5,4) default 0.0,
  referral_commission numeric(10,2) generated always as (annual_premium * commission_rate * referral_split) stored,
  effective_date date,
  bound_date date,
  commission_logged_at timestamptz default now(),
  notes text
);

create index if not exists commission_ledger_lob_idx on commission_ledger (lob);
create index if not exists commission_ledger_bound_date_idx on commission_ledger (bound_date);

-- YTD summary view
create or replace view commission_ytd as
select
  lob,
  count(*) as policies_bound,
  sum(annual_premium) as total_premium,
  sum(lamar_commission) as total_commission
from commission_ledger
where date_trunc('year', bound_date) = date_trunc('year', current_date)
group by lob
order by total_commission desc;
```

---

### `20240005_carrier_appetite.sql`

Structured carrier appetite data. Paired with vector chunks in knowledge_chunks for semantic search.

```sql
create table if not exists carrier_appetite (
  id uuid primary key default gen_random_uuid(),
  carrier_name text not null,
  lob text not null,
  appetite_level text check (appetite_level in ('preferred', 'standard', 'non-standard', 'declined')),
  min_premium numeric(10,2),
  max_premium numeric(10,2),
  states_approved text[],
  key_requirements text[],
  exclusions text[],
  notes text,
  effective_date date,
  active boolean default true,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists carrier_appetite_lob_idx on carrier_appetite (lob);
create index if not exists carrier_appetite_carrier_idx on carrier_appetite (carrier_name);
create index if not exists carrier_appetite_appetite_idx on carrier_appetite (appetite_level);

-- Quick lookup function for N8N
create or replace function find_carriers (
  p_lob text,
  p_state text default null,
  p_appetite text[] default array['preferred', 'standard']
)
returns table (
  carrier_name text,
  appetite_level text,
  key_requirements text[],
  exclusions text[],
  notes text
)
language sql stable
as $$
  select
    carrier_name,
    appetite_level,
    key_requirements,
    exclusions,
    notes
  from carrier_appetite
  where
    lob = p_lob
    and active = true
    and appetite_level = any(p_appetite)
    and (p_state is null or p_state = any(states_approved))
  order by
    case appetite_level
      when 'preferred' then 1
      when 'standard' then 2
      when 'non-standard' then 3
      else 4
    end;
$$;
```

---

## Step 3 — GitHub Actions deploy workflow

### `.github/workflows/deploy.yml`

```yaml
name: Deploy Supabase Migrations

on:
  push:
    branches:
      - main
    paths:
      - 'supabase/migrations/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: supabase/setup-cli@v1
        with:
          version: latest

      - name: Deploy migrations
        run: supabase db push --linked
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
          SUPABASE_DB_PASSWORD: ${{ secrets.SUPABASE_DB_PASSWORD }}
          SUPABASE_PROJECT_ID: fekxkldrucwiorxriohx
```

---

## Step 4 — Supabase config

### `supabase/config.toml`

```toml
project_id = "fekxkldrucwiorxriohx"
```

---

## Step 5 — .gitignore

```
.env
.env.local
*.pem
.supabase/
```

---

## Step 6 — Push to GitHub and configure secrets

After Claude Code creates the repo and files:

1. Create repo on GitHub: `rsg-infrastructure` (private)
    
2. Run:
    
    ```
    git remote add origin https://github.com/YOUR_USERNAME/rsg-infrastructure.git
    git add .
    git commit -m "feat: initial RSG Supabase schema"
    git push -u origin main
    ```
    
3. Add these GitHub Secrets (Settings → Secrets → Actions):
    
    - `SUPABASE_ACCESS_TOKEN` → get from https://supabase.com/dashboard/account/tokens
    - `SUPABASE_DB_PASSWORD` → your Supabase project DB password
4. Push triggers GitHub Actions → migrations deploy automatically to Supabase project `fekxkldrucwiorxriohx`
    

---

## Verify it worked

Run this in Supabase SQL Editor:

```sql
select table_name from information_schema.tables
where table_schema = 'public'
order by table_name;
```

You should see: `carrier_appetite`, `commission_ledger`, `commission_rules`, `documents`, `knowledge_chunks`

Then test the vector search function:

```sql
select * from match_chunks(
  '[0.1, 0.2, ...]'::vector,  -- replace with real embedding
  'carrier',
  0.7,
  3
);
```