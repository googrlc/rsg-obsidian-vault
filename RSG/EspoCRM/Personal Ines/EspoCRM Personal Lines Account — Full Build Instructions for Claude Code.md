## 

```
You are building the Personal Lines Account layout inside EspoCRM for 
Risk Solutions Group (RSG). This is a separate layout configuration 
from the Commercial account. All work targets the Account entity with 
account_type = Personal.

Follow these instructions exactly and in order.

---

## STEP 1 — CREATE ALL CUSTOM FIELDS ON ACCOUNT ENTITY

Navigate to: Admin → Entity Manager → Account → Fields

All fields below are additions to the Account entity.
Do not remove any existing EspoCRM default fields.
Group fields exactly as labeled — this controls panel organization.

---

### GROUP 1: Account Classification
(These may already exist from the commercial build — skip if present)

account_type         Enum       Prospect, Commercial, Personal  Required, default: Personal
account_status       Enum       Active, Urgent, Renewing, At Risk, Inactive  Default: Active
assigned_user        Link       Relate to Users  Default: Gretchen
client_since         Date
referral_source      Enum       Referral, Google, Social Media, Cold Outreach, Walk-in, NowCerts Import, Other
referral_name        Varchar    Max: 100
preferred_contact    Enum       Phone, Email, Text
best_time_to_call    Varchar    Max: 100
do_not_contact       Bool       Default: false
communication_notes  Text

---

### GROUP 2: Household Profile

primary_first_name      Varchar    Max: 100   Required
primary_last_name       Varchar    Max: 100   Required
primary_dob             Date
primary_gender          Enum       Male, Female, Other, Prefer not to say
primary_occupation      Varchar    Max: 150
primary_phone           Phone
primary_email           Email
spouse_first_name       Varchar    Max: 100
spouse_last_name        Varchar    Max: 100
spouse_dob              Date
spouse_occupation       Varchar    Max: 150
dependents_count        Int
dependent_ages          Varchar    Max: 100
property_address        Varchar    Max: 200
property_city           Varchar    Max: 100
property_state          Varchar    Max: 50   Default: GA
property_zip            Varchar    Max: 10
mailing_address_same    Bool       Default: true
mailing_address         Varchar    Max: 200
residence_type          Enum       Owned, Rented, Condo, Mobile Home, Other
years_at_address        Int

---

### GROUP 3: Vehicle Inventory

vehicle_count            Int
vehicle_1_year           Int
vehicle_1_make           Varchar    Max: 50
vehicle_1_model          Varchar    Max: 50
vehicle_1_vin            Varchar    Max: 20
vehicle_1_use            Enum       Commute, Pleasure, Business, Rideshare
vehicle_1_annual_miles   Int
vehicle_1_ownership      Enum       Owned, Financed, Leased
vehicle_2_year           Int
vehicle_2_make           Varchar    Max: 50
vehicle_2_model          Varchar    Max: 50
vehicle_2_vin            Varchar    Max: 20
vehicle_2_use            Enum       Commute, Pleasure, Business, Rideshare
vehicle_2_annual_miles   Int
vehicle_2_ownership      Enum       Owned, Financed, Leased
vehicle_additional_notes Text
youthful_driver_flag     Bool       Default: false  Calculated by n8n
rideshare_driver_flag    Bool       Default: false

---

### GROUP 4: Driver Inventory

driver_count             Int
driver_1_name            Varchar    Max: 100
driver_1_dob             Date
driver_1_license_state   Varchar    Max: 50
driver_1_violations      Int
driver_1_accidents       Int
driver_2_name            Varchar    Max: 100
driver_2_dob             Date
driver_2_license_state   Varchar    Max: 50
driver_2_violations      Int
driver_2_accidents       Int
driver_additional_notes  Text
mvr_flag                 Bool       Default: false

---

### GROUP 5: Property Inventory

property_count            Int
home_year_built           Int
home_construction         Enum       Frame, Masonry, Mixed, Log, Other
home_square_footage       Int
home_dwelling_value       Currency
home_purchase_year        Int
home_roof_year            Int
home_roof_material        Enum       Asphalt Shingle, Metal, Tile, Wood Shake, Other
home_security_system      Bool       Default: false
home_alarm_monitored      Bool       Default: false
home_trampoline           Bool       Default: false
home_pool                 Bool       Default: false
home_dog                  Bool       Default: false
home_dog_breed            Varchar    Max: 100
rental_property_flag      Bool       Default: false
rental_property_count     Int
rental_property_notes     Text

---

### GROUP 6: Active Policies

policy_auto_active          Bool       Default: false
policy_auto_carrier         Varchar    Max: 100
policy_auto_number          Varchar    Max: 100
policy_auto_premium         Currency
policy_auto_effective       Date
policy_auto_expiration      Date
policy_auto_bi_limits       Varchar    Max: 50
policy_auto_comp_collision  Bool       Default: false
policy_auto_deductible      Varchar    Max: 50
policy_auto_um_uim          Bool       Default: false
policy_home_active          Bool       Default: false
policy_home_carrier         Varchar    Max: 100
policy_home_number          Varchar    Max: 100
policy_home_premium         Currency
policy_home_effective       Date
policy_home_expiration      Date
policy_home_dwelling_limit  Currency
policy_home_deductible      Varchar    Max: 50
policy_home_wind_hail_ded   Varchar    Max: 50
policy_renter_active        Bool       Default: false
policy_renter_carrier       Varchar    Max: 100
policy_renter_premium       Currency
policy_renter_expiration    Date
policy_umbrella_active      Bool       Default: false
policy_umbrella_carrier     Varchar    Max: 100
policy_umbrella_limit       Varchar    Max: 50
policy_umbrella_premium     Currency
policy_umbrella_expiration  Date
policy_life_active          Bool       Default: false
policy_life_carrier         Varchar    Max: 100
policy_life_type            Enum       Term, Whole, Universal, Final Expense
policy_life_face_value      Currency
policy_life_premium         Currency
policy_life_expiration      Date
policy_medicare_active      Bool       Default: false
policy_medicare_carrier     Varchar    Max: 100
policy_medicare_plan_type   Enum       Medicare Advantage, Medicare Supplement, PDP
policy_medicare_plan_name   Varchar    Max: 150
policy_medicare_premium     Currency
policy_medicare_effective   Date
policy_medicare_aep_flag    Bool       Default: false
total_annual_premium        Currency   Calculated by n8n — read only
policy_count_active         Int        Calculated by n8n — read only

---

### GROUP 7: Coverage Gaps

gap_umbrella            Bool       Calculated by n8n
gap_umbrella_reason     Text
gap_life                Bool       Calculated by n8n
gap_life_reason         Text
gap_life_need_est       Currency
gap_renters             Bool       Calculated by n8n
gap_auto_um             Bool       Calculated by n8n
gap_medicare            Bool       Calculated by n8n
gap_medicare_eligible   Date       Calculated from primary_dob — 65th birthday
gap_landlord            Bool       Calculated by n8n
gap_rideshare           Bool       Calculated by n8n
gap_final_expense       Bool       Calculated by n8n
gap_count               Int        Calculated by n8n — total true gap flags

---

### GROUP 8: Account Score

score_total              Int        0–100  Read only — calculated by n8n
score_tier               Enum       Strong, Good, At Risk, Critical  Read only
score_bundle_depth       Int        0–20
score_payment_history    Int        0–20
score_years_retained     Int        0–20
score_claims_activity    Int        0–20
score_last_contact       Int        0–20
score_last_calculated    DateTime
score_change_direction   Enum       Up, Down, Flat
score_change_amount      Int
score_alert_sent         Bool       Default: false

---

### GROUP 9: Renewal Tracking

next_renewal_date          Date       Calculated by n8n
next_renewal_lob           Varchar    Max: 50
next_renewal_carrier       Varchar    Max: 100
days_to_renewal            Int        Calculated daily by n8n
renewal_outreach_stage     Enum       Not Started, Day 60 Sent, Day 30 Sent, 
                                      Day 14 Sent, Confirmed, Shopped, Lost
renewal_quote_received     Bool       Default: false
renewal_quote_amount       Currency
renewal_quote_carrier      Varchar    Max: 100
renewal_quote_date         Date
renewal_decision           Enum       Renewing, Re-marketed, Lost — Price, 
                                      Lost — Service, Lost — Carrier, 
                                      Non-renewed by Carrier
renewal_decision_notes     Text
premium_change_amount      Currency
premium_change_pct         Decimal
rate_increase_flag         Bool       Default: false

---

### GROUP 10: Claims

claims_count_lifetime    Int
claims_count_3yr         Int
claims_open              Int
last_claim_date          Date
last_claim_lob           Enum       Auto, Home, Umbrella, Life, Medicare, Renters, Other
last_claim_type          Varchar    Max: 150
last_claim_status        Enum       Open, Closed, Subrogation
claims_notes             Text

---

### GROUP 11: Activity & Outreach

last_contact_date         Date       Auto-updated when RsgActivity logged
last_contact_type         Enum       Call, Email, Text, In Person
last_contact_by           Link       Relate to Users
last_contact_outcome      Enum       Reached, Voicemail, No Answer, 
                                     Email Opened, Unresponsive
outreach_attempts_current Int        Reset each renewal cycle by n8n
nps_score                 Int
nps_date                  Date
referrals_given           Int        Default: 0

---

## STEP 2 — CONFIGURE DYNAMIC LOGIC (CONDITIONAL FIELDS)

Navigate to: Admin → Entity Manager → Account → Fields
Set Dynamic Logic per field as follows:

mailing_address:
  Visible when: mailing_address_same = false

home_dog_breed:
  Visible when: home_dog = true

rental_property_count:
  Visible when: rental_property_flag = true

rental_property_notes:
  Visible when: rental_property_flag = true

vehicle_2_year:
  Visible when: vehicle_count >= 2

vehicle_2_make:
  Visible when: vehicle_count >= 2

vehicle_2_model:
  Visible when: vehicle_count >= 2

vehicle_2_vin:
  Visible when: vehicle_count >= 2

vehicle_2_use:
  Visible when: vehicle_count >= 2

vehicle_2_annual_miles:
  Visible when: vehicle_count >= 2

vehicle_2_ownership:
  Visible when: vehicle_count >= 2

policy_auto_carrier:
  Visible when: policy_auto_active = true

policy_auto_number:
  Visible when: policy_auto_active = true

policy_auto_premium:
  Visible when: policy_auto_active = true

policy_auto_effective:
  Visible when: policy_auto_active = true

policy_auto_expiration:
  Visible when: policy_auto_active = true

policy_auto_bi_limits:
  Visible when: policy_auto_active = true

policy_auto_comp_collision:
  Visible when: policy_auto_active = true

policy_auto_deductible:
  Visible when: policy_auto_active = true

policy_auto_um_uim:
  Visible when: policy_auto_active = true

policy_home_carrier:
  Visible when: policy_home_active = true

policy_home_number:
  Visible when: policy_home_active = true

policy_home_premium:
  Visible when: policy_home_active = true

policy_home_effective:
  Visible when: policy_home_active = true

policy_home_expiration:
  Visible when: policy_home_active = true

policy_home_dwelling_limit:
  Visible when: policy_home_active = true

policy_home_deductible:
  Visible when: policy_home_active = true

policy_home_wind_hail_ded:
  Visible when: policy_home_active = true

policy_renter_carrier:
  Visible when: policy_renter_active = true

policy_renter_premium:
  Visible when: policy_renter_active = true

policy_renter_expiration:
  Visible when: policy_renter_active = true

policy_umbrella_carrier:
  Visible when: policy_umbrella_active = true

policy_umbrella_limit:
  Visible when: policy_umbrella_active = true

policy_umbrella_premium:
  Visible when: policy_umbrella_active = true

policy_umbrella_expiration:
  Visible when: policy_umbrella_active = true

policy_life_carrier:
  Visible when: policy_life_active = true

policy_life_type:
  Visible when: policy_life_active = true

policy_life_face_value:
  Visible when: policy_life_active = true

policy_life_premium:
  Visible when: policy_life_active = true

policy_life_expiration:
  Visible when: policy_life_active = true

policy_medicare_carrier:
  Visible when: policy_medicare_active = true

policy_medicare_plan_type:
  Visible when: policy_medicare_active = true

policy_medicare_plan_name:
  Visible when: policy_medicare_active = true

policy_medicare_premium:
  Visible when: policy_medicare_active = true

policy_medicare_effective:
  Visible when: policy_medicare_active = true

gap_umbrella_reason:
  Visible when: gap_umbrella = true

gap_life_reason:
  Visible when: gap_life = true

gap_life_need_est:
  Visible when: gap_life = true

renewal_quote_amount:
  Visible when: renewal_quote_received = true

renewal_quote_carrier:
  Visible when: renewal_quote_received = true

renewal_quote_date:
  Visible when: renewal_quote_received = true

premium_change_amount:
  Visible when: renewal_decision is not empty

premium_change_pct:
  Visible when: renewal_decision is not empty

renewal_decision_notes:
  Visible when: renewal_decision is not empty

---

## STEP 3 — BUILD THE DETAIL VIEW LAYOUT

Navigate to: Admin → Entity Manager → Account → Layouts → Detail View

This layout applies only when account_type = Personal.
If EspoCRM supports layout-per-type, create a separate layout called
"Personal Lines". If not, all panels render on all accounts and
Gretchen learns to ignore commercial-irrelevant panels.

Tab order:
  Tab 1: Overview
  Tab 2: Policies
  Tab 3: Renewal
  Tab 4: Activity
  Tab 5: Documents

---

### TAB 1: Overview

Contains 5 panels stacked vertically in a two-column grid layout.
Left column: Account Score + Household Profile
Right column: Summary Stats + Active Policies Summary + Coverage Gaps

---

PANEL: Account score
Position: Left column, top
Collapsible: No

Layout:
  Row 1: score_total (label: "Score") | score_tier (label: "Tier")
  Row 2: score_change_direction (label: "Trend") | score_change_amount (label: "Change")
  Row 3: score_last_calculated (label: "Last calculated") — full width
  Divider
  Row 4: score_bundle_depth (label: "Bundle depth") | [score bar — 0-20]
  Row 5: score_payment_history (label: "Payment history") | [score bar — 0-20]
  Row 6: score_years_retained (label: "Years retained") | [score bar — 0-20]
  Row 7: score_claims_activity (label: "Claims activity") | [score bar — 0-20]
  Row 8: score_last_contact (label: "Last contact") | [score bar — 0-20]
  Divider
  Row 9: score_alert_sent (label: "Alert sent")

Note on score display:
  score_total renders as a large number (24px, bold)
  score_tier renders as a colored badge:
    Strong    → success green
    Good      → info blue
    At Risk   → warning amber
    Critical  → danger red

---

PANEL: Household profile
Position: Left column, below Account Score
Collapsible: Yes — default expanded

Layout:
  Row 1:  primary_first_name (label: "First name") | primary_last_name (label: "Last name")
  Row 2:  primary_dob (label: "Date of birth") | primary_gender (label: "Gender")
  Row 3:  primary_occupation (label: "Occupation") | primary_phone (label: "Phone")
  Row 4:  primary_email (label: "Email") — full width
  Divider — label: "Spouse"
  Row 5:  spouse_first_name (label: "First name") | spouse_last_name (label: "Last name")
  Row 6:  spouse_dob (label: "Date of birth") | spouse_occupation (label: "Occupation")
  Divider — label: "Household"
  Row 7:  dependents_count (label: "Dependents") | dependent_ages (label: "Ages")
  Row 8:  youthful_driver_flag (label: "Youthful driver") | rideshare_driver_flag (label: "Rideshare driver")
  Divider — label: "Address"
  Row 9:  property_address (label: "Street") — full width
  Row 10: property_city (label: "City") | property_state (label: "State")
  Row 11: property_zip (label: "ZIP") | residence_type (label: "Residence type")
  Row 12: years_at_address (label: "Years at address") | mailing_address_same (label: "Mailing same")
  Row 13: mailing_address (label: "Mailing address") — full width [CONDITIONAL]
  Divider — label: "Account"
  Row 14: client_since (label: "Client since") | referral_source (label: "Source")
  Row 15: referral_name (label: "Referred by") | preferred_contact (label: "Preferred contact")
  Row 16: best_time_to_call (label: "Best time") | do_not_contact (label: "Do not contact")
  Row 17: communication_notes (label: "Notes") — full width

---

PANEL: Summary stats
Position: Right column, top
Collapsible: No
Style: 2x2 stat card grid

Layout:
  Card 1: total_annual_premium (label: "Total annual premium")
  Card 2: next_renewal_date + days_to_renewal (label: "Next renewal")
  Card 3: claims_open (label: "Open claims")
  Card 4: gap_count (label: "Coverage gaps")

Color rules:
  days_to_renewal < 15   → render value in danger red
  days_to_renewal 15-30  → render value in warning amber
  days_to_renewal > 30   → render value in primary
  gap_count > 0          → render value in warning amber
  claims_open > 0        → render value in warning amber

---

PANEL: Active policies summary
Position: Right column, below summary stats
Collapsible: Yes — default expanded

Render one row per active policy (where policy_{lob}_active = true).
Each row contains:
  LOB label pill | Carrier | Policy number | Annual premium | Expiration date | Status badge

Status badge rules:
  expiration <= 15 days → Urgent (red)
  expiration 16-30 days → Renewing (amber)
  expiration > 30 days  → Active (green)

Rows to render (only if active Bool = true):
  Auto:      policy_auto_carrier, policy_auto_number, policy_auto_premium, policy_auto_expiration
  Home:      policy_home_carrier, policy_home_number, policy_home_premium, policy_home_expiration
  Renters:   policy_renter_carrier, [no number], policy_renter_premium, policy_renter_expiration
  Umbrella:  policy_umbrella_carrier, policy_umbrella_limit, policy_umbrella_premium, policy_umbrella_expiration
  Life:      policy_life_carrier, policy_life_type, policy_life_premium, policy_life_expiration
  Medicare:  policy_medicare_carrier, policy_medicare_plan_name, policy_medicare_premium, policy_medicare_effective

If no policies active: render "No active policies on record" in muted text.

---

PANEL: Coverage gaps
Position: Right column, below active policies
Collapsible: Yes — default expanded

Render one row per gap flag that is true.
Each row contains:
  Colored dot | LOB name | Reason text | "Prep pitch" button

Gap rows to render (only if gap Bool = true):
  gap_umbrella   → "Personal Umbrella"  → gap_umbrella_reason
  gap_life       → "Life Insurance"     → gap_life_reason + gap_life_need_est
  gap_renters    → "Renters Insurance"  → "Client is renting with no renters policy"
  gap_auto_um    → "UM/UIM Coverage"    → "Auto policy active but UM/UIM not carried"
  gap_medicare   → "Medicare"           → "Client approaching Medicare eligibility" + gap_medicare_eligible
  gap_landlord   → "Landlord Policy"    → "Rental property on record with no landlord coverage"
  gap_rideshare  → "Rideshare Endorsement" → "Rideshare driver with no endorsement on auto policy"
  gap_final_expense → "Final Expense"   → "Client age 70+ with no life or final expense coverage"

"Prep pitch" button fires sendPrompt in the UI:
  sendPrompt('Draft a renewal talking point for [gap LOB] for [client name]')

If gap_count = 0: render "No coverage gaps identified" in muted text.

---

### TAB 2: Policies

Full detail on every policy type.
Render all policy panels stacked vertically.
Each panel header contains the LOB name and an active/inactive badge.

---

PANEL: Personal auto
Collapsible: Yes
Header badge: Active (green) if policy_auto_active = true, else Inactive (gray)

Layout:
  Row 1:  policy_auto_active (label: "Active") | policy_auto_carrier (label: "Carrier")
  Row 2:  policy_auto_number (label: "Policy number") | policy_auto_premium (label: "Annual premium")
  Row 3:  policy_auto_effective (label: "Effective") | policy_auto_expiration (label: "Expiration")
  Row 4:  policy_auto_bi_limits (label: "BI/PD limits") | policy_auto_deductible (label: "Deductible")
  Row 5:  policy_auto_comp_collision (label: "Comp/collision") | policy_auto_um_uim (label: "UM/UIM")
  Divider — label: "Vehicles"
  Row 6:  vehicle_count (label: "Total vehicles")
  Row 7:  vehicle_1_year | vehicle_1_make | vehicle_1_model (label: "Vehicle 1")
  Row 8:  vehicle_1_vin (label: "VIN") | vehicle_1_use (label: "Use")
  Row 9:  vehicle_1_annual_miles (label: "Annual miles") | vehicle_1_ownership (label: "Ownership")
  Row 10: vehicle_2_year | vehicle_2_make | vehicle_2_model (label: "Vehicle 2") [CONDITIONAL]
  Row 11: vehicle_2_vin | vehicle_2_use [CONDITIONAL]
  Row 12: vehicle_2_annual_miles | vehicle_2_ownership [CONDITIONAL]
  Row 13: vehicle_additional_notes (label: "Additional vehicles") — full width
  Divider — label: "Drivers"
  Row 14: driver_count (label: "Total drivers")
  Row 15: driver_1_name (label: "Driver 1") | driver_1_dob
  Row 16: driver_1_license_state | driver_1_violations (label: "Violations") | driver_1_accidents (label: "Accidents")
  Row 17: driver_2_name (label: "Driver 2") | driver_2_dob
  Row 18: driver_2_license_state | driver_2_violations | driver_2_accidents
  Row 19: driver_additional_notes — full width
  Row 20: mvr_flag (label: "MVR flag") | youthful_driver_flag | rideshare_driver_flag

---

PANEL: Homeowners
Collapsible: Yes
Header badge: Active or Inactive

Layout:
  Row 1:  policy_home_active | policy_home_carrier
  Row 2:  policy_home_number | policy_home_premium
  Row 3:  policy_home_effective | policy_home_expiration
  Row 4:  policy_home_dwelling_limit (label: "Dwelling limit") | policy_home_deductible
  Row 5:  policy_home_wind_hail_ded (label: "Wind/hail deductible")
  Divider — label: "Property"
  Row 6:  home_year_built | home_construction
  Row 7:  home_square_footage | home_dwelling_value (label: "Replacement cost est.")
  Row 8:  home_purchase_year | home_roof_year (label: "Roof year")
  Row 9:  home_roof_material | home_security_system
  Row 10: home_alarm_monitored | home_trampoline
  Row 11: home_pool | home_dog
  Row 12: home_dog_breed [CONDITIONAL — visible if home_dog = true]
  Divider — label: "Additional properties"
  Row 13: rental_property_flag | rental_property_count [CONDITIONAL]
  Row 14: rental_property_notes [CONDITIONAL] — full width

---

PANEL: Renters insurance
Collapsible: Yes
Header badge: Active or Inactive

Layout:
  Row 1: policy_renter_active | policy_renter_carrier
  Row 2: policy_renter_premium | policy_renter_expiration

---

PANEL: Umbrella
Collapsible: Yes
Header badge: Active or Inactive

Layout:
  Row 1: policy_umbrella_active | policy_umbrella_carrier
  Row 2: policy_umbrella_limit | policy_umbrella_premium
  Row 3: policy_umbrella_expiration

---

PANEL: Life insurance
Collapsible: Yes
Header badge: Active or Inactive

Layout:
  Row 1: policy_life_active | policy_life_carrier
  Row 2: policy_life_type | policy_life_face_value (label: "Death benefit")
  Row 3: policy_life_premium | policy_life_expiration (label: "Term end date")

---

PANEL: Medicare
Collapsible: Yes
Header badge: Active or Inactive

Layout:
  Row 1: policy_medicare_active | policy_medicare_carrier
  Row 2: policy_medicare_plan_type | policy_medicare_plan_name
  Row 3: policy_medicare_premium (label: "Monthly premium") | policy_medicare_effective
  Row 4: policy_medicare_aep_flag (label: "AEP flag")

---

### TAB 3: Renewal

All renewal tracking fields in one focused view.
Gretchen works this tab during renewal season.

---

PANEL: Renewal status
Collapsible: No

Layout:
  Row 1: next_renewal_date (label: "Next renewal") | next_renewal_lob (label: "LOB")
  Row 2: next_renewal_carrier | days_to_renewal (label: "Days remaining")
  Row 3: renewal_outreach_stage (label: "Outreach stage") — full width

---

PANEL: Quote tracking
Collapsible: Yes — default expanded

Layout:
  Row 1: renewal_quote_received | renewal_quote_date
  Row 2: renewal_quote_amount | renewal_quote_carrier [CONDITIONAL]

---

PANEL: Decision & outcome
Collapsible: Yes — default expanded

Layout:
  Row 1: renewal_decision — full width
  Row 2: premium_change_amount | premium_change_pct [CONDITIONAL]
  Row 3: rate_increase_flag
  Row 4: renewal_decision_notes — full width [CONDITIONAL]

---

PANEL: Claims history
Collapsible: Yes — default expanded

Layout:
  Row 1: claims_count_lifetime | claims_count_3yr
  Row 2: claims_open | last_claim_date
  Row 3: last_claim_lob | last_claim_type
  Row 4: last_claim_status
  Row 5: claims_notes — full width

---

PANEL: Outreach log
Collapsible: Yes — default expanded

Layout:
  Row 1: last_contact_date | last_contact_type
  Row 2: last_contact_by | last_contact_outcome
  Row 3: outreach_attempts_current (label: "Attempts this cycle")
  Divider
  Row 4: nps_score | nps_date
  Row 5: referrals_given

---

## STEP 4 — PERSONAL LINES LIST VIEW

Navigate to: Admin → Entity Manager → Account → Layouts → List View

Create saved filter: Personal Lines
  Condition: account_type = Personal

Column configuration:
  account_name (display as: primary_first_name + primary_last_name) — 25%
  lob                    — 12%
  next_renewal_date      — 10%   Color: red if <15 days, amber if 15-30 days
  total_annual_premium   — 10%
  renewal_outreach_stage — 12%
  score_total            — 8%    Render as colored number matching tier color
  gap_count              — 7%    Render as amber badge if > 0
  account_status         — 8%    Colored badge
  assigned_user          — 8%

Sort default: next_renewal_date ascending
  (soonest renewal at top — keeps Gretchen focused on what's urgent)

Pin to left sidebar as "Personal Lines"

---

## STEP 5 — ACCOUNT STATUS BADGE COLORS

Navigate to: Admin → Entity Manager → Account → Fields → account_status
Set label colors:

  Active    → success (green)
  Renewing  → warning (amber)
  Urgent    → danger (red)
  At Risk   → danger (red)
  Inactive  → default (gray)

---

## STEP 6 — ACCOUNT SCORE AUTOMATION TRIGGERS

The following n8n workflows must be built to keep the score current.
Document these endpoints for the n8n build spec.

Trigger 1 — Score recalculation
  Fire: Daily at 6am ET
  Action: For every account where account_type = Personal and account_status != Inactive
    Recalculate all 5 score components
    Sum to score_total
    Derive score_tier from total
    Set score_change_direction and score_change_amount vs previous score_total
    PATCH Account via EspoCRM REST API
    If score drops below 50 and score_alert_sent = false:
      Fire Slack alert to Gretchen
      Set score_alert_sent = true

Score calculation rules:

  score_bundle_depth:
    Count active policy Bool fields where value = true
    1 policy  = 5 pts
    2 policies = 10 pts
    3 policies = 15 pts
    4+ policies = 20 pts

  score_payment_history:
    Pull from NowCerts payment records for this account
    0 late payments     = 20 pts
    1 late payment      = 14 pts
    2 late payments     = 8 pts
    3+ late payments    = 0 pts
    NowCerts unavailable = carry forward last known value

  score_years_retained:
    Calculate from client_since to today
    < 1 year  = 4 pts
    1-2 years = 8 pts
    3-4 years = 12 pts
    5-6 years = 16 pts
    7+ years  = 20 pts

  score_claims_activity:
    Use claims_count_3yr
    0 claims = 20 pts
    1 claim  = 14 pts
    2 claims = 8 pts
    3+ claims = 0 pts

  score_last_contact:
    Calculate days since last_contact_date
    < 30 days  = 20 pts
    31-60 days = 14 pts
    61-90 days = 8 pts
    91-180 days = 4 pts
    180+ days  = 0 pts

Trigger 2 — Gap flag calculation
  Fire: On Account save + daily sweep
  Logic:
    gap_umbrella = true if policy_umbrella_active = false
    gap_life = true if policy_life_active = false
    gap_renters = true if residence_type = Rented AND policy_renter_active = false
    gap_auto_um = true if policy_auto_active = true AND policy_auto_um_uim = false
    gap_medicare = true if primary_dob is set AND today >= (primary_dob + 64 years)
                          AND policy_medicare_active = false
    gap_medicare_eligible = primary_dob + 65 years
    gap_landlord = true if rental_property_flag = true AND policy_umbrella_active = false
    gap_rideshare = true if rideshare_driver_flag = true AND policy_auto_active = true
    gap_final_expense = true if policy_life_active = false
                              AND primary_dob is set
                              AND age(primary_dob) >= 70
    gap_count = count of all true gap flags
    youthful_driver_flag = true if any value in dependent_ages is between 16 and 25
    rate_increase_flag = true if premium_change_pct > 15

Trigger 3 — Next renewal calculation
  Fire: Daily at 6am ET
  Logic:
    Find earliest expiration date across all active policy expiration fields
    Set next_renewal_date = that date
    Set next_renewal_lob = corresponding LOB
    Set next_renewal_carrier = corresponding carrier
    Set days_to_renewal = (next_renewal_date - today) in days
    Set account_status:
      days_to_renewal <= 15  → Urgent
      days_to_renewal 16-30  → Renewing
      days_to_renewal > 30   → Active

Trigger 4 — AEP flag
  Fire: October 1 each year
  Logic:
    For every account where policy_medicare_active = true
    Set policy_medicare_aep_flag = true
    Reset to false on January 1

---

## STEP 7 — ESPOCRM REST API FIELD MAP FOR N8N

All fields are writable via:
PATCH /api/v1/Account/{id}

Key field names for n8n PATCH payload (camelCase as EspoCRM expects):

  accountType, accountStatus, assignedUserId
  clientSince, referralSource, referralName
  primaryFirstName, primaryLastName, primaryDob
  spouseFirstName, spouseLastName, spouseDob
  dependentsCount, dependentAges
  propertyAddress, propertyCity, propertyState, propertyZip
  residenceType, yearsAtAddress, mailingAddressSame, mailingAddress
  vehicleCount, vehicle1Year, vehicle1Make, vehicle1Model
  vehicle1Vin, vehicle1Use, vehicle1AnnualMiles, vehicle1Ownership
  vehicle2Year, vehicle2Make, vehicle2Model
  vehicle2Vin, vehicle2Use, vehicle2AnnualMiles, vehicle2Ownership
  youthfulDriverFlag, rideshareDriverFlag
  driverCount, driver1Name, driver1Dob, driver1LicenseState
  driver1Violations, driver1Accidents
  driver2Name, driver2Dob, driver2LicenseState
  driver2Violations, driver2Accidents, mvrFlag
  homeYearBuilt, homeConstruction, homeSquareFootage
  homeDwellingValue, homeRoofYear, homeRoofMaterial
  homeSecuritySystem, homeAlarmMonitored
  homeTampoline, homePool, homeDog, homeDogBreed
  rentalPropertyFlag, rentalPropertyCount
  policyAutoActive, policyAutoCarrier, policyAutoNumber
  policyAutoPremium, policyAutoEffective, policyAutoExpiration
  policyAutoBiLimits, policyAutoCompCollision
  policyAutoDeductible, policyAutoUmUim
  policyHomeActive, policyHomeCarrier, policyHomeNumber
  policyHomePremium, policyHomeEffective, policyHomeExpiration
  policyHomeDwellingLimit, policyHomeDeductible, policyHomeWindHailDed
  policyRenterActive, policyRenterCarrier
  policyRenterPremium, policyRenterExpiration
  policyUmbrellaActive, policyUmbrellaCarrier
  policyUmbrellaLimit, policyUmbrellaPremium, policyUmbrellaExpiration
  policyLifeActive, policyLifeCarrier, policyLifeType
  policyLifeFaceValue, policyLifePremium, policyLifeExpiration
  policyMedicareActive, policyMedicareCarrier
  policyMedicarePlanType, policyMedicarePlanName
  policyMedicarePremium, policyMedicareEffective, policyMedicareAepFlag
  totalAnnualPremium, policyCountActive
  gapUmbrella, gapUmbrellaReason, gapLife, gapLifeReason
  gapLifeNeedEst, gapRenters, gapAutoUm, gapMedicare
  gapMedicareEligible, gapLandlord, gapRideshare, gapFinalExpense, gapCount
  scoreTotal, scoreTier, scoreBundleDepth, scorePaymentHistory
  scoreYearsRetained, scoreClaimsActivity, scoreLastContact
  scoreLastCalculated, scoreChangeDirection, scoreChangeAmount, scoreAlertSent
  nextRenewalDate, nextRenewalLob, nextRenewalCarrier, daysToRenewal
  renewalOutreachStage, renewalQuoteReceived, renewalQuoteAmount
  renewalQuoteCarrier, renewalQuoteDate, renewalDecision
  renewalDecisionNotes, premiumChangeAmount, premiumChangePct, rateIncreaseFlag
  claimsCountLifetime, claimsCount3yr, claimsOpen
  lastClaimDate, lastClaimLob, lastClaimType, lastClaimStatus, claimsNotes
  lastContactDate, lastContactType, lastContactById, lastContactOutcome
  outreachAttemptsCurrent, npsScore, npsDate, referralsGiven

---

## VALIDATION CHECKLIST

[ ] 138 fields created on Account entity
[ ] Dynamic logic fires correctly on all conditional fields
[ ] Overview tab renders 5 panels in two-column layout
[ ] Account score displays as large number with tier badge
[ ] Score factor bars render with correct colors
[ ] Active policies panel shows only active LOBs
[ ] Coverage gaps panel shows only true gap flags
[ ] Prep pitch buttons fire correctly
[ ] Policies tab shows all 6 LOB panels with active/inactive badge
[ ] Renewal tab shows all 5 renewal panels
[ ] Personal Lines list view sorted by next_renewal_date ascending
[ ] account_status auto-updates based on days_to_renewal
[ ] n8n score recalculation runs daily at 6am
[ ] n8n gap calculation runs on save and daily
[ ] n8n next renewal calculation runs daily
[ ] AEP flag sets October 1 and resets January 1
[ ] Slack alert fires when score drops below 50
[ ] All field names in REST API payload match camelCase spec above
```