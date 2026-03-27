### 1. `knowledge_chunks` — RAG/semantic search store

|Column|Type|Notes|
|---|---|---|
|`id`|uuid|PK, auto-generated|
|`content`|text|Required|
|`embedding`|vector(1536)|For OpenAI embeddings|
|`source_url`|text|Nullable|
|`source_title`|text|Nullable|
|`domain`|text|Required — `agency`, `ministry`, `personal`, `carrier`, `lob`|
|`doc_type`|text|Nullable|
|`tags`|text[]|Nullable|
|`created_at`|timestamptz|Default `now()`|
|`updated_at`|timestamptz|Default `now()`|

**Function:** `match_chunks(query_embedding, match_domain, match_threshold, match_count)` — semantic similarity search

---

### 2. `documents` — Ingested document tracker

|Column|Type|Notes|
|---|---|---|
|`id`|uuid|PK, auto-generated|
|`title`|text|Required|
|`source_url`|text|Nullable|
|`source_type`|text|`google_drive`, `upload`, `url`, `manual`|
|`domain`|text|Required — same enum as knowledge_chunks|
|`doc_type`|text|Nullable|
|`chunk_count`|integer|Default `0`|
|`last_ingested_at`|timestamptz|Nullable|
|`created_at`|timestamptz|Default `now()`|

---

###3. `commission_rules` — LOB rate definitions (10 rows seeded)

| Column            | Type          | Notes                                     |     |
| ----------------- | ------------- | ----------------------------------------- | --- |
| `id`              | uuid          | PK, auto-generated                        |     |
| `lob`             | text          | Required                                  |     |
| `carrier`         | text          | Nullable (for carrier-specific overrides) |     |
| `commission_rate` | numeric(5,4)  | Required                                  |     |
| `lamar_split`     | numeric(5,4)  | Default `1.0`                             |     |
| `referral_split`  | numeric(5,4)  | Default `0.0`                             |     |
| `min_premium`     | numeric(10,2) | Nullable                                  |     |
| `max_premium`     | numeric(10,2) | Nullable                                  |     |
| `notes`           | text          | Nullable                                  |     |
| `active`          | boolean       | Default `true`                            |     |
| `created_at`      | timestamptz   | Default `now()`                           |     |
| `updated_at`      | timestamptz   | Default `now()`                           |     |

---

### 4. `commission_ledger` — Actual bound policy commissions

|Column|Type|Notes|
|---|---|---|
|`id`|uuid|PK, auto-generated|
|`espocrm_opportunity_id`|text|Unique, nullable — links to EspoCRM|
|`client_name`|text|Required|
|`lob`|text|Required|
|`carrier`|text|Nullable|
|`policy_number`|text|Nullable|
|`annual_premium`|numeric(10,2)|Required|
|`commission_rate`|numeric(5,4)|Required|
|`gross_commission`|numeric(10,2)|**Generated:** `premium × rate`|
|`lamar_split`|numeric(5,4)|Default `1.0`|
|`lamar_commission`|numeric(10,2)|**Generated:** `premium × rate × lamar_split`|
|`referral_split`|numeric(5,4)|Default `0.0`|
|`referral_commission`|numeric(10,2)|**Generated:** `premium × rate × referral_split`|
|`effective_date`|date|Nullable|
|`bound_date`|date|Nullable|
|`commission_logged_at`|timestamptz|Default `now()`|
|`notes`|text|Nullable|

**View:** `commission_ytd` — YTD summary grouped by LOB

---

### 5. `carrier_appetite` — Carrier/LOB matching

|Column|Type|Notes|
|---|---|---|
|`id`|uuid|PK, auto-generated|
|`carrier_name`|text|Required|
|`lob`|text|Required|
|`appetite_level`|text|`preferred`, `standard`, `non-standard`, `declined`|
|`min_premium`|numeric(10,2)|Nullable|
|`max_premium`|numeric(10,2)|Nullable|
|`states_approved`|text[]|Nullable|
|`key_requirements`|text[]|Nullable|
|`exclusions`|text[]|Nullable|
|`notes`|text|Nullable|
|`effective_date`|date|Nullable|
|`active`|boolean|Default `true`|
|`created_at`|timestamptz|Default `now()`|
|`updated_at`|timestamptz|Default `now()`|

**Function:** `find_carriers(p_lob, p_state, p_appetite)` — lookup carriers by LOB/state/appetite level