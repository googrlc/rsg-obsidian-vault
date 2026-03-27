You are building a CRM schema inside EspoCRM for Risk Solutions Group (RSG), 
a two-person independent insurance agency. You will create three entities, 
configure list views, and build a custom Intel tab on the Account entity.
All work is done via the EspoCRM Admin panel or direct database/config file 
manipulation. Follow these instructions exactly.

---

## STEP 1 — CREATE CUSTOM FIELDS ON THE ACCOUNT ENTITY

Navigate to: Admin → Entity Manager → Account → Fields

Create the following fields. All intel fields must be prefixed intel_ or insight_.

---

### GROUP 1: Account Classification

Field name: account_type
Type: Enum
Options: Prospect, Commercial, Personal
Required: true
Default: Prospect

Field name: lob
Type: Multi-Enum
Options: Commercial Auto, GL, Workers Comp, Cargo, Home, Auto, Life, Medicare, BOP
Required: false

Field name: x_date
Type: Date
Required: false

Field name: estimated_premium
Type: Currency
Required: false

Field name: annual_premium
Type: Currency
Required: false

Field name: renewal_date
Type: Date
Required: false

Field name: carrier
Type: Varchar
Max length: 100
Required: false

Field name: account_status
Type: Enum
Options: Active, Urgent, Renewing, At Risk, Inactive
Default: Active
Required: false

Field name: stage
Type: Enum
Options: New, Qualified, Proposal, Negotiation, Closed Won, Closed Lost
Required: false

---

### GROUP 2: Intel Meta

Field name: intel_run
Type: Bool
Default: false

Field name: intel_run_date
Type: DateTime

Field name: intel_run_by
Type: Varchar
Max length: 100

Field name: intel_sources_hit
Type: Int

Field name: intel_confidence
Type: Enum
Options: High, Medium, Low

---

### GROUP 3: AI Output

Field name: intel_ai_summary
Type: Text

Field name: intel_pain_points
Type: Text

Field name: intel_cross_sell
Type: Text

Field name: intel_growth_indicator
Type: Text

---

### GROUP 4: Insights

Field name: insight_signal
Type: Text

Field name: insight_objection
Type: Text

Field name: insight_opener
Type: Text

Field name: insight_relationship
Type: Text

---

### GROUP 5: Company Profile

Field name: intel_legal_name
Type: Varchar
Max length: 200

Field name: intel_dba
Type: Varchar
Max length: 200

Field name: intel_naics
Type: Varchar
Max length: 100

Field name: intel_sic
Type: Varchar
Max length: 20

Field name: intel_entity_type
Type: Enum
Options: LLC, Corp, Sole Prop, Partnership, Other

Field name: intel_years_in_business
Type: Int

Field name: intel_employee_count
Type: Int

Field name: intel_annual_revenue_est
Type: Varchar
Max length: 100

Field name: intel_website
Type: Url

Field name: intel_linkedin_url
Type: Url

Field name: intel_bbb_rating
Type: Varchar
Max length: 10

Field name: intel_bbb_accredited
Type: Bool

Field name: intel_bbb_complaints
Type: Int

---

### GROUP 6: Fleet / Risk — Conditional Fields

Field name: intel_fleet_size
Type: Int

Field name: intel_operating_radius
Type: Varchar
Max length: 200

Field name: intel_cargo_type
Type: Varchar
Max length: 200

Field name: intel_owner_operators
Type: Bool

Field name: intel_dot_incidents
Type: Int

Field name: intel_osha_violations
Type: Text

---

### GROUP 7: Raw Research Notes

Field name: intel_website_notes
Type: Text

Field name: intel_news_notes
Type: Text

Field name: intel_linkedin_notes
Type: Text

Field name: intel_bbb_notes
Type: Text

Field name: intel_signal_news
Type: Text

Field name: intel_signal_linkedin
Type: Text

---


---

## STEP 2 — CREATE THE ACTIVITY LOG ENTITY

Entity name: RsgActivity
Type: Base
Label: Activity Log

Create the following fields:

Field name: account
Type: Link
Link to: Account
Required: true

Field name: activity_type
Type: Enum
Options: Call, Email, Note, Intel Run, Renewal Outreach

Field name: description
Type: Text

Field name: created_by
Type: Link
Link to: Users

---

## STEP 3 — CONFIGURE THE INTEL TAB ON ACCOUNT DETAIL VIEW

Navigate to: Admin → Entity Manager → Account → Layouts → Detail View

Add a new panel named "Intelligence" with the following configuration:

Position this panel AFTER the default panels, not before.

Panel: Intelligence
Tab label: Intelligence

Arrange fields inside the Intelligence panel in these sub-sections:

Sub-section: Run Status
Row 1: intel_run, intel_run_date
Row 2: intel_confidence, intel_sources_hit
Row 3: intel_run_by

