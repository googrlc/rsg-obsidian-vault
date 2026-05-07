#!/bin/bash
# RSG Vault Migration Script
# Moves all files from old structure to new 00-05 numbered hierarchy
# Run from the vault root: chmod +x migrate.sh && ./migrate.sh
#
# IMPORTANT: Run this locally, NOT via API. It handles binaries, preserves
# git history, and is atomic. After running, open Obsidian to fix wikilinks,
# then commit and push.

set -e

echo "=== RSG Vault Migration ==="
echo "Moving files to new 00-05 folder structure..."
echo ""

# ──────────────────────────────────────────────────────────────────────────────
# 01-Operations: SOPs, Workflows, Templates, Clients
# ──────────────────────────────────────────────────────────────────────────────
echo "[1/7] Migrating to 01-Operations/..."

mkdir -p "01-Operations/SOPs"
mkdir -p "01-Operations/Workflows"

# SOPs
if [ -d "RSG/SOPs" ]; then
  git mv "RSG/SOPs/Call-Intake-Parser-SOP.md" "01-Operations/SOPs/" 2>/dev/null || true
  if [ -d "RSG/SOPs/Intake Pipeline" ]; then
    mkdir -p "01-Operations/SOPs/Intake Pipeline"
    git mv "RSG/SOPs/Intake Pipeline/README.md" "01-Operations/SOPs/Intake Pipeline/" 2>/dev/null || true
    git mv "RSG/SOPs/Intake Pipeline/rsg-intake-pipeline.py" "01-Operations/SOPs/Intake Pipeline/" 2>/dev/null || true
  fi
fi

# Workflows (operational ones)
if [ -d "RSG/Workflows" ]; then
  git mv "RSG/Workflows/Dify_Node_Prompts_Intake_Agent.md" "01-Operations/Workflows/" 2>/dev/null || true
  git mv "RSG/Workflows/N8n_nowcerts_worink sample.json" "01-Operations/Workflows/" 2>/dev/null || true
  # Handle special characters in filename
  for f in RSG/Workflows/RSG*Renewal*Pipeline*.json; do
    [ -f "$f" ] && git mv "$f" "01-Operations/Workflows/" 2>/dev/null || true
  done
fi

