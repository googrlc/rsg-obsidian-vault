---
name: vin-lookup
description: >
  Decodes VINs via the free NHTSA vPIC API for commercial auto underwriting. Returns year, make, model, GVWR, body class. Includes GVWR classification table (Class 1–8), underwriting flags, and batch fleet lookup.
---

# VIN Lookup — Commercial Auto Underwriting

**Trigger:** Agent receives a VIN, fleet schedule, or vehicle question for quoting.

**Output:** Decoded vehicle data with underwriting classification.

## Data Source

### NHTSA vPIC API (free, no key required)
- **Base URL:** `https://vpic.nhtsa.dot.gov/api`
- **Format:** Always append `?format=json`
- **Rate limit:** None published, but batch endpoint preferred for 2+ VINs

## Single VIN Decode

```
GET https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{VIN}?format=json
```

### Key Fields to Extract
| vPIC Field | Use |
|---|---|
| `ModelYear` | Policy year validation |
| `Make` | Carrier appetite matching |
| `Model` | Rate class |
| `BodyClass` | Truck/Van/Sedan/Bus classification |
| `GVWR` | Weight class (drives premium) |
| `DriveType` | 4WD/AWD flag |
| `FuelTypePrimary` | EV/Hybrid flag |
| `VehicleType` | TRUCK/PASSENGER/MULTIPURPOSE/BUS |
| `PlantCountry` | Import flag |
| `DisplacementL` | Engine size |
| `Doors` | Body style confirmation |
| `TrailerType` | Trailer classification |
| `TrailerBodyType` | Cargo type |

## Batch Fleet Decode (up to 50 VINs)

```
POST https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVINValuesBatch/
Content-Type: application/x-www-form-urlencoded

format=json&data={VIN1};{VIN2};{VIN3}
```

Semicolon-separated, max 50 per call. For larger fleets, batch in groups of 50.

## GVWR Classification Table

| Class | GVWR (lbs) | Examples | Insurance Category |
|---|---|---|---|
| 1 | 0–6,000 | Sedans, small SUVs, pickups | Light Duty — Personal Auto rates |
| 2 | 6,001–10,000 | Full-size pickups, cargo vans | Light Duty — Commercial Auto |
| 3 | 10,001–14,000 | Large vans, small box trucks | Medium Duty |
| 4 | 14,001–16,000 | City delivery trucks, large walk-ins | Medium Duty |
| 5 | 16,001–19,500 | Bucket trucks, large stake beds | Medium Duty |
| 6 | 19,501–26,000 | School buses, single-axle box trucks | Medium Duty |
| 7 | 26,001–33,000 | Refuse trucks, city transit buses | Heavy Duty |
| 8 | 33,001+ | Tractor-trailers, dump trucks, cement mixers | Heavy Duty — Specialized |

### GVWR Parsing
The vPIC `GVWR` field returns a range string like `"Class 3: 10,001 - 14,000 lb"`. Parse the class number or max weight:
```
GVWR string → extract class number (1-8) → map to table above
```

If `GVWR` is empty (common for passenger vehicles), classify as Class 1.

## Underwriting Flags

Flag these for the agent and post warnings:

| Flag | Condition | Why It Matters |
|---|---|---|
| **🔴 HEAVY DUTY** | Class 7-8 | Requires specialized trucking markets, higher limits |
| **🟡 MEDIUM DUTY** | Class 3-6 | Commercial auto required, check radius of operations |
| **🟡 OVER 10K GVW** | GVWR > 10,000 | CDL may be required — impacts driver qualification |
| **🟡 OVER 26K GVW** | GVWR > 26,000 | CDL Class A required, DOT number mandatory |
| **🔴 MODEL YEAR 15+** | Current year minus ModelYear > 15 | Many carriers decline vehicles older than 15 years |
| **🟡 MODEL YEAR 10+** | Current year minus ModelYear > 10 | Stated value may be required, limited carriers |
| **⚡ ELECTRIC/HYBRID** | FuelTypePrimary contains "Electric" or "Hybrid" | Limited commercial auto markets, battery exclusions |
| **🚌 BUS** | VehicleType = "BUS" | Specialty market, passenger liability |
| **🚛 TRAILER** | VehicleType = "TRAILER" | Separate inland marine or auto policy |

## Output Format — Vehicle Brief

```
🚛 VIN DECODE: {VIN}
{YEAR} {MAKE} {MODEL} — {BODY_CLASS}
GVWR: {CLASS} ({WEIGHT} lbs) — {INSURANCE_CATEGORY}
Drive: {DRIVE_TYPE} | Fuel: {FUEL} | Doors: {DOORS}

UNDERWRITING FLAGS:
{🔴/🟡/⚡ flags if any, or "✅ No flags — standard commercial auto"}

CARRIER NOTES:
- Class {X} vehicle → {applicable carrier appetite notes}
- Age: {AGE} years → {age-related notes}
```

## Fleet Schedule Builder

When processing a full fleet schedule:
1. Batch decode all VINs (groups of 50)
2. Sort by GVWR class descending (heaviest first — they drive the rate)
3. Flag any VINs that fail to decode (typos, bad check digits)
4. Summarize fleet:

```
🚛 FLEET SUMMARY: {COMPANY}
Total vehicles: {COUNT}
Class breakdown: {X} Light Duty | {X} Medium | {X} Heavy
Oldest vehicle: {YEAR} {MAKE} {MODEL} ({AGE} yrs)
Newest vehicle: {YEAR} {MAKE} {MODEL}
Flags: {count} vehicles with underwriting flags

FULL SCHEDULE:
# | VIN | Year | Make/Model | Class | GVWR | Flags
1 | {VIN} | {YEAR} | {MAKE} {MODEL} | {CLASS} | {GVWR} | {FLAGS}
...
```

## Integration with Other Skills
- After decode, check **carrier-appetite.md** for Commercial Auto carriers by GVWR class
- For fleet prospects, feed results to **prospect-researcher.md** for full pre-call brief
- Log fleet details in EspoCRM via **crm-manager.md** on the Account record

## Error Handling
- Invalid VIN (bad check digit) → vPIC returns partial data with `ErrorCode` field. Flag as "⚠️ VIN check digit invalid — verify with client"
- VIN not found → may be too new, foreign-only, or kit vehicle. Note in output.
- NHTSA API timeout → retry once after 3 seconds
