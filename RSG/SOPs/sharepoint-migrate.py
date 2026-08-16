#!/usr/bin/env python3
"""Migrate SharePoint content into RSG Knowledge Site folder structure."""

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HOST = "riskintranet.sharepoint.com"

FOLDER_STRUCTURE = [
    "01-Carriers/Appetites",
    "01-Carriers/Commissions",
    "01-Carriers/Contacts",
    "02-Lines-of-Business/Commercial-Auto",
    "02-Lines-of-Business/General-Liability",
    "02-Lines-of-Business/Workers-Comp",
    "02-Lines-of-Business/Property",
    "02-Lines-of-Business/BOP",
    "02-Lines-of-Business/Medicare",
    "03-Operations/SOPs",
    "03-Operations/Workflows",
    "03-Operations/Roles",
    "03-Operations/Finance",
    "03-Operations/Current-Projects",
    "04-Client-Service/Intake-Templates",
    "04-Client-Service/Call-Scripts",
    "04-Client-Service/FAQ",
    "05-Marketing/Brand-Guide/Branding-Files",
    "05-Marketing/Brand-Guide/Images",
    "05-Marketing/Brand-Guide/Logos",
    "05-Marketing/Brand-Guide/Documents",
    "05-Marketing/Brand-Guide/Social-Media",
    "05-Marketing/Marketing-Assets",
    "05-Marketing/Newsletters",
    "05-Marketing/Presentations",
    "05-Marketing/Press-Kit",
    "05-Marketing/Widget-Assets",
    "06-Training/Onboarding",
    "06-Training/Insurance-Education",
    "07-Compliance/Licenses",
    "07-Compliance/Policies-Coverages",
    "08-CRM-and-Systems/CRM-Setup",
    "08-CRM-and-Systems/Codes-and-Prompts",
    "09-Archive/Migrated-from/BrandGuide",
    "09-Archive/Migrated-from/Root-Intranet",
]

RSG_REORG = {
    "Current projects": "03-Operations/Current-Projects",
    "Marketing assets": "05-Marketing/Marketing-Assets",
    "Newsletters": "05-Marketing/Newsletters",
    "Onboarding": "06-Training/Onboarding",
    "Presentations": "05-Marketing/Presentations",
    "Press kit": "05-Marketing/Press-Kit",
}

BRAND_GUIDE_MAP = {
    "Documents": "05-Marketing/Brand-Guide/Documents",
    "Branding files": "05-Marketing/Brand-Guide/Branding-Files",
    "Images": "05-Marketing/Brand-Guide/Images",
    "Social Media Posting Guide": "05-Marketing/Brand-Guide/Social-Media",
    "Logos": "05-Marketing/Brand-Guide/Logos",
}

ROOT_MAP = {
    "Talk Tracks": "04-Client-Service/Call-Scripts",
    "Media library": "03-Operations/SOPs",
    "WidgetBoard_Assets": "05-Marketing/Widget-Assets",
    "MyLinksIcons": "05-Marketing/Widget-Assets",
}


