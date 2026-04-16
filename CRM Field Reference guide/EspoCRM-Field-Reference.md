# EspoCRM Field Reference — RSG
*Leads · Contacts · Tasks · Accounts · Opportunities | Last updated: 2026-04-08*

> **Bold = Enum field** (dropdown with fixed options — must use exact values)

---

## LEADS

| Label | Field Name | Type | Enum Options |
|-------|------------|------|--------------|
| First Name | firstName | Varchar | — |
| Last Name | lastName | Varchar | — |
| Account Name | accountName | Varchar | — |
| Title | title | Varchar | — |
| **Status** | **status** | **Enum** | `New` · `Assigned` · `In Process` · `Converted` · `Recycled` · `Dead` |
| **Priority** | **priority** | **Enum** | `Hot` · `Warm` · `Cold` |
| **Source** | **source** | **Enum** | `Call` · `Email` · `Existing Customer` · `Partner` · `Public Relations` · `Web Site` · `Campaign` · `Other` |
| **Insurance Interest** | **insuranceInterest** | **Enum** | `Commercial Auto` · `General Liability` · `Workers Comp` · `Commercial Property` · `BOP` · `Personal Auto` · `Homeowners` · `Life` · `Health` · `Medicare` · `Group Benefits` · `Inland Marine` · `Multiple` · `Other` |
| **Industry** | **industry** | **Enum** | Agriculture · Automotive · Construction · Consulting · Education · Finance · Healthcare · Insurance · Landscaping Services / Tree Care · Legal · Manufacturing · Real Estate · Retail · Technology · Transportation · (+ more) |
| **Salutation** | **salutationName** | **Enum** | `Mr.` · `Ms.` · `Mrs.` · `Dr.` |
| Email | emailAddress | Email | — |
| Phone | phoneNumber | Phone | — |
| Website | website | URL | — |
| Date of Birth | dateOfBirth | Date | — |
| Est. Premium | estimatedPremium | Currency | — |
| Opportunity Amount | opportunityAmount | Currency | — |
| Current Carrier | currentCarrier | Varchar | — |
| Currently Insured? | currentlyInsured | Boolean | — |
| Medicare Eligible | medicareEligible | Boolean | — |
| Medicare Part A Date | medicarePartADate | Date | — |
| Medicare Part B Date | medicarePartBDate | Date | — |
| Current Medicare Plan | currentMedicarePlan | Varchar | — |
| Do Not Call | doNotCall | Boolean | — |
| Intel Pack Run | intelPackRun | Boolean | — |
| T65 Alert Sent | t65AlertSent | Boolean | — |
| AI Summary | aiSummary | Text | — |
| Description | description | Text | — |
| Assigned User | assignedUser | Link | — |
| Converted At | convertedAt | Date-Time | — |
| Created At | createdAt | Date-Time | — |

---

## CONTACTS

| Label | Field Name | Type | Enum Options |
|-------|------------|------|--------------|
| First Name | firstName | Varchar | — |
| Last Name | lastName | Varchar | — |
| **Salutation** | **salutationName** | **Enum** | `Mr.` · `Ms.` · `Mrs.` · `Dr.` |
| Title | title | Varchar | — |
| **Client Type** | **clientType** | **Enum** | `Personal` · `Commercial` |
| **Household Role** | **householdRole** | **Enum** | `Primary` · `Spouse` · `Dependent` · `Co-insured` |
| **Opportunity Role** | **opportunityRole** | **Enum** | `Decision Maker` · `Evaluator` · `Influencer` |
| **Life Health Class** | **lifeHealthClass** | **Enum** | `Preferred Plus` · `Preferred` · `Standard Plus` · `Standard` · `Substandard` |
| **Life Policy Type** | **lifePolicyType** | **Enum** | `Term` · `Whole` · `Universal` |
| **Medicare Plan Type** | **medicarePlanType** | **Enum** | `Supplement` · `Advantage` · `Part D` |
| Email | emailAddress | Email | — |
| Phone | phoneNumber | Phone | — |
| Address Street | addressStreet | Text | — |
| Address City | addressCity | Varchar | — |
| Address State | addressState | Varchar | — |
| Address Postal Code | addressPostalCode | Varchar | — |
| Date of Birth | dateOfBirth | Date | — |
| Account | account | Link | — |
| CSR Name | csrName | Varchar | — |
| Momentum Client ID | momentumClientId | Varchar | — |
| Drive Folder URL | contactDriveFolderUrl | URL | — |
| Medicare Eligible | medicareEligible | Boolean | — |
| Medicare Part B | medicarePartB | Boolean | — |
| Medicare Carrier | medicareCarrier | Varchar | — |
| AEP/SEP Date | aepSepDate | Date | — |
| IRMAA Applies | irmaApplies | Boolean | — |
| Life Annual Premium | lifeAnnualPremium | Currency | — |
| Life Face Amount | lifeFaceAmount | Currency | — |
| Life Coverage In Force | lifeCoverageInForce | Boolean | — |
| Life Beneficiary On File | lifeBeneficiaryOnFile | Boolean | — |
| Life Review Date | lifeReviewDate | Date | — |
| Do Not Call | doNotCall | Boolean | — |
| Description | description | Text | — |
| Assigned User | assignedUser | Link | — |
| Policies | policies | Link Multiple | — |
| Renewals | renewals | Link Multiple | — |
| Commissions | commissions | Link Multiple | — |
| Created At | createdAt | Date-Time | — |

