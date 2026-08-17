#!/usr/bin/env python3
"""Build RSG Knowledge Base site UI: homepage, section pages, cleanup."""

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HOST = "riskintranet.sharepoint.com"
SITE_PATH = "/sites/RSG"
BASE_URL = f"https://{HOST}{SITE_PATH}"

SECTIONS = [
    {
        "num": "01",
        "slug": "01-Carriers",
        "title": "Carriers",
        "folder": "01-Carriers",
        "desc": "Carrier appetite guides, commission schedules, UW contacts, and underwriting references.",
        "subs": ["Appetites", "Commissions", "Contacts"],
        "loop_drop": ["Carriers", "UW questions"],
        "color": "#0078d4",
    },
    {
        "num": "02",
        "slug": "02-Lines-of-Business",
        "title": "Lines of Business",
        "folder": "02-Lines-of-Business",
        "desc": "Commercial Auto, GL, Workers Comp, Property, BOP, and Medicare education.",
        "subs": ["Commercial-Auto", "General-Liability", "Workers-Comp", "Property", "BOP", "Medicare"],
        "loop_drop": ["Medicare Rollout"],
        "color": "#107c10",
    },
    {
        "num": "03",
        "slug": "03-Operations",
        "title": "Operations",
        "folder": "03-Operations",
        "desc": "SOPs, workflows, role definitions, finance, and current projects.",
        "subs": ["SOPs", "Workflows", "Roles", "Finance", "Current-Projects"],
        "loop_drop": ["Workflows", "Roles and responsibilites", "Current Operations Manager Tasks", "Intranet Notes"],
        "color": "#5c2d91",
    },
    {
        "num": "04",
        "slug": "04-Client-Service",
        "title": "Client Service",
        "folder": "04-Client-Service",
        "desc": "Call scripts, intake templates, talk tracks, and internal FAQ.",
        "subs": ["Intake-Templates", "Call-Scripts", "FAQ"],
        "loop_drop": ["When a client calls in"],
        "color": "#d83b01",
    },
    {
        "num": "05",
        "slug": "05-Marketing",
        "title": "Marketing",
        "folder": "05-Marketing",
        "desc": "Brand guide, logos, presentations, newsletters, press kit, and widget assets.",
        "subs": ["Brand-Guide", "Marketing-Assets", "Newsletters", "Presentations", "Press-Kit", "Widget-Assets"],
        "loop_drop": ["Agency growth", "Leads Gen"],
        "color": "#e3008c",
    },
    {
        "num": "06",
        "slug": "06-Training",
        "title": "Training",
        "folder": "06-Training",
        "desc": "Onboarding guides, insurance education, and CE material.",
        "subs": ["Onboarding", "Insurance-Education"],
        "loop_drop": ["Kim Onboarding Guide"],
        "color": "#008272",
    },
    {
        "num": "07",
        "slug": "07-Compliance",
        "title": "Compliance",
        "folder": "07-Compliance",
        "desc": "Agency licenses, policies, coverages, and regulatory references.",
        "subs": ["Licenses", "Policies-Coverages"],
        "loop_drop": ["Agency Licenses and Insurance"],
        "color": "#a4262c",
    },
]

SAMPLE_PAGES = [
    "Culture.aspx",
    "Our-Leadership.aspx",
    "Our-teams.aspx",
    "Vision-and-Priorities.aspx",
    "DepartmentHome.aspx",
]


class Graph:
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

    def call(self, method, path, body=None, beta=False):
        base = "https://graph.microsoft.com/beta" if beta else "https://graph.microsoft.com/v1.0"
        url = path if path.startswith("http") else f"{base}{path}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        if body is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = resp.read().decode()
                return resp.status, json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            raw = e.read().decode()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                payload = {"message": raw}
            return e.code, payload

    def encode_path(self, path):
        if not path:
            return path
        if path.startswith("/"):
            return "/" + "/".join(urllib.parse.quote(p, safe="") for p in path.strip("/").split("/"))
        return "/".join(urllib.parse.quote(p, safe="") for p in path.split("/"))

    def list_children(self, drive_id, folder_path=None):
        if folder_path:
            enc = self.encode_path(folder_path if folder_path.startswith("/") else f"/{folder_path}")
            path = f"/drives/{drive_id}/root:{enc}:/children?$top=200&$select=name,size,webUrl,file,folder,lastModifiedDateTime"
        else:
            path = f"/drives/{drive_id}/root/children?$top=200&$select=name,size,webUrl,file,folder,lastModifiedDateTime"
        status, data = self.call("GET", path)
        return data.get("value", []) if status == 200 else []

    def walk_files(self, drive_id, folder_path=None, rel="", depth=0, max_depth=4, max_files=30):
        files = []
        if depth > max_depth:
            return files
        for item in self.list_children(drive_id, folder_path):
            if len(files) >= max_files:
                break
            name = item["name"]
            child_rel = f"{rel}/{name}" if rel else name
            if item.get("folder"):
                sub = f"{folder_path}/{name}" if folder_path else f"/{name}"
                files.extend(self.walk_files(drive_id, sub, child_rel, depth + 1, max_depth, max_files - len(files)))
            else:
                files.append({
                    "name": name,
                    "path": child_rel,
                    "url": item.get("webUrl", ""),
                    "size": item.get("size", 0),
                    "modified": (item.get("lastModifiedDateTime") or "")[:10],
                })
        return files