class GraphClient:
    def __init__(self):
        tenant = os.environ["MS365_TENANT_ID"]
        client_id = os.environ["MS365_CLIENT_ID"]
        client_secret = os.environ["MS365_CLIENT_SECRET"]
        token_data = urllib.parse.urlencode({
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }).encode()
        req = urllib.request.Request(
            f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
            data=token_data,
            method="POST",
        )
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        with urllib.request.urlopen(req) as resp:
            self.token = json.loads(resp.read().decode())["access_token"]

    def request(self, method, path, body=None, timeout=120):
        url = path if path.startswith("http") else f"https://graph.microsoft.com/v1.0{path}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        if body is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode()
                if resp.status == 202:
                    return 202, {"location": resp.headers.get("Location"), "accepted": True}
                return resp.status, json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            raw = e.read().decode()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {"message": raw}
            return e.code, payload

    def get_site(self, site_path):
        if site_path == ":":
            path = f"/sites/{HOST}"
        elif site_path.startswith(":/sites/"):
            path = f"/sites/{HOST}{site_path}"
        else:
            path = f"/sites/{HOST}:{site_path}"
        status, data = self.request("GET", path)
        if status != 200:
            raise RuntimeError(f"Site {site_path} failed: {data}")
        return data

    def get_drive(self, site_id, drive_name=None):
        status, data = self.request("GET", f"/sites/{site_id}/drives")
        if status != 200:
            raise RuntimeError(f"Drives failed: {data}")
        drives = data.get("value", [])
        if drive_name:
            for d in drives:
                if d["name"] == drive_name:
                    return d
            raise RuntimeError(f"Drive {drive_name} not found")
        return drives[0] if drives else None

    def encode_path(self, path):
        if not path:
            return path
        if path.startswith("/"):
            return "/" + "/".join(urllib.parse.quote(p, safe="") for p in path.strip("/").split("/"))
        return "/".join(urllib.parse.quote(p, safe="") for p in path.split("/"))

    def ensure_folder(self, drive_id, folder_path):
        encoded = self.encode_path(folder_path)
        status, data = self.request("GET", f"/drives/{drive_id}/root:{encoded}")
        if status == 200:
            return data["id"]
        parts = folder_path.strip("/").split("/")
        current = ""
        parent_id = "root"
        for part in parts:
            current = f"{current}/{part}" if current else part
            enc = self.encode_path(f"/{current}")
            status, data = self.request("GET", f"/drives/{drive_id}/root:{enc}")
            if status == 200:
                parent_id = data["id"]
                continue
            if parent_id == "root":
                endpoint = f"/drives/{drive_id}/root/children"
            else:
                endpoint = f"/drives/{drive_id}/items/{parent_id}/children"
            status, data = self.request("POST", endpoint, {
                "name": part,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "fail",
            })
            if status not in (200, 201):
                status2, data2 = self.request("GET", f"/drives/{drive_id}/root:{enc}")
                if status2 == 200:
                    parent_id = data2["id"]
                    continue
                raise RuntimeError(f"Create folder {current} failed: {data}")
            parent_id = data["id"]
        return parent_id

    def list_children(self, drive_id, folder_path=None):
        if folder_path:
            enc = self.encode_path(folder_path if folder_path.startswith("/") else f"/{folder_path}")
            path = f"/drives/{drive_id}/root:{enc}:/children?$top=200"
        else:
            path = f"/drives/{drive_id}/root/children?$top=200"
        status, data = self.request("GET", path)
        return data.get("value", []) if status == 200 else []

    def copy_item(self, source_drive_id, item_id, dest_drive_id, dest_folder_path, name=None):
        dest_folder_id = self.ensure_folder(dest_drive_id, dest_folder_path)
        body = {
            "parentReference": {"driveId": dest_drive_id, "id": dest_folder_id},
            "@microsoft.graph.conflictBehavior": "rename",
        }
        if name:
            body["name"] = name
        status, data = self.request(
            "POST",
            f"/drives/{source_drive_id}/items/{item_id}/copy",
            body,
        )
        return status in (200, 201, 202), data

    def move_item(self, drive_id, item_id, dest_folder_path):
        dest_folder_id = self.ensure_folder(drive_id, dest_folder_path)
        status, data = self.request("PATCH", f"/drives/{drive_id}/items/{item_id}", {
            "parentReference": {"id": dest_folder_id},
        })
        return status == 200, data

    def walk_drive(self, drive_id, folder_path=None, rel_path=""):
        items = []
        for child in self.list_children(drive_id, folder_path):
            name = child["name"]
            child_rel = f"{rel_path}/{name}" if rel_path else name
            if child.get("folder"):
                sub_path = f"{folder_path}/{name}" if folder_path else f"/{name}"
                items.extend(self.walk_drive(drive_id, sub_path, child_rel))
            else:
                items.append({
                    "id": child["id"],
                    "name": name,
                    "path": child_rel,
                    "size": child.get("size", 0),
                })
        return items


