# 02-Underwriting

Carrier knowledge, appetite guides, commercial data models, class codes, and risk assessment tools.

## Subfolders
- `Carriers/` - Carrier appetite guides and commission schedules
- `Commercial-Data-Model/` - GL, WC, SIC class codes and risk scoring
- `Knowledge-Base/` - Insurance education, lines of business reference
- `Intake-Schemas/` - Client intake forms and data collection specs

## Key Resources
- Insurance Carrier Database Reference Guide
- AI Underwriting Runbook
- Commercial Client Intake Schema
- GL/WC/SIC class code databases (2,000+ entries)
- Carrier appetite matrix

## Data Flow
Underwriting data feeds into:
1. Zoho CRM (client/policy records)
2. Supabase `knowledge_chunks` (RAG retrieval)
3. Claude agents (field research and risk assessment)