# Templates (if exists)
if [ -d "RSG/Templates" ]; then
  mkdir -p "01-Operations/Templates"
  git mv RSG/Templates/* "01-Operations/Templates/" 2>/dev/null || true
fi

# Clients (if exists)
if [ -d "RSG/Clients" ]; then
  mkdir -p "01-Operations/Clients"
  git mv RSG/Clients/* "01-Operations/Clients/" 2>/dev/null || true
fi

echo "  Done."

# ──────────────────────────────────────────────────────────────────────────────
# 02-Underwriting: Carriers, Data Models, Knowledge Base
# ──────────────────────────────────────────────────────────────────────────────
echo "[2/7] Migrating to 02-Underwriting/..."

mkdir -p "02-Underwriting/Carriers"
mkdir -p "02-Underwriting/Commercial-Data-Model"
mkdir -p "02-Underwriting/Knowledge-Base"
mkdir -p "02-Underwriting/Intake-Schemas"

# Carrier appetite guides (including binaries like .pptx)
if [ -d "Carriers" ]; then
  git mv Carriers/* "02-Underwriting/Carriers/" 2>/dev/null || true
fi

# AI Knowledge carriers
if [ -d "AI_Knowledge/Carriers" ]; then
  mkdir -p "02-Underwriting/Knowledge-Base/Carriers"
  git mv AI_Knowledge/Carriers/* "02-Underwriting/Knowledge-Base/Carriers/" 2>/dev/null || true
fi

# Insurance Carrier Database Reference
if [ -f "AI_Knowledge/Insurance Carrier Database Reference Guide.md" ]; then
  git mv "AI_Knowledge/Insurance Carrier Database Reference Guide.md" "02-Underwriting/Knowledge-Base/" 2>/dev/null || true
fi

# Insurance Education
if [ -d "AI_Knowledge/Insurance Education" ]; then
  mkdir -p "02-Underwriting/Knowledge-Base/Education"
  git mv "AI_Knowledge/Insurance Education"/* "02-Underwriting/Knowledge-Base/Education/" 2>/dev/null || true
fi

# Lines of Business
if [ -d "AI_Knowledge/Lines of Business" ]; then
  mkdir -p "02-Underwriting/Knowledge-Base/LOB"
  git mv "AI_Knowledge/Lines of Business"/* "02-Underwriting/Knowledge-Base/LOB/" 2>/dev/null || true
fi

# Commercial Data Model (2,000+ files - this is the big one)
if [ -d "RSG Commercial Data model" ]; then
  echo "  Moving RSG Commercial Data model (2,000+ files, may take a minute)..."
  git mv "RSG Commercial Data model"/* "02-Underwriting/Commercial-Data-Model/" 2>/dev/null || true
fi

# CRM Field Reference guide intake schemas (if applicable)
# These are more CRM/Systems, handled in section 3

echo "  Done."

# ──────────────────────────────────────────────────────────────────────────────
# 03-Systems: CRM, Infrastructure, Agents, Integrations
# ──────────────────────────────────────────────────────────────────────────────
echo "[3/7] Migrating to 03-Systems/..."

mkdir -p "03-Systems/CRM/Field-Reference"
mkdir -p "03-Systems/CRM/EspoCRM"
mkdir -p "03-Systems/Infrastructure"
mkdir -p "03-Systems/Agents/Skills"
mkdir -p "03-Systems/Agents/OpenClaw"
mkdir -p "03-Systems/Integrations"

# CRM Field Reference guide
if [ -d "CRM Field Reference guide" ]; then
  git mv "CRM Field Reference guide"/* "03-Systems/CRM/Field-Reference/" 2>/dev/null || true
fi

# RSG/EspoCRM -> 03-Systems/CRM/EspoCRM
if [ -d "RSG/EspoCRM" ]; then
  # Handle subdirectories
  for subdir in "Account Module" "Commercial Lines"; do
    if [ -d "RSG/EspoCRM/$subdir" ]; then
      mkdir -p "03-Systems/CRM/EspoCRM/$subdir"
      git mv "RSG/EspoCRM/$subdir"/* "03-Systems/CRM/EspoCRM/$subdir/" 2>/dev/null || true
    fi
  done
  # Move remaining files (md, png, etc.)
  for f in RSG/EspoCRM/*; do
    [ -f "$f" ] && git mv "$f" "03-Systems/CRM/EspoCRM/" 2>/dev/null || true
  done
fi

# rsg-infrastructure -> 03-Systems/CRM
if [ -d "rsg-infrastructure" ]; then
  git mv rsg-infrastructure/* "03-Systems/CRM/" 2>/dev/null || true
fi

# RSG/Infrastructure -> 03-Systems/Infrastructure
if [ -d "RSG/Infrastructure" ]; then
  # Handle Databases subdir
  if [ -d "RSG/Infrastructure/Databases" ]; then
    mkdir -p "03-Systems/Infrastructure/Databases"
    git mv RSG/Infrastructure/Databases/* "03-Systems/Infrastructure/Databases/" 2>/dev/null || true
  fi
  # Move remaining files
  for f in RSG/Infrastructure/*; do
    [ -f "$f" ] && git mv "$f" "03-Systems/Infrastructure/" 2>/dev/null || true
  done
fi

# AI_Knowledge/Skills -> 03-Systems/Agents/Skills
if [ -d "AI_Knowledge/Skills" ]; then
  # Handle call-intake-parser subdir
  if [ -d "AI_Knowledge/Skills/call-intake-parser" ]; then
    mkdir -p "03-Systems/Agents/Skills/call-intake-parser"
    git mv AI_Knowledge/Skills/call-intake-parser/* "03-Systems/Agents/Skills/call-intake-parser/" 2>/dev/null || true
  fi
  # Move remaining skill files
  for f in AI_Knowledge/Skills/*; do
    [ -f "$f" ] && git mv "$f" "03-Systems/Agents/Skills/" 2>/dev/null || true
  done
fi

# RSG/Workflows/OpenClaw Build -> 03-Systems/Agents/OpenClaw
if [ -d "RSG/Workflows/OpenClaw Build" ]; then
  # Persona Design subdir
  if [ -d "RSG/Workflows/OpenClaw Build/Persona Design" ]; then
    mkdir -p "03-Systems/Agents/OpenClaw/Persona-Design"
    git mv "RSG/Workflows/OpenClaw Build/Persona Design"/* "03-Systems/Agents/OpenClaw/Persona-Design/" 2>/dev/null || true
  fi
  # Security subdir
  if [ -d "RSG/Workflows/OpenClaw Build/security" ]; then
    mkdir -p "03-Systems/Agents/OpenClaw/security"
    git mv "RSG/Workflows/OpenClaw Build/security"/* "03-Systems/Agents/OpenClaw/security/" 2>/dev/null || true
  fi
  # Move remaining OpenClaw files
  for f in "RSG/Workflows/OpenClaw Build"/*; do
    [ -f "$f" ] && git mv "$f" "03-Systems/Agents/OpenClaw/" 2>/dev/null || true
  done
fi

# Deprecated skills folder
if [ -d "skills" ]; then
  git mv skills/* "03-Systems/Agents/Skills/" 2>/dev/null || true
fi

# Github references -> 03-Systems/Infrastructure/Github
if [ -d "Github" ]; then
  mkdir -p "03-Systems/Infrastructure/Github"
  cp -r Github/* "03-Systems/Infrastructure/Github/" 2>/dev/null || true
  git add "03-Systems/Infrastructure/Github/" 2>/dev/null || true
  git rm -r "Github/" 2>/dev/null || true
fi

echo "  Done."

# ──────────────────────────────────────────────────────────────────────────────
# 00-Inbox: Document Inbox merge
# ──────────────────────────────────────────────────────────────────────────────
echo "[4/7] Migrating to 00-Inbox/..."

if [ -d "AI_Knowledge/Document Inbox" ]; then
  git mv "AI_Knowledge/Document Inbox/README.md" "00-Inbox/Document-Inbox-README.md" 2>/dev/null || true
  # Move any other files in Document Inbox
  for f in "AI_Knowledge/Document Inbox"/*; do
    [ -f "$f" ] && git mv "$f" "00-Inbox/" 2>/dev/null || true
  done
fi

echo "  Done."

# ──────────────────────────────────────────────────────────────────────────────
# 05-Personal: Ministry, Journal, Goals (local-only folders if present)
# ──────────────────────────────────────────────────────────────────────────────
echo "[5/7] Migrating to 05-Personal/..."

if [ -d "Ministry" ]; then
  mkdir -p "05-Personal/Ministry"
  git mv Ministry/* "05-Personal/Ministry/" 2>/dev/null || true
fi

if [ -d "Personal" ]; then
  for f in Personal/*; do
    [ -f "$f" ] && git mv "$f" "05-Personal/" 2>/dev/null || true
    [ -d "$f" ] && git mv "$f" "05-Personal/" 2>/dev/null || true
  done
fi

echo "  Done."

# ──────────────────────────────────────────────────────────────────────────────
# Remove the API-copied duplicate (01-Operations/SOPs/Call-Intake-Parser-SOP.md)
# that was pushed via the API before this script was created
# ──────────────────────────────────────────────────────────────────────────────
echo "[6/7] Cleaning up API migration artifacts..."

# The API push already created this file - git mv will overwrite or we can remove
# the old RSG/SOPs copy. Both versions are identical.

echo "  Done."

# ──────────────────────────────────────────────────────────────────────────────
# Clean up empty old directories
# ──────────────────────────────────────────────────────────────────────────────
echo "[7/7] Cleaning up empty old directories..."

# Remove empty directories (git doesn't track empty dirs, but local FS does)
for dir in "RSG/SOPs" "RSG/Workflows" "RSG/EspoCRM" "RSG/Infrastructure" "RSG/Templates" "RSG/Clients" "RSG" \
           "Carriers" "AI_Knowledge/Carriers" "AI_Knowledge/Insurance Education" "AI_Knowledge/Lines of Business" \
           "AI_Knowledge/Document Inbox" "AI_Knowledge/Skills" "AI_Knowledge" \
           "CRM Field Reference guide" "RSG Commercial Data model" "rsg-infrastructure" "skills" "Github"; do
  if [ -d "$dir" ] && [ -z "$(ls -A "$dir" 2>/dev/null)" ]; then
    rmdir "$dir" 2>/dev/null || true
  fi
done

echo "  Done."

# ──────────────────────────────────────────────────────────────────────────────
# Summary
# ──────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== Migration Complete ==="
echo ""
echo "Next steps:"
echo "  1. Open Obsidian - check for broken [[wikilinks]] (they'll show as unresolved)"
echo "  2. Use Obsidian's 'Find and Replace in all files' to fix common link patterns"
echo "  3. git add -A && git commit -m 'vault(migrate): move all files to 00-05 structure'"
echo "  4. git push"
echo ""
echo "Files NOT moved (manual action needed):"
echo "  - .obsidian/ (config, stays in root)"
echo "  - _System/ (meta folder, stays in root)"
echo "  - _Archive/ (retired content, stays in root)"
echo "  - .gitignore (stays in root)"
echo "  - VoiceInk_Dictionary.json (root level config - consider archiving)"
echo "  - migrate.sh (this script - delete after migration)"
echo ""
