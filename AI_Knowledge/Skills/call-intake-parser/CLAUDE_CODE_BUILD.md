# Claude Code Build Instructions
# RSG Commercial Client Intake Parser
# Run this file in Claude Code from the project root

## What to Build

A production-ready Python service that:
1. Accepts a call transcript (text file or raw string)
2. Parses it via Anthropic Claude API into structured intake JSON
3. Writes Account + Opportunity + Tasks to EspoCRM via REST API
4. Generates a branded RSG PDF intake report via ReportLab
5. Posts a summary alert to Slack #lamar-alerts
6. Returns a success/failure JSON response

---

## Project Structure to Create

```
rsg-intake-parser/
├── main.py                  # CLI entry point + FastAPI app
├── parser.py                # Claude API transcript parser
├── crm_writer.py            # EspoCRM API writer
├── pdf_generator.py         # ReportLab PDF report builder
├── slack_notifier.py        # Slack alert sender
├── schema.py                # Pydantic models for all intake fields
├── config.py                # Environment config (reads from .env)
├── requirements.txt         # All dependencies
├── .env.example             # Environment variable template
├── tests/
│   ├── test_parser.py       # Unit tests for transcript parsing
│   ├── test_crm_writer.py   # Unit tests for CRM writes
│   └── sample_transcript.txt # Sample intake call transcript for testing
└── README.md                # Setup and usage instructions
```

---

## Environment Variables Required (.env)

```
ANTHROPIC_API_KEY=           # Claude API key
ESPOCRM_BASE_URL=https://rrespocrm-rsg-u69864.vm.elestio.app/api/v1
ESPOCRM_API_KEY=             # EspoCRM API key
ESPOCRM_LAMAR_USER_ID=       # Lamar's EspoCRM user ID
SLACK_BOT_TOKEN=             # Slack bot token
SLACK_CHANNEL_ID=C0ANQUENX4P # #lamar-alerts channel
OUTPUT_DIR=./output          # Where PDFs are saved
```

---

## schema.py — Pydantic Models

Build Pydantic v2 models matching this exact JSON structure (used for
Claude API response validation AND EspoCRM payload construction):

```python
class BusinessIdentity(BaseModel):
    legal_name: Optional[str]
    dba: Optional[str]
    entity_type: Optional[str]  # LLC, Corp, S-Corp, Sole Prop, Partnership
    fein: Optional[str]
    date_established: Optional[str]
    state_of_formation: Optional[str]
    naics_code: Optional[str]
    sic_code: Optional[str]
    prior_non_renewal: Optional[bool]
    sos_status: Optional[str]

class Location(BaseModel):
    mailing_address: Optional[str]
    operating_locations: List[str] = []
    owned_or_leased: Optional[str]
    sq_footage: Optional[int]
    year_built: Optional[int]
    construction_type: Optional[str]
    flood_zone: Optional[str]
    building_value: Optional[float]
    bpp_value: Optional[float]
    sprinkler: Optional[bool]
    security_system: Optional[bool]

class KeyPeople(BaseModel):
    owners: List[dict] = []  # [{name, ownership_pct, role}]
    primary_contact_name: Optional[str]
    primary_contact_email: Optional[str]
    primary_contact_phone: Optional[str]
    licenses: List[str] = []

class Financials(BaseModel):
    annual_revenue_current: Optional[float]
    annual_revenue_prior_1: Optional[float]
    annual_revenue_prior_2: Optional[float]
    annual_payroll_current: Optional[float]
    employees_ft: Optional[int]
    employees_pt: Optional[int]
    employees_seasonal: Optional[int]
    subcontractor_spend: Optional[float]
    subs_insured: Optional[bool]

class Operations(BaseModel):
    description: Optional[str]
    multi_state: Optional[bool]
    alcohol_pct: Optional[float]
    vehicles_in_ops: Optional[bool]
    sells_products: Optional[bool]
    professional_advice: Optional[bool]
    stores_pii: Optional[bool]
    government_contracts: Optional[bool]

class RecentUpdates(BaseModel):
    ownership_change: Optional[bool]
    new_locations: Optional[bool]
    new_vehicles: Optional[bool]
    pending_claims: Optional[bool]
    carrier_notices: Optional[bool]
    operations_change: Optional[bool]

class ExistingCoverage(BaseModel):
    carriers: List[str] = []
    policy_numbers: List[str] = []
    expiration_dates: List[str] = []
    current_premiums: List[float] = []
    loss_runs_received: Optional[bool]
    umbrella_in_place: Optional[bool]
    umbrella_limit: Optional[float]
    prior_non_renewal_reason: Optional[str]

class AutoInfo(BaseModel):
    vehicles: List[dict] = []
    drivers: List[dict] = []
    radius: Optional[str]
    dot_number: Optional[str]
    hnoa_exposure: Optional[bool]

class IntakeResult(BaseModel):
    business_identity: BusinessIdentity = BusinessIdentity()
    location: Location = Location()
    key_people: KeyPeople = KeyPeople()
    financials: Financials = Financials()
    operations: Operations = Operations()
    recent_updates: RecentUpdates = RecentUpdates()
    existing_coverage: ExistingCoverage = ExistingCoverage()
    auto: AutoInfo = AutoInfo()
    cross_sell_flags: List[str] = []
    missing_required_fields: List[str] = []
    submission_ready: bool = False
    ai_confidence: int = 0
    call_summary: Optional[str] = None
    next_actions: List[str] = []
```

---

## parser.py — Claude API Transcript Parser

