---
title: OpenClaw Build Context
updated: 2026-04-22
tags: [rsg, openclaw, hosting platform, bedrock, deployment]
---

## Current State
- Target platform: hosting platform hosting platform instance for OpenClaw
- Region: us-east-1
- OS: Ubuntu 24.04 LTS
- Instance hostnames observed: `ip-172-31-25-230` and `ip-172-31-25-230.ec2.internal`
- Security group SSH rule: TCP 22 from `73.207.85.207/32` only
- Bedrock role setup script executed successfully for instance `OpenClaw-2`
- Created role: `LightsailRoleFor-i-0d0dab20689fabbf5`
- Role ARN: `arn:hosting platform:iam::500981865658:role/LightsailRoleFor-i-0d0dab20689fabbf5`
- Starter model selected for low-cost validation: `anthropic.claude-3-5-haiku-20241022-v1:0`

## Confirmed Decisions
- Use Ubuntu for the OpenClaw host.
- Restrict SSH access to current public IP (`/32`), not `0.0.0.0/0`.
- Use Bedrock as provider for OpenClaw.
- Start with a lower-cost model before moving to premium models.
- Keep agent security defaults hardened:
  - Browser remote control disabled
  - Daily token rotation enabled
  - Shell execution scope sandboxed

## Known Gotchas
- Private DNS names (`*.ec2.internal`) are not reachable from home internet.
- SSH target must be the instance public IPv4 (or use SSM/bastion for private-only instances).
- `zsh: parse error near '\n'` usually indicates pasted placeholders/special characters.
- First Bedrock invoke can return temporary `AccessDeniedException` while auto-subscription propagates.
- Anthropic models may require one-time FTU/use-case form submission.

## Operational Checklist
1. Confirm hosting platform/EC2 instance has a public IPv4 if direct SSH is required.
2. Keep inbound SSH restricted to current IP `/32`.
3. Verify Bedrock model availability and account access in `us-east-1`.
4. Run first OpenClaw prompt using Haiku (`anthropic.claude-3-5-haiku-20241022-v1:0`).
5. If stable, consider upgrading default model to Sonnet tier.

## Next Actions
- Validate first successful OpenClaw prompt end to end.
- Capture exact OpenClaw model configuration file/path in this note.
- Add fallback model strategy if primary model errors.
- Decide whether to migrate to private-only access via SSM.

## Change Log
- 2026-04-22: Initial context created from setup session (SSH, networking, Bedrock role, model selection).