def main():
    g = GraphClient()
    log = []
    stats = {"folders_created": 0, "copied": 0, "moved": 0, "failed": 0, "skipped": 0}

    def record(action, source, target, status, detail=""):
        log.append({
            "time": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "source": source,
            "target": target,
            "status": status,
            "detail": str(detail)[:300],
        })
        print(f"[{status}] {action}: {source} -> {target}" + (f" ({detail})" if detail else ""))

    # Target site
    rsg_site = g.get_site(":/sites/RSG")
    rsg_drive = g.get_drive(rsg_site["id"], "Documents")
    rsg_drive_id = rsg_drive["id"]

    print("Creating folder structure...")
    for folder in FOLDER_STRUCTURE:
        try:
            g.ensure_folder(rsg_drive_id, folder)
            stats["folders_created"] += 1
            record("create_folder", folder, folder, "ok")
        except Exception as e:
            record("create_folder", folder, folder, "failed", e)
            stats["failed"] += 1

    # Reorganize existing RSG folders (move within same drive)
    print("\nReorganizing existing RSG folders...")
    for old_name, new_path in RSG_REORG.items():
        children = g.list_children(rsg_drive_id)
        match = next((c for c in children if c["name"] == old_name), None)
        if not match:
            record("move", old_name, new_path, "skipped", "not found")
            stats["skipped"] += 1
            continue
        ok, detail = g.move_item(rsg_drive_id, match["id"], new_path)
        if ok:
            stats["moved"] += 1
            record("move", old_name, new_path, "ok")
        else:
            stats["failed"] += 1
            record("move", old_name, new_path, "failed", detail)

    # Migrate Brand Guide
    print("\nMigrating Brand Guide...")
    try:
        bg_site = g.get_site(":/sites/BrandGuide")
        bg_drives = g.request("GET", f"/sites/{bg_site['id']}/drives")[1].get("value", [])
        for drive in bg_drives:
            dest_base = BRAND_GUIDE_MAP.get(drive["name"], "05-Marketing/Brand-Guide/Documents")
            files = g.walk_drive(drive["id"])
            print(f"  {drive['name']}: {len(files)} files -> {dest_base}")
            for f in files:
                ok, detail = g.copy_item(drive["id"], f["id"], rsg_drive_id, dest_base, f["name"])
                if ok:
                    stats["copied"] += 1
                    record("copy", f"BrandGuide/{drive['name']}/{f['path']}", dest_base, "ok")
                else:
                    stats["failed"] += 1
                    record("copy", f"BrandGuide/{drive['name']}/{f['path']}", dest_base, "failed", detail)
                time.sleep(0.3)
    except Exception as e:
        record("copy", "BrandGuide", "05-Marketing/Brand-Guide", "failed", e)
        stats["failed"] += 1

    # Migrate root intranet libraries
    print("\nMigrating root intranet...")
    try:
        root_site = g.get_site(":")
        root_drives = g.request("GET", f"/sites/{root_site['id']}/drives")[1].get("value", [])
        for drive in root_drives:
            dest_base = ROOT_MAP.get(drive["name"])
            if not dest_base:
                record("copy", f"root/{drive['name']}", "-", "skipped", "no mapping")
                stats["skipped"] += 1
                continue
            files = g.walk_drive(drive["id"])
            print(f"  {drive['name']}: {len(files)} files -> {dest_base}")
            for f in files:
                ok, detail = g.copy_item(drive["id"], f["id"], rsg_drive_id, dest_base, f["name"])
                if ok:
                    stats["copied"] += 1
                    record("copy", f"root/{drive['name']}/{f['path']}", dest_base, "ok")
                else:
                    stats["failed"] += 1
                    record("copy", f"root/{drive['name']}/{f['path']}", dest_base, "failed", detail)
                time.sleep(0.3)
    except Exception as e:
        record("copy", "root intranet", "RSG", "failed", e)
        stats["failed"] += 1

    # Migrate coverages and agencyfinance if they have files
    for site_name, dest in [("coverages", "07-Compliance/Policies-Coverages"), ("agencyfinance", "03-Operations/Finance")]:
        print(f"\nMigrating {site_name}...")
        try:
            site = g.get_site(f":/sites/{site_name}")
            drives = g.request("GET", f"/sites/{site['id']}/drives")[1].get("value", [])
            for drive in drives:
                files = g.walk_drive(drive["id"])
                if not files:
                    continue
                print(f"  {drive['name']}: {len(files)} files")
                for f in files:
                    ok, detail = g.copy_item(drive["id"], f["id"], rsg_drive_id, dest, f["name"])
                    if ok:
                        stats["copied"] += 1
                        record("copy", f"{site_name}/{f['path']}", dest, "ok")
                    else:
                        stats["failed"] += 1
                        record("copy", f"{site_name}/{f['path']}", dest, "failed", detail)
                    time.sleep(0.3)
        except Exception as e:
            record("copy", site_name, dest, "failed", e)
            stats["failed"] += 1

    # Write migration log
    report_dir = os.path.join(os.path.dirname(__file__), "..", "Reports")
    os.makedirs(report_dir, exist_ok=True)
    log_path = os.path.join(report_dir, "migration-execution-log.json")
    with open(log_path, "w") as f:
        json.dump({"stats": stats, "entries": log}, f, indent=2)

    summary_path = os.path.join(report_dir, "migration-completion-report.md")
    with open(summary_path, "w") as f:
        f.write("# SharePoint Migration Completion Report\n\n")
        f.write(f"**Completed:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n")
        f.write("## Stats\n\n")
        f.write(f"- Folders created: {stats['folders_created']}\n")
        f.write(f"- Files copied: {stats['copied']}\n")
        f.write(f"- Folders moved (RSG reorg): {stats['moved']}\n")
        f.write(f"- Skipped: {stats['skipped']}\n")
        f.write(f"- Failed: {stats['failed']}\n\n")
        f.write("## Migrated sources\n\n")
        f.write("| Source | Destination |\n|--------|-------------|\n")
        f.write("| Brand Guide (all libraries) | 05-Marketing/Brand-Guide/* |\n")
        f.write("| Root: Talk Tracks | 04-Client-Service/Call-Scripts |\n")
        f.write("| Root: Media library | 03-Operations/SOPs |\n")
        f.write("| Root: WidgetBoard_Assets | 05-Marketing/Widget-Assets |\n")
        f.write("| RSG: Current projects | 03-Operations/Current-Projects |\n")
        f.write("| RSG: Marketing assets | 05-Marketing/Marketing-Assets |\n")
        f.write("| RSG: Newsletters | 05-Marketing/Newsletters |\n")
        f.write("| RSG: Onboarding | 06-Training/Onboarding |\n")
        f.write("| RSG: Presentations | 05-Marketing/Presentations |\n")
        f.write("| RSG: Press kit | 05-Marketing/Press-Kit |\n\n")
        f.write("## Deferred (manual Loop export)\n\n")
        f.write("30 Loop workspaces including Carriers, UW questions, Workflows, When a client calls in, Kim Onboarding Guide, etc.\n\n")
        f.write("## Next steps\n\n")
        f.write("1. Lamar exports Loop workspaces manually into target RSG folders\n")
        f.write("2. Point Amy SharePoint grounding at RSG/Documents (folders 01-07)\n")
        f.write("3. Run Supabase ingestion (P0: Carriers, SOPs, Commissions)\n")
        f.write("4. Delete Tier 1 Loop sites after confirming migration\n")

    print("\n=== MIGRATION COMPLETE ===")
    print(json.dumps(stats, indent=2))
    print(f"Log: {log_path}")
    print(f"Report: {summary_path}")


if __name__ == "__main__":
    main()