- Use `anthropic` Python SDK (latest)
- Model: `claude-sonnet-4-6` 
- Max tokens: 4000
- System prompt: extract structured JSON from transcript
- Use the EXACT system prompt from SKILL.md in this directory
- Validate response with Pydantic IntakeResult model
- Compute `missing_required_fields` by checking these fields are not None:
  `legal_name, fein, entity_type, mailing_address, sq_footage, year_built,
   construction_type, annual_revenue_current, annual_payroll_current,
   employees_ft, description, carriers, expiration_dates, loss_runs_received`
- Compute `submission_ready`: True only if missing_required_fields is empty
  AND pending_claims is not True
- Set `ai_confidence` based on: (non-null fields / total fields) * 100

---

## crm_writer.py — EspoCRM Writer

Use `httpx` for all HTTP calls (async-capable).

### write_account(intake: IntakeResult, client_name: str) -> str
- GET /Account?where[0][type]=contains&where[0][attribute]=name&where[0][value]={name}
- If found: PATCH /Account/{id} with updated fields → return existing id
- If not found: POST /Account with all available fields → return new id
- Map fields:
  - name → legal_name or client_name
  - type → "Prospect" for new, "Customer" for existing
  - billingAddressStreet → mailing_address
  - numberOfEmployees → employees_ft
  - annualRevenue → annual_revenue_current
  - description → operations.description
  - industry → naics_code

### write_opportunity(intake: IntakeResult, account_id: str, call_date: str) -> str
- POST /Opportunity
- name: "{client_name} — Intake {call_date}"
- accountId: account_id
- stage: "Intake / Qualifying"
- closeDate: 30 days from today
- description: call_summary + confidence score

### write_tasks(missing_fields: List[str], xsell: List[str], account_id: str, opp_id: str)
- For each missing field: POST /Task with name "MISSING: {field}", priority High,
  status "Inbox", due in 3 days, linked to Opportunity
- For each cross-sell flag: POST /Task with name "CROSS-SELL: {flag}", priority Normal,
  status "Inbox", due in 14 days, linked to Account

---

## pdf_generator.py — ReportLab PDF

Use the full generate_intake_pdf.py already written at this path:
  /Users/lamarcoates/Documents/GitHub/rsg-obsidian-vault/AI_Knowledge/Skills/call-intake-parser/generate_intake_pdf.py

Copy that file's content into pdf_generator.py as the base.
Refactor the generate_report() function to accept an IntakeResult Pydantic
object instead of a raw dict. Keep all RSG branding, colors, and layout.
Add page numbers to footer: "Page X of Y"
Add a QR code linking to the EspoCRM account record (use qrcode library).

---

## slack_notifier.py — Slack Alerts

Use `slack_sdk` Python library.

### send_intake_alert(intake: IntakeResult, client_name: str, call_date: str,
                      account_id: str, opp_id: str, pdf_path: str)

Post to SLACK_CHANNEL_ID with Block Kit formatting:

Header block: "🗂 NEW INTAKE: {client_name}"
Section fields:
  - Call date / type
  - AI Confidence: {score}%
  - Missing required fields: {count}
  - Submission ready: ✅ YES / ❌ NO
Cross-sell flags as bullet list (if any)
Next actions as numbered list (first 3 only)
Button: "View in CRM" → EspoCRM account URL
Footer: "Generated by RSG OpenClaw"

---

## main.py — CLI + FastAPI

### CLI usage:
```bash
python main.py --transcript call.txt --client "Exquisite Delites Inc" --date 2026-04-01 --type new_prospect
```

### FastAPI endpoint (for n8n webhook):
```
POST /intake
Body: {transcript, client_name, call_date, call_type, called_by}
Returns: {status, account_id, opp_id, missing_count, pdf_path, confidence}
```

Run with: `uvicorn main:app --host 0.0.0.0 --port 8000`

---

## tests/sample_transcript.txt

Create a realistic sample transcript for a fictional catering company
("Peachtree Catering LLC") covering:
- Owner name and contact info
- Business address in Atlanta
- 8 employees (6 FT, 2 PT)
- Annual revenue ~$480,000
- Vehicles used for delivery
- No current umbrella policy
- Hartford BOP expiring in 3 months
- One fire claim 2 years ago (neighbor's fault)
- Mentions serving wine at events (~10% of revenue)
This transcript should intentionally be missing: sq_footage, year_built,
annual_payroll, subcontractor info — so the missing fields logic gets tested.

---

## requirements.txt

```
anthropic>=0.40.0
httpx>=0.27.0
pydantic>=2.0.0
reportlab>=4.0.0
slack_sdk>=3.27.0
qrcode>=7.4.2
Pillow>=10.0.0
fastapi>=0.110.0
uvicorn>=0.29.0
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```

---

## Build Instructions for Claude Code

1. Create the project directory at:
   `/Users/lamarcoates/Documents/rsg-intake-parser/`

2. Create all files listed in the project structure above

3. Install all dependencies:
   `pip3 install -r requirements.txt`

4. Run the test suite against the sample transcript:
   `pytest tests/ -v`

5. Generate a sample PDF using the sample transcript:
   `python main.py --transcript tests/sample_transcript.txt --client "Peachtree Catering LLC" --date 2026-04-01 --type new_prospect --dry-run`
   (dry-run skips CRM write and Slack, just generates the PDF)

6. Confirm PDF opens correctly and all sections render

7. Report back: file paths created, test results, any errors

---

## Important Notes for Claude Code

- DO NOT hardcode any API keys — read everything from .env
- DO NOT write to EspoCRM during tests — use --dry-run flag
- The EspoCRM API key is in 1Password at: op://RSG/EspoCRM API Key/credential
- The Anthropic API key is in 1Password at: op://RSG/Anthropic API Key/credential
- If reportlab is not installed, install it: pip3 install reportlab
- If any import fails, fix the dependency and retry
- Keep all output PDFs in ./output/ directory
- After successful build, print a summary of all files created and test results