---

## TASKS

| Label | Field Name | Type | Enum Options |
|-------|------------|------|--------------|
| Name | name | Varchar | — |
| **Status** | **status** | **Enum** | `Inbox` · `In Progress` · `Waiting on Client` · `Waiting on Carrier` · `Completed` · `Cancelled` |
| **Priority** | **priority** | **Enum** | `Low` · `Normal` · `High` · `Urgent` |
| **Urgency** | **urgency** | **Enum** | `Urgent` · `High` · `Normal` · `Low` |
| **Task Type** | **taskType** | **Enum** | `Client Service` · `Policy Change` · `Renewal` · `New Business` · `Follow Up` · `Onboarding` · `Claims` · `Commission` · `Admin` · `Other` |
| **Task Source** | **taskSource** | **Enum** | `Account` · `Contact` · `Policy` |
| **Sync Source** | **syncSource** | **Enum** | `Manual` · `Gmail` · `Slack` · `Momentum` · `n8n` · `Viktor` |
| Parent | parent | Link Parent | Account · Contact · Lead · Opportunity · Case · Policy · Renewal |
| Account | account | Link | — |
| Contact | contact | Link | — |
| Assigned User | assignedUser | Link | — |
| Date Start | dateStart | Date-Time | — |
| Date Due | dateEnd | Date-Time | — |
| Date Completed | dateCompleted | Date-Time | — |
| Is Overdue | isOverdue | Boolean | — |
| Description | description | Text | — |
| Triage Reason | triageReason | Text | — |
| Triage Summary | triageSummary | Text | — |
| Attachments | attachments | Attachment Multiple | — |
| Created At | createdAt | Date-Time | — |
| Created By | createdBy | Link | — |


---

## ACCOUNTS

