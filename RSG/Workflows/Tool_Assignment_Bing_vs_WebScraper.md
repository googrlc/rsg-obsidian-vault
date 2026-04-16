# Tool Assignment — Bing vs Web Scraper
# Which tool goes in which node in RSG Client Intake & Assessment
# App ID: 81bfd19b-5cee-4726-915e-bddc92d3556d
# Updated: 2026-04-08

---

## THE RULE
- Bing = find the URL / get the data point
- Web Scraper = read the actual page content

---

## NODE-BY-NODE ASSIGNMENTS

### Vehicle Web Search → BING ✓ (keep as-is)
Job: find KBB/Edmunds retail value from search snippets
Bing is enough — the number surfaces in the snippet
No page scraping needed
Query: "[year] [make] [model] [trim] retail value Georgia 2026"

### Property Web Search → SPLIT: BING first, then WEB SCRAPER
Step 1 — Bing: "[property address] site:qpublic.net OR site:assessor.* square footage"
Step 2 — Web Scraper: scrape the county tax assessor URL that Bing returns
Why: Tax assessor pages are dynamic. Bing snippet won't have sq footage.
      Web Scraper reads the actual property record page and pulls it.
Query for Web Scraper: pass the top URL from Bing result directly

### Web Search Enrichment → SPLIT: BING first, then WEB SCRAPER
Step 1 — Bing (existing): "[business name] official website"
Step 2 — Web Scraper (ADD THIS): scrape the official website URL from Bing result
Why: Bing gives you the homepage URL. Web Scraper reads what's actually
      on the page — services, fleet size, locations, contact info, red flags
Query for Web Scraper: pass official_website URL from Bing result

---

## CHANGES FOR CLAUDE CODE

### Change 1 — Property Research node: add Web Scraper step
After the existing Property Web Search (Bing) node, add a NEW tool node:
- Tool: Web Scraper
- Title: Scrape Property Records Page
- Input: top URL result from Property Web Search node
- Output: raw page content → passes to Property Research & Rebuild Cost LLM node

Update Property Research & Rebuild Cost LLM prompt to include:
{{#scrape_property_records_node.text#}} in the user prompt

### Change 2 — Business enrichment: add Web Scraper step
After the existing Web Search Enrichment (Bing) node, add a NEW tool node:
- Tool: Web Scraper
- Title: Scrape Business Website
- Input: first URL result from Web Search Enrichment node
- Output: raw page content → passes to Parse Web Research Results LLM node

Update Parse Web Research Results LLM user prompt to include:
{{#scrape_business_website_node.text#}} in the user prompt

---

## WHAT THIS GETS YOU

| Before | After |
|---|---|
| Business website: just a URL + snippet | Full homepage content: services, locations, fleet, red flags |
| Property sq footage: often missing | Actual tax assessor record: sq ft, year built, lot size |
| Rebuild cost: estimate only | Grounded in actual property data |

---
## NO CHANGE NEEDED
- Vehicle Web Search — Bing only is correct
- Carrier Appetite Lookup — Supabase direct, no search needed
- EspoCRM nodes — API calls, no search needed
