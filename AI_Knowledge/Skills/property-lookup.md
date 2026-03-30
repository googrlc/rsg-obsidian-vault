---
name: property-lookup
description: >
  Property data lookup for underwriting — Census geocoder, FEMA flood maps, Georgia county tax assessors (Fulton/DeKalb/Gwinnett/Cobb), ISO protection class. Returns year built, construction type, roof age, sq footage, flood zone, replacement cost estimate.
---

# Property Lookup — Underwriting Intelligence

**Trigger:** Agent receives a property address for homeowners, BOP, or commercial property quoting.

**Output:** Property profile with year built, construction, flood zone, protection class, and replacement cost estimate.

## Data Sources (All Free, No API Keys)

### 1. Census Geocoder — Address Validation + FIPS Codes
```
GET https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?address={FULL_ADDRESS}&benchmark=Public_AR_Current&vintage=Current_Current&format=json
```

**Extract:**
- `coordinates` (lat/lon) — needed for FEMA and fire station lookups
- `geographies.Counties[0].BASENAME` — county name
- `geographies.Counties[0].GEOID` — FIPS code (13121=Fulton, 13089=DeKalb, 13135=Gwinnett, 13067=Cobb)
- `matchedAddress` — standardized address

### 2. FEMA Flood Map — NFHL Layer Query
```
GET https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer/28/query?geometry={LON},{LAT}&geometryType=esriGeometryPoint&spatialRel=esriSpatialRelIntersects&outFields=FLD_ZONE,ZONE_SUBTY,SFHA_TF,STATIC_BFE&f=json
```

**Flood Zone Mapping:**
| Zone | Risk | Insurance Impact |
|---|---|---|
| X (unshaded) | Minimal | No flood required |
| X (shaded / B) | Moderate | Flood recommended, not required |
| A, AE, AH, AO | High — SFHA | Flood insurance REQUIRED if mortgaged |
| V, VE | Coastal high hazard | Flood required + higher rates |

### 3. Georgia County Tax Assessors — Property Details

**Fulton County:**
```
https://iaspublicaccess.fultoncountyga.gov/
```
Search by address or parcel ID. Extract: year built, sq footage, construction type, land use code, assessed value.

**DeKalb County:**
```
https://propertyappraisal.dekalbcountyga.gov/
```

**Gwinnett County:**
```
https://www.gwinnettassessor.com/
```

**Cobb County:**
```
https://www.cobbassessor.org/
```

> **Note:** These are web portals, not REST APIs. For automated lookups, use the property details if already known from the client. For manual lookups, provide the direct link with the address pre-filled where possible.

### 4. ISO Protection Class Lookup
Protection class is based on distance to nearest fire station and fire hydrant:

| Distance to Fire Station | Distance to Hydrant | Likely PPC |
|---|---|---|
| < 5 miles, < 1,000 ft | < 1,000 ft | 1–4 (Excellent) |
| < 5 miles | > 1,000 ft | 5–7 (Average) |
| 5–7 miles | Any | 8–8B |
| > 7 miles | Any | 9–10 (Rural) |

**Estimate PPC from geocoded address:**
- Use lat/lon to check nearest fire station (Google Maps or local fire dept data)
- Metro Atlanta (inside I-285) → typically PPC 2-5
- Suburban (Gwinnett, Cobb, outer Fulton) → typically PPC 3-6
- Rural Georgia → PPC 7-10

## Workflow

### Step 1: Geocode the Address
```
GET https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?address={ADDRESS}&benchmark=Public_AR_Current&vintage=Current_Current&format=json
```
Extract lat/lon, county, FIPS code. If no match → ask client to verify address.

### Step 2: Check Flood Zone
Use lat/lon from Step 1:
```
GET https://hazards.fema.gov/gis/nfhl/rest/services/public/NFHL/MapServer/28/query?geometry={LON},{LAT}&geometryType=esriGeometryPoint&spatialRel=esriSpatialRelIntersects&outFields=FLD_ZONE,ZONE_SUBTY,SFHA_TF,STATIC_BFE&f=json
```

### Step 3: Pull Property Details
From county tax assessor (if available) or from client-provided info:
- Year built
- Square footage
- Construction type (frame, masonry, fire-resistive)
- Roof type and age
- Number of stories
- Land use (residential, commercial, mixed)
- Assessed/market value

### Step 4: Estimate Replacement Cost
Rough Georgia replacement cost estimates (2026):
| Construction | Per Sq Ft | Notes |
|---|---|---|
| Frame residential | $150–200 | Wood frame, standard finishes |
| Masonry residential | $175–250 | Brick/block, better wind resistance |
| Frame commercial | $125–175 | Strip retail, offices |
| Masonry commercial | $150–225 | Retail, warehouse |
| Fire-resistive | $200–300 | Steel/concrete, multi-story |

`Estimated replacement = sq_footage * per_sq_ft_rate`

### Step 5: Estimate Protection Class
Based on county + location within metro area. Provide as range unless exact PPC is known.

## Output Format — Property Brief

```
🏠 PROPERTY BRIEF: {ADDRESS}
County: {COUNTY} | FIPS: {FIPS}
Lat/Lon: {LAT}, {LON}

PROPERTY DETAILS:
Year Built: {YEAR} | Age: {AGE} years
Sq Footage: {SQFT} | Stories: {STORIES}
Construction: {TYPE} | Roof: {ROOF_TYPE}
Assessed Value: ${ASSESSED} | Market Value: ${MARKET}

FLOOD ZONE: {ZONE} — {RISK_LEVEL}
{🔴 "Flood insurance REQUIRED" if SFHA | 🟢 "No flood required" if Zone X}
Base Flood Elevation: {BFE if available}

PROTECTION CLASS: {PPC estimate} ({quality label})

REPLACEMENT COST ESTIMATE: ${ESTIMATE}
(Based on {SQFT} sqft × ${RATE}/sqft {CONSTRUCTION} in {COUNTY})

UNDERWRITING FLAGS:
{🔴 Flood zone A/V — mandatory flood}
{🟡 Year built pre-1980 — check wiring, plumbing, roof}
{🟡 PPC 8+ — limited carrier appetite}
{🟡 Frame construction — wind/hail exposure in GA}
{⚠️ Assessed value vs replacement cost gap — potential coinsurance issue}
```

## Underwriting Flags

| Flag | Condition | Action |
|---|---|---|
| **🔴 SFHA Flood Zone** | Zone A, AE, V, VE | Flood policy required, quote separately |
| **🟡 Pre-1980 Build** | Year built < 1980 | Verify electrical (knob & tube?), plumbing (polybutylene?), roof age |
| **🟡 Roof Age 15+** | Current year - roof year > 15 | Many carriers require roof < 15 years, may need inspection |
| **🟡 High PPC** | Protection class 8-10 | Limited carrier options, higher rates |
| **🔴 PPC 10** | No fire protection | Very limited markets, surplus lines likely |
| **🟡 Frame + Coastal** | Frame construction near coast | Wind/hail exclusions, separate wind policy |
| **⚠️ Value Gap** | Replacement cost > 150% of market value | Coinsurance penalty risk, verify with client |

## Integration with Other Skills
- After property brief, check **carrier-appetite.md** for Homeowners/BOP carrier appetite
- Feed results to **prospect-researcher.md** if this is a new commercial prospect
- Log property details on the EspoCRM Account via **crm-manager.md**

## Error Handling
- Census geocoder returns no match → address may be new construction or rural. Ask client to verify.
- FEMA returns no flood data → area may not be mapped. Note "Flood zone unmapped — recommend flood quote anyway"
- County assessor has no record → new construction or recently platted. Use client-provided details.