| Label | Field Name | Type | Enum Options |
|-------|------------|------|--------------|
| Name | name | Varchar | — |
| **Account Status** | **accountStatus** | **Enum** | `Active` · `Urgent` · `Renewing` · `At Risk` · `Inactive` |
| **Account Type** | **accountType** | **Enum** | `Prospect` · `Commercial Lines` · `Personal Lines` · `Group Benefits` · `Medicare` · `Life Insurance` |
| **Type** | **type** | **Enum** | `Commercial Lines` · `Personal Lines` · `Group Benefits` · `Prospect` |
| **Business Entity** | **businessEntity** | **Enum** | `Sole Proprietor` · `LLC` · `Corporation` · `S-Corp` · `Partnership` · `Non-Profit` · `Other` |
| **Industry** | **industry** | **Enum** | Agriculture · Automotive · Construction · Healthcare · Insurance · Landscaping Services / Tree Care · Legal · Manufacturing · Real Estate · Technology · Transportation · (+ more) |
| **Stage** | **stage** | **Enum** | `New` · `Qualified` · `Proposal` · `Negotiation` · `Closed Won` · `Closed Lost` |
| **Referral Source** | **referralSource** | **Enum** | `Referral` · `Google` · `Social Media` · `Cold Outreach` · `Walk-in` · `NowCerts Import` · `Other` |
| **Retention Risk** | **retentionRisk** | **Enum** | `Low` · `Medium` · `High` |
| **Score Tier** | **scoreTier** | **Enum** | `Strong` · `Good` · `At Risk` · `Critical` |
| **Renewal Decision** | **renewalDecision** | **Enum** | `Renewing` · `Re-marketed` · `Lost — Price` · `Lost — Service` · `Lost — Carrier` · `Non-renewed by Carrier` |
| **Renewal Outreach Stage** | **renewalOutreachStage** | **Enum** | `Not Started` · `Day 60 Sent` · `Day 30 Sent` · `Day 14 Sent` · `Confirmed` · `Shopped` · `Lost` |
| **Last Contact Outcome** | **lastContactOutcome** | **Enum** | `Reached` · `Voicemail` · `No Answer` · `Email Opened` · `Unresponsive` |
| **Last Contact Type** | **lastContactType** | **Enum** | `Call` · `Email` · `Text` · `In Person` |
| **Preferred Contact** | **preferredContact** | **Enum** | `Phone` · `Email` · `Text` |
| **LOB** | **lob** | **Multi-Enum** | `Commercial Auto` · `GL` · `Workers Comp` · `Cargo` · `Home` · `Auto` · `Life` · `Medicare` · `BOP` · `Umbrella` · `Professional Liability` · `Builders Risk` · `Transportation` |
| **Intel Confidence** | **intelConfidence** | **Enum** | `High` · `Medium` · `Low` |
| **Score Change Direction** | **scoreChangeDirection** | **Enum** | `Up` · `Down` · `Flat` |
| **Marital Status** | **maritalStatus** | **Enum** | `Single` · `Married` · `Divorced` · `Widowed` · `Separated` |
| **Residence Type** | **residenceType** | **Enum** | `Owned` · `Rented` · `Condo` · `Mobile Home` · `Other` |
| **Home Construction** | **homeConstruction** | **Enum** | `Frame` · `Masonry` · `Mixed` · `Log` · `Other` |
| **Home Roof Material** | **homeRoofMaterial** | **Enum** | `Asphalt Shingle` · `Metal` · `Tile` · `Wood Shake` · `Other` |
| **Policy Life Type** | **policyLifeType** | **Enum** | `Term` · `Whole` · `Universal` · `Final Expense` |
| **Policy Medicare Plan Type** | **policyMedicarePlanType** | **Enum** | `Medicare Advantage` · `Medicare Supplement` · `PDP` |
| **Last Claim LOB** | **lastClaimLob** | **Enum** | `Auto` · `Home` · `Umbrella` · `Life` · `Medicare` · `Renters` · `Other` |
| **Last Claim Status** | **lastClaimStatus** | **Enum** | `Open` · `Closed` · `Subrogation` |
| Email | emailAddress | Email | — |
| Phone | phoneNumber | Phone | — |
| Website | website | URL | — |
| FEIN | fein | Varchar | — |
| Annual Premium | annualPremium | Currency | — |
| Total Active Premium | totalActivePremium | Currency | — |
| Est. Premium | estimatedPremium | Currency | — |
| Account Score | accountScore | Integer | — |
| Risk Score | riskScore | Integer | — |
| Active Policy Count | activePolicyCount | Integer | — |
| Employee Count | employeeCount | Integer | — |
| Years In Business | yearsInBusiness | Integer | — |
| Client Since | clientSince | Date | — |
| Next Renewal Date | nextRenewalDate | Date | — |
| Next X-Date | nextXDate | Date | — |
| Last Contact Date | lastContactDate | Date | — |
| Momentum Client ID | momentumClientId | Varchar | — |
| Google Drive Folder URL | googleDriveFolderUrl | URL | — |
| CSR Name | csrName | Varchar | — |
| AI Summary | intelAiSummary | Text | — |
| AI Assessment | aiAssessment | Text | — |
| Coverage Gaps | coverageGaps | Text | — |
| Description | description | Text | — |
| Assigned User | assignedUser | Link | — |
| Policies | policies | Link Multiple | — |
| Renewals | renewals | Link Multiple | — |


---

## OPPORTUNITIES