def esc(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def folder_url(folder):
    return f"{BASE_URL}/Shared%20Documents/{urllib.parse.quote(folder)}"


def page_url(name):
    return f"{BASE_URL}/SitePages/{name}"


def text_webpart(html):
    return {"@odata.type": "#microsoft.graph.textWebPart", "innerHtml": html}


def canvas(html):
    return {
        "horizontalSections": [{
            "layout": "oneColumn",
            "columns": [{"width": 12, "webparts": [text_webpart(html)]}],
        }]
    }


def build_home_html(section_files):
    cards = []
    for s in SECTIONS:
        count = len(section_files.get(s["folder"], []))
        cards.append(f"""
        <div style="border-left:6px solid {s['color']};padding:16px 20px;margin:12px 0;background:#f8f9fa;border-radius:4px;">
          <h2 style="margin:0 0 6px 0;"><a href="{page_url(s['slug'] + '.aspx')}" style="color:{s['color']};text-decoration:none;">{s['num']} — {esc(s['title'])}</a></h2>
          <p style="margin:0 0 8px 0;color:#444;">{esc(s['desc'])}</p>
          <p style="margin:0;font-size:13px;">
            <a href="{folder_url(s['folder'])}">Open folder</a>
            &nbsp;|&nbsp; {count} file{'s' if count != 1 else ''} migrated
          </p>
        </div>""")

    return f"""
<div style="max-width:960px;margin:0 auto;font-family:'Segoe UI',sans-serif;">
  <div style="background:linear-gradient(135deg,#0078d4 0%,#005a9e 100%);color:#fff;padding:32px 28px;border-radius:8px;margin-bottom:24px;">
    <h1 style="margin:0 0 8px 0;font-size:32px;">RSG Knowledge Base</h1>
    <p style="margin:0;font-size:16px;opacity:0.95;">Risk Solutions Group — single source of truth for carriers, operations, client service, and agency knowledge.</p>
  </div>

  <div style="background:#fff4ce;border:1px solid #f0c800;padding:14px 18px;border-radius:4px;margin-bottom:20px;">
    <strong>Adding knowledge:</strong> Drop files into the numbered folders below, or export Loop workspaces into the matching section.
    Amy (Copilot) reads folders <strong>01–07</strong>.
  </div>

  <h2 style="border-bottom:2px solid #0078d4;padding-bottom:6px;">Knowledge Sections</h2>
  {''.join(cards)}

  <div style="margin-top:32px;padding:20px;background:#f3f2f1;border-radius:4px;">
    <h3 style="margin-top:0;">Quick links</h3>
    <ul>
      <li><a href="{folder_url('08-CRM-and-Systems')}">08 — CRM &amp; Systems</a> (internal AI configs — not ingested by Amy)</li>
      <li><a href="{folder_url('09-Archive')}">09 — Archive</a> (migrated originals)</li>
      <li><a href="{BASE_URL}/Shared%20Documents/Forms/AllItems.aspx">Browse all documents</a></li>
    </ul>
  </div>

  <p style="color:#666;font-size:12px;margin-top:24px;">Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>
</div>"""


def build_section_html(section, files):
    sub_links = []
    for sub in section["subs"]:
        sub_path = f"{section['folder']}/{sub}"
        sub_links.append(f'<li><a href="{folder_url(sub_path)}">{esc(sub.replace("-", " "))}</a></li>')

    file_rows = []
    for f in sorted(files, key=lambda x: x["name"].lower())[:25]:
        size_kb = f["size"] / 1024
        size_str = f"{size_kb:.0f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
        link = f'<a href="{esc(f["url"])}">{esc(f["name"])}</a>' if f["url"] else esc(f["name"])
        file_rows.append(f"<tr><td>{link}</td><td>{esc(f['path'])}</td><td>{size_str}</td><td>{f['modified']}</td></tr>")

    loop_items = "".join(f"<li><strong>{esc(l)}</strong> → drop into this section after Loop export</li>" for l in section["loop_drop"])

    files_table = ""
    if file_rows:
        files_table = f"""
        <h3>Key documents ({len(files)} total)</h3>
        <table style="width:100%;border-collapse:collapse;font-size:14px;">
          <tr style="background:#f3f2f1;"><th style="text-align:left;padding:8px;">File</th><th style="text-align:left;padding:8px;">Path</th><th>Size</th><th>Modified</th></tr>
          {''.join(file_rows)}
        </table>"""
    else:
        files_table = """
        <div style="background:#fff4ce;padding:14px;border-radius:4px;">
          <strong>No files yet.</strong> Export Loop content or upload documents to this section's folder.
        </div>"""

    return f"""
<div style="max-width:960px;margin:0 auto;font-family:'Segoe UI',sans-serif;">
  <p><a href="{page_url('Home.aspx')}">← Back to Knowledge Base Home</a></p>
  <div style="border-left:6px solid {section['color']};padding:20px 24px;background:#f8f9fa;border-radius:4px;margin-bottom:20px;">
    <h1 style="margin:0 0 8px 0;color:{section['color']};">{section['num']} — {esc(section['title'])}</h1>
    <p style="margin:0 0 12px 0;">{esc(section['desc'])}</p>
    <p><a href="{folder_url(section['folder'])}" style="font-weight:bold;">Open {esc(section['folder'])} folder →</a></p>
  </div>

  <h3>Subfolders</h3>
  <ul>{''.join(sub_links)}</ul>

  <h3>Loop workspaces to export here</h3>
  <ul>{loop_items}</ul>

  {files_table}
</div>"""


def upsert_page(g, site_id, name, title, html, existing_pages):
    page_name = name if name.endswith(".aspx") else f"{name}.aspx"
    body = {
        "@odata.type": "#microsoft.graph.sitePage",
        "name": page_name,
        "title": title,
        "pageLayout": "article",
        "showComments": False,
        "showRecommendedPages": False,
        "canvasLayout": canvas(html),
    }

    match = next((p for p in existing_pages if p.get("name") == page_name), None)
    if match:
        status, result = g.call(
            "PATCH",
            f"/sites/{site_id}/pages/{match['id']}/microsoft.graph.sitePage",
            {"title": title, "canvasLayout": canvas(html)},
        )
        action = "updated"
        page_id = match["id"]
    else:
        status, result = g.call("POST", f"/sites/{site_id}/pages", body)
        action = "created"
        page_id = result.get("id")

    if status not in (200, 201):
        return action, status, result

    pub_status, pub = g.call(
        "POST",
        f"/sites/{site_id}/pages/{page_id}/microsoft.graph.sitePage/publish",
        beta=True,
    )
    return action, pub_status, {"page_id": page_id, "name": page_name, "publish": pub}


def main():
    g = Graph()
    log = []

    status, site = g.call("GET", f"/sites/{HOST}:{SITE_PATH}")
    site_id = site["id"]

    # Rename site
    g.call("PATCH", f"/sites/{site_id}", {
        "displayName": "RSG Knowledge Base",
    })
    log.append("Renamed site to RSG Knowledge Base")

    # Get drives and scan files per section
    status, drives = g.call("GET", f"/sites/{site_id}/drives")
    docs_drive = next(d for d in drives["value"] if d["name"] == "Documents")
    drive_id = docs_drive["id"]

    section_files = {}
    for s in SECTIONS:
        section_files[s["folder"]] = g.walk_files(drive_id, f"/{s['folder']}", max_files=50)
        log.append(f"Scanned {s['folder']}: {len(section_files[s['folder']])} files")

    # List existing pages
    status, pages_data = g.call("GET", f"/sites/{site_id}/pages")
    existing_pages = pages_data.get("value", [])

    # Delete sample pages
    for page_name in SAMPLE_PAGES:
        match = next((p for p in existing_pages if p.get("name") == page_name), None)
        if match:
            st, res = g.call("DELETE", f"/sites/{site_id}/pages/{match['id']}")
            log.append(f"Delete {page_name}: {st}")
            if st == 204:
                existing_pages = [p for p in existing_pages if p["id"] != match["id"]]

    # Build homepage
    home_html = build_home_html(section_files)
    action, st, res = upsert_page(g, site_id, "Home.aspx", "RSG Knowledge Base", home_html, existing_pages)
    log.append(f"Homepage {action}: {st} {res}")

    # Build section pages
    for s in SECTIONS:
        html = build_section_html(s, section_files.get(s["folder"], []))
        page_name = f"{s['slug']}.aspx"
        title = f"{s['num']} — {s['title']}"
        action, st, res = upsert_page(g, site_id, page_name, title, html, existing_pages)
        log.append(f"Section {page_name} {action}: {st}")
        time.sleep(0.5)

    # Write log
    report_path = os.path.join(os.path.dirname(__file__), "..", "Reports", "knowledge-site-ui-build.json")
    with open(report_path, "w") as f:
        json.dump({"log": log, "site_path": SITE_PATH, "home_page": "SitePages/Home.aspx"}, f, indent=2)

    print("RSG Knowledge Base UI build complete")
    print(f"Site: {BASE_URL}")
    print(f"Home: {page_url('Home.aspx')}")
    for line in log:
        print(f"  {line}")


if __name__ == "__main__":
    main()