Sub-section: AI Summary
Row 1: intel_ai_summary (full width)

Sub-section: Insights
Row 1: insight_opener (full width)
Row 2: insight_signal (full width)
Row 3: insight_objection (full width)
Row 4: insight_relationship (full width)

Sub-section: AI Output
Row 1: intel_pain_points (full width)
Row 2: intel_cross_sell, intel_growth_indicator

Sub-section: Company Profile
Row 1: intel_legal_name, intel_dba
Row 2: intel_naics, intel_sic
Row 3: intel_entity_type, intel_years_in_business
Row 4: intel_employee_count, intel_annual_revenue_est
Row 5: intel_website, intel_linkedin_url
Row 6: intel_bbb_rating, intel_bbb_accredited
Row 7: intel_bbb_complaints

Sub-section: Fleet & Risk Details
Row 1: intel_fleet_size, intel_operating_radius
Row 2: intel_cargo_type, intel_owner_operators
Row 3: intel_dot_incidents
Row 4: intel_osha_violations (full width)
Row 5: intel_underwriting_flag (full width)

Sub-section: Raw Research Notes
Row 1: intel_website_notes (full width)
Row 2: intel_news_notes (full width)
Row 3: intel_linkedin_notes (full width)
Row 4: intel_bbb_notes (full width)

---

## STEP 4 — CONFIGURE CONDITIONAL FIELD VISIBILITY

Navigate to: Admin → Entity Manager → Account → Layouts → Detail View

Apply the following dynamic logic to the Intelligence panel.
EspoCRM handles this via the Dynamic Logic feature on each field.

intel_fleet_size:
  Visible if: lob contains "Commercial Auto" OR lob contains "Cargo"

intel_operating_radius:
  Visible if: lob contains "Commercial Auto" OR lob contains "Cargo"

intel_cargo_type:
  Visible if: lob contains "Cargo"

intel_owner_operators:
  Visible if: lob contains "Commercial Auto"

intel_dot_incidents:
  Visible if: lob contains "Commercial Auto"

intel_osha_violations:
  Visible always — no condition

---

## STEP 5 — CREATE THREE FILTERED LIST VIEWS

Navigate to: Admin → Entity Manager → Account → Layouts → List View

Create three saved search filters using the Search & Filter panel.

Filter 1:
  Name: Prospects
  Condition: account_type = Prospect
  Columns: account_name, lob, stage, x_date, estimated_premium, 
            intel_run, intel_confidence, assigned_user

Filter 2:
  Name: Commercial Lines
  Condition: account_type = Commercial
  Columns: account_name, lob, renewal_date, annual_premium, 
            carrier, account_status, assigned_user

Filter 3:
  Name: Personal Lines
  Condition: account_type = Personal
  Columns: account_name, lob, renewal_date, annual_premium, 
            carrier, account_status, assigned_user

Pin all three filters to the left navigation sidebar as separate links.

---

## STEP 6 — CREATE THE INTEL PACK MANUAL WORKFLOW TRIGGER

Navigate to: Admin → Workflows → Create Workflow

Workflow name: Run Intel Pack
Entity: Account
Trigger type: Manual (button on record)
Condition: account_type = Prospect

Action:
  Type: Send HTTP Request
  Method: POST
  URL: {YOUR_N8N_WEBHOOK_URL}
  Headers:
    Content-Type: application/json
  Body:
    {
      "record_id": "{id}",
      "company_name": "{name}",
      "lob": "{lob}",
      "contact_name": "{contact_name}",
      "website": "{intel_website}",
      "x_date": "{x_date}"
    }

This creates the "Run Intel Pack" button on every Prospect record.
The button does not appear on Commercial or Personal account types.

---

## STEP 7 — CONFIGURE N8N WRITE-BACK VIA ESPOCRM REST API

When n8n completes the Intel Pack run it must PATCH the Account record.

Endpoint: PATCH /api/v1/Account/{record_id}

Payload must map exactly to the field names created in Step 1.
All intel_ and insight_ fields are writable via the standard REST API.

After successful PATCH, n8n must also:
1. Set intel_run = true
2. Set intel_run_date = current UTC datetime
3. Set intel_confidence = value from LLM output
4. Set intel_sources_hit = integer count of sources that returned data

---

## VALIDATION CHECKLIST

Before marking the build complete, verify:

[ ] All 43 fields exist on the Account entity
[ ] Policy entity created with 8 fields
[ ] RsgActivity entity created with 5 fields
[ ] Intelligence panel appears as a tab on Account detail view
[ ] Five conditional fields show/hide correctly based on lob value
[ ] Three list view filters work and are pinned to sidebar


---

Here's the schema for everything on that tab. All intel fields — none of them touch the main account view.
![[Pasted image 20260325194700.png]]