| Label | Field Name | Type | Enum Options |
|-------|------------|------|--------------|
| Name | name | Varchar | — |
| **Stage** | **stage** | **Enum** | `Prospect` · `Qualify` · `Quote` · `Proposal` · `Negotiate` · `Won - Bound` · `Lost` · `Renewal Notice Sent` · `Markets Out / Shopping` · `Quoted` · `Presented to Client` · `Bound / Renewed` · `Non-Renewal / Lost` |
| **Priority** | **priority** | **Enum** | `Hot` · `Warm` · `Cold` |
| **Business Type** | **businessType** | **Enum** | `New Business` · `Renewal` · `Rewrite` |
| **Line of Business** | **lineOfBusiness** | **Enum** | `Commercial Auto` · `General Liability` · `Workers Comp` · `Commercial Property` · `BOP` · `Professional Liability` · `Umbrella` · `Builders Risk` · `Inland Marine` · `Personal Auto` · `Homeowners` · `Renters` · `Life` · `Health` · `Medicare` · `Group Benefits` · `Other` |
| **Lead Source** | **leadSource** | **Enum** | `Call` · `Email` · `Existing Customer` · `Partner` · `Web Site` · `Campaign` · `Other` |
| **Lost Reason** | **lostReason** | **Enum** | `Price` · `Coverage` · `Service` · `Competitor Stole` · `Business Closed` · `Carrier Non-Renewed` · `Client Moved` · `Unknown` · `N/A` |
| **Last Contact Method** | **lastContactMethod** | **Enum** | `Phone` · `Email` · `Text` · `No Response` |
| **Policy Stub Status** | **policyStubStatus** | **Enum** | `Pending Sync` · `Synced` |
| **CA Business Type** | **caBusType** | **Enum** | `Trucking` · `Contractor` · `Fleet` · `Delivery` · `Other` |
| **Operating Radius** | **caRadius** | **Enum** | `Local <50mi` · `Intermediate 50-200mi` · `Long haul 200+mi` |
| **Prop Construction Type** | **propConstructionType** | **Enum** | `Frame` · `Masonry` · `Mixed` |
| **Prop Occupancy** | **propOccupancy** | **Enum** | `Owner Occupied` · `Tenant Occupied` · `Seasonal` · `Vacant` · `Commercial` |
| **Prop Roof Type** | **propRoofType** | **Enum** | `Asphalt Shingle` · `Metal` · `Tile` · `Flat` · `Slate` · `Other` |
| **Life Coverage Type** | **lifeCoverageType** | **Enum** | `Term` · `Whole` · `Universal` · `IUL` |
| **Term Length** | **lifeTermLength** | **Enum** | `10yr` · `15yr` · `20yr` · `30yr` |
| **Health Coverage Type** | **healthCoverageType** | **Enum** | `Term` · `Whole Life` · `Universal Life` · `Final Expense` · `Medicare Supplement` · `Medicare Advantage` · `Group` · `Individual` · `Other` |
| **Health Risk Class** | **healthRiskClass** | **Enum** | `Preferred Plus` · `Preferred` · `Standard Plus` · `Standard` · `Substandard` · `Declined` · `Pending` |
| **Medicare Plan Type** | **medPlanType** | **Enum** | `Advantage` · `Supplement` · `Part D` |
| **Umbrella Limit** | **umbrellaLimit** | **Enum** | `$1M` · `$2M` · `$5M` · `$10M` |
| Account | account | Link | — |
| Contact (Primary) | contact | Link | — |
| Amount | amount | Currency | — |
| Est. Premium | estimatedPremium | Currency | — |
| Written Premium | writtenPremium | Currency | — |
| Est. Commission | estimatedCommission | Currency | — |
| Commission Rate % | commissionRate | Float | — |
| Close Date | closeDate | Date | — |
| Bind Date | bindDate | Date | — |
| Effective Date | effectiveDate | Date | — |
| Carrier | carrier | Varchar | — |
| Target Carrier | targetCarrier | Varchar | — |
| Current Carrier | currentCarrier | Varchar | — |
| Policy Number | policyNumber | Varchar | — |
| DOT Number | caDotNumber | Varchar | — |
| MC Number | caMcNumber | Varchar | — |
| Vehicle Count | caVehicleCount | Integer | — |
| Driver Count | caDriverCount | Integer | — |
| GL Annual Payroll | glAnnualPayroll | Currency | — |
| GL Annual Revenue | glAnnualRevenue | Currency | — |
| WC Annual Payroll | wcAnnualPayroll | Currency | — |
| WC Experience Mod | wcExperienceMod | Float | — |
| Loss Runs Requested | lossRunsRequested | Boolean | — |
| Commission Logged | commissionLogged | Boolean | — |
| AI Summary | aiSummary | Text | — |
| Description | description | Text | — |
| Assigned User | assignedUser | Link | — |
| Created At | createdAt | Date-Time | — |

### Opportunity Checklist Fields (all Boolean)

| Label | Field Name |
|-------|------------|
| App Submitted | chkAppSubmitted |
| Bound | chkBound |
| CMS Confirmation | chkCmsConfirmation |
| Dec Page Delivered | chkDecPageDelivered |
| MVRs Pulled | chkMvrsPulled |
| Plan Presented | chkPlanPresented |
| Proposal Sent | chkProposalSent |
| Quote Submitted | chkQuoteSubmitted |
| Scope of Appointment | chkScopeOfAppt |
| Signed App Received | chkSignedAppReceived |
| Underlying Confirmed | chkUnderlyingConfirmed |
| Welcome Letter | chkWelcomeLetter |


---

## QUICK ENUM CHEAT SHEET

### Leads
- **Status:** New / Uncontacted · Assigned · In Process · Converted · Recycled · Dead
- **Priority:** Hot · Warm · Cold
- **Source:** Call · Email · Existing Customer · Partner · Web Site · Campaign · Other
- **Insurance Interest:** Commercial Auto · GL · Workers Comp · Commercial Property · BOP · Personal Auto · Homeowners · Life · Health · Medicare · Group Benefits · Inland Marine · Multiple · Other

### Tasks
- **Status:** Inbox · In Progress · Waiting on Client · Waiting on Carrier · Completed · Cancelled
- **Priority:** Low · Normal · High · Urgent
- **Type:** Client Service · Policy Change · Renewal · New Business · Follow Up · Onboarding · Claims · Commission · Admin · Other

### Accounts
- **Account Status:** Active · Urgent · Renewing · At Risk · Inactive
- **Account Type:** Prospect · Commercial Lines · Personal Lines · Group Benefits · Medicare · Life Insurance
- **Retention Risk:** Low · Medium · High
- **Score Tier:** Strong · Good · At Risk · Critical
- **Renewal Outreach Stage:** Not Started · Day 60 Sent · Day 30 Sent · Day 14 Sent · Confirmed · Shopped · Lost
- **Renewal Decision:** Renewing · Re-marketed · Lost — Price · Lost — Service · Lost — Carrier · Non-renewed by Carrier

### Opportunities
- **Stage:** Prospect · Qualify · Quote · Proposal · Negotiate · Won - Bound · Lost · Renewal Notice Sent · Markets Out / Shopping · Quoted · Presented to Client · Bound / Renewed · Non-Renewal / Lost
- **Business Type:** New Business · Renewal · Rewrite
- **Line of Business:** Commercial Auto · GL · Workers Comp · Commercial Property · BOP · Professional Liability · Umbrella · Builders Risk · Inland Marine · Personal Auto · Homeowners · Renters · Life · Health · Medicare · Group Benefits · Other
- **Lost Reason:** Price · Coverage · Service · Competitor Stole · Business Closed · Carrier Non-Renewed · Client Moved · Unknown · N/A
- **CA Business Type:** Trucking · Contractor · Fleet · Delivery · Other

### Contacts
- **Client Type:** Personal · Commercial
- **Household Role:** Primary · Spouse · Dependent · Co-insured
- **Medicare Plan Type:** Supplement · Advantage · Part D
- **Life Policy Type:** Term · Whole · Universal

---

## PERSONAL PROFILE FIELDS (Lead + Contact)

> Custom fields — EspoCRM auto-prefixes all custom fields with `c` in the API.

| Label | API Field Name | Type |
|-------|---------------|------|
| Personal LinkedIn | `cPersonalLinkedinUrl` | URL |
| Personal Facebook | `cPersonalFacebook` | URL |
| Personal Instagram | `cPersonalInstagram` | URL |
| Profile Photo URL | `cProfilePhotoUrl` | URL |
| Personal Hooks | `cPersonalHooks` | Text |
| Personality Read | `cPersonalityRead` | Varchar |
| Outreach Angle | `cOutreachAngle` | Text |
| Profile Last Updated | `cProfileLastUpdated` | Date |

**Applies to:** Lead and Contact entities
**Purpose:** Hyper-personalized outreach — survives full client lifecycle (Lead → Contact)
**Note:** Use `c`-prefixed names in ALL API calls and automations
