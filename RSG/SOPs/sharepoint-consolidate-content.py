#!/usr/bin/env python3
"""Consolidate useful SharePoint pages from all sites into RSG Knowledge Base."""

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HOST = "riskintranet.sharepoint.com"
RSG_PATH = "/sites/RSG"
BASE = f"https://{HOST}{RSG_PATH}"

# Source site path -> RSG section folder prefix for new pages
SOURCE_SITES = {
    "homepage": ("Operations and Roles", "03-Operations"),
    "coverages": ("Policies & Coverages", "02-Lines-of-Business"),
    "BrandGuide": ("Brand Guide", "05-Marketing"),
    "": ("Root Intranet", None),  # root site
}

# Pages to skip (templates, empty, duplicates)
SKIP_TITLES = {
    "Home", "None", "Help center", "HomeForBrandCentral",
    "LearnHome", "Page", "Apps", "Formshome",
}
SKIP_NAME_PATTERNS = [r"^Page\(\d+\)\.aspx$", r"^Home_old\.aspx$", r"^try\.aspx$"]

# Manual overrides: (site_key, page_name) -> section prefix
PAGE_OVERRIDES = {
    ("homepage", "takingcalls.aspx"): "04-Client-Service",
    ("homepage", "Service-SOP.aspx"): "04-Client-Service",
    ("homepage", "Account Manager.aspx"): "04-Client-Service",
    ("homepage", "Commission-Guidelines.aspx"): "01-Carriers",
    ("homepage", "How-we-secure-policies.aspx"): "01-Carriers",
    ("homepage", "Employee-Handboook.aspx"): "06-Training",
    ("homepage", "Operations-and-Roles.aspx"): "06-Training",
    ("", "Contacts.aspx"): "01-Carriers",
    ("", "Contacts(1).aspx"): "01-Carriers",
    ("", "FAQs.aspx"): "04-Client-Service",
    ("", "Knowledge-Hub.aspx"): "03-Operations",
    ("", "Creating-a-Comprehensive-and-Searchable-Knowledge-Base-Wiki-for-Risk-Solutions-Group.aspx"): "03-Operations",
    ("", "Using-Agency-Zoom.aspx"): "08-CRM-and-Systems",
    ("", "Using-Agency-Zoom1.aspx"): "08-CRM-and-Systems",
    ("", "Using-QQ-Catalyst.aspx"): "08-CRM-and-Systems",
    ("", "Tools.aspx"): "08-CRM-and-Systems",
    ("BrandGuide", "Our-Brand-Strategy.aspx"): "05-Marketing",
    ("BrandGuide", "Marketing-Expression.aspx"): "05-Marketing",
    ("BrandGuide", "Help-Center.aspx"): "05-Marketing",
}


class Graph:
    def __init__(self):
        tenant = os.environ["MS365_TENANT_ID"]
        client_id = os.environ["MS365_CLIENT_ID"]
        client_secret = os.environ["MS365_CLIENT_SECRET"]
        data = urllib.parse.urlencode({
            "client_id": client_id, "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default", "grant_type": "client_credentials",
        }).encode()
        req = urllib.request.Request(
            f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
            data=data, method="POST",
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
                payload = {"message": raw[:500]}
            return e.code, payload


def esc(text):
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def slugify(title):
    s = re.sub(r"[^\w\s-]", "", title).strip().lower()
    s = re.sub(r"[\s_]+", "-", s)
    return s[:60] or "page"


def should_skip(title, name):
    if not title or title.strip() in SKIP_TITLES:
        return True
    for pat in SKIP_NAME_PATTERNS:
        if re.match(pat, name):
            return True
    return False


def extract_html(page_detail):
    parts = []
    canvas = page_detail.get("canvasLayout", {})
    for section in canvas.get("horizontalSections", []):
        for col in section.get("columns", []):
            for wp in col.get("webparts", []):
                html = wp.get("innerHtml") or ""
                if not html and wp.get("data"):
                    html = wp["data"].get("innerHtml", "") or wp["data"].get("description", "")
                if html and html.strip():
                    parts.append(html)
    if parts:
        return "\n".join(parts)
    # Fallback: page description (search snippet with real content)
    desc = page_detail.get("description", "")
    if desc and len(desc) > 30:
        return f"<p>{esc(desc)}</p>"
    return ""


def wrap_imported_page(title, html, source_site, source_url, section):
    if not html.strip():
        html = "<p><em>This page had no extractable content. Check the source site.</em></p>"
    return f"""
<div style="max-width:960px;margin:0 auto;font-family:'Segoe UI',sans-serif;">
  <p><a href="{BASE}/SitePages/Home.aspx">← Knowledge Base Home</a>
     &nbsp;|&nbsp; <a href="{BASE}/SitePages/{section.split('/')[0].replace(' ', '-')}.aspx">{esc(section.split('/')[0])}</a></p>
  <div style="background:#f3f2f1;padding:10px 14px;border-radius:4px;margin-bottom:16px;font-size:13px;">
    Imported from <strong>{esc(source_site)}</strong>
    {f' · <a href="{esc(source_url)}">View original</a>' if source_url else ''}
  </div>
  <h1>{esc(title)}</h1>
  {html}
</div>"""


def canvas(html):
    return {
        "horizontalSections": [{
            "layout": "oneColumn",
            "columns": [{"width": 12, "webparts": [{"@odata.type": "#microsoft.graph.textWebPart", "innerHtml": html}]}],
        }]
    }


def list_to_html(g, site_id, list_id, list_name, max_items=50):
    rows = []
    status, data = g.call("GET", f"/sites/{site_id}/lists/{list_id}/items?$expand=fields&$top={max_items}")
    if status != 200:
        return ""
    for item in data.get("value", []):
        fields = item.get("fields", {})
        cells = []
        for k, v in fields.items():
            if k.startswith("@") or k in ("id", "ContentType", "Modified", "Created", "AuthorLookupId", "EditorLookupId"):
                continue
            if v and str(v).strip() and not str(v).startswith("{"):
                cells.append(f"<strong>{esc(k)}:</strong> {esc(str(v)[:500])}")
        if cells:
            rows.append(f"<li>{'<br/>'.join(cells)}</li>")
    if not rows:
        return ""
    return f"<h2>{esc(list_name)}</h2><ul>{''.join(rows)}</ul>"


def create_page(g, rsg_site_id, name, title, html, existing_names):
    page_name = name if name.endswith(".aspx") else f"{name}.aspx"
    # Avoid duplicates
    base = page_name.replace(".aspx", "")
    counter = 1
    while page_name in existing_names:
        page_name = f"{base}-{counter}.aspx"
        counter += 1

    body = {
        "@odata.type": "#microsoft.graph.sitePage",
        "name": page_name,
        "title": title,
        "pageLayout": "article",
        "showComments": False,
        "showRecommendedPages": False,
        "canvasLayout": canvas(html),
    }
    status, result = g.call("POST", f"/sites/{rsg_site_id}/pages", body)
    if status not in (200, 201):
        return None, status, result
    page_id = result["id"]
    g.call("POST", f"/sites/{rsg_site_id}/pages/{page_id}/microsoft.graph.sitePage/publish", beta=True)
    existing_names.add(page_name)
    return page_name, status, result


def get_site(g, site_key):
    if site_key == "":
        path = f"/sites/{HOST}"
    else:
        path = f"/sites/{HOST}:/sites/{site_key}"
    status, site = g.call("GET", path)
    if status != 200:
        raise RuntimeError(f"Site {site_key}: {site}")
    return site


def main():
    g = Graph()
    rsg = get_site(g, "RSG")
    rsg_id = rsg["id"]

    status, pages_data = g.call("GET", f"/sites/{rsg_id}/pages")
    existing_names = {p["name"] for p in pages_data.get("value", [])}

    imported = []
    skipped = []
    failed = []

    # Import pages from each source site
    for site_key, (site_label, default_section) in SOURCE_SITES.items():
        try:
            site = get_site(g, site_key)
        except RuntimeError as e:
            failed.append({"site": site_key, "error": str(e)})
            continue

        site_id = site["id"]
        site_url = site.get("webUrl", "")

        status, pages = g.call("GET", f"/sites/{site_id}/pages")
        if status != 200:
            failed.append({"site": site_key, "error": pages})
            continue

        print(f"\n=== {site_label} ({len(pages.get('value', []))} pages) ===")

        for p in pages.get("value", []):
            title = p.get("title", "")
            name = p.get("name", "")
            if should_skip(title, name):
                skipped.append({"site": site_label, "title": title, "name": name, "reason": "skip list"})
                continue

            section = PAGE_OVERRIDES.get((site_key, name), default_section)
            if not section:
                # Root site: categorize by title keywords
                t = title.lower()
                if any(k in t for k in ["carrier", "commission", "contact"]):
                    section = "01-Carriers"
                elif any(k in t for k in ["commercial", "homeowner", "auto", "property", "wc", "work comp", "medicare", "liability", "flood", "life", "pet", "umbrella", "coverage", "insurance"]):
                    section = "02-Lines-of-Business"
                elif any(k in t for k in ["faq", "call", "client", "service", "personal line"]):
                    section = "04-Client-Service"
                elif any(k in t for k in ["brand", "marketing", "meet the team"]):
                    section = "05-Marketing"
                elif any(k in t for k in ["training", "onboard", "handbook", "meeting", "agenda"]):
                    section = "06-Training"
                elif any(k in t for k in ["tool", "agency zoom", "qq", "catalyst"]):
                    section = "08-CRM-and-Systems"
                else:
                    section = "03-Operations"

            # Get full page content (no $expand — canvasLayout unavailable via app permissions)
            status, detail = g.call("GET", f"/sites/{site_id}/pages/{p['id']}")
            if status != 200:
                failed.append({"site": site_label, "title": title, "error": detail})
                continue

            html_content = extract_html(detail)
            source_page_url = detail.get("webUrl", p.get("webUrl", ""))
            if source_page_url:
                html_content += (
                    f'<p style="margin-top:20px;"><a href="{esc(source_page_url)}" target="_blank">'
                    f'<strong>View full original page →</strong></a></p>'
                )
            wrapped = wrap_imported_page(title, html_content, site_label, source_page_url, section)

            # Name: section-slug-title
            page_slug = f"KB-{section[:2]}-{slugify(title)}"
            result_name, st, res = create_page(g, rsg_id, page_slug, title, wrapped, existing_names)
            if result_name:
                imported.append({
                    "title": title,
                    "page": result_name,
                    "section": section,
                    "source": site_label,
                    "has_content": bool(html_content.strip()),
                })
                print(f"  ✓ {title} -> {result_name} [{section}]")
            else:
                failed.append({"site": site_label, "title": title, "error": res})
                print(f"  ✗ {title}: {st}")

            time.sleep(0.4)

        # Import useful lists as pages
        LIST_MAP = {
            "homepage": [
                ("FAQ Questions1", "04-Client-Service", "FAQ"),
                ("Glossary table", "02-Lines-of-Business", "Glossary"),
            ],
            "coverages": [
                ("Glossary", "02-Lines-of-Business", "Coverage Glossary"),
            ],
            "": [
                ("Carrier Contacts", "01-Carriers", "Carrier Contacts"),
                ("Carrier Gallery", "01-Carriers", "Carrier Gallery"),
                ("carriers_master_updated", "01-Carriers", "Carriers Master List"),
                ("carrier-commission-table-with-evanston", "01-Carriers", "Commission Table"),
                ("General Liability Class codes", "02-Lines-of-Business", "GL Class Codes"),
                ("Workers Compensation Class Codes", "02-Lines-of-Business", "WC Class Codes"),
                ("SIC_Codes", "02-Lines-of-Business", "SIC Codes"),
                ("TOOLS", "08-CRM-and-Systems", "Agency Tools"),
                ("FAQQuestions", "04-Client-Service", "FAQ"),
            ],
        }
        for list_name, section, page_title in LIST_MAP.get(site_key, []):
            status, lists = g.call("GET", f"/sites/{site_id}/lists")
            match = next((l for l in lists.get("value", []) if l.get("displayName") == list_name), None)
            if not match:
                continue
            list_html = list_to_html(g, site_id, match["id"], list_name)
            if not list_html:
                continue
            wrapped = wrap_imported_page(page_title, list_html, site_label, site_url, section)
            page_slug = f"KB-{section[:2]}-list-{slugify(page_title)}"
            result_name, st, res = create_page(g, rsg_id, page_slug, page_title, wrapped, existing_names)
            if result_name:
                imported.append({"title": page_title, "page": result_name, "section": section, "source": f"{site_label} list", "has_content": True})
                print(f"  ✓ LIST {list_name} -> {result_name}")
            time.sleep(0.4)

    # Update section landing pages with imported page links
    section_pages = {}
    for item in imported:
        section_pages.setdefault(item["section"], []).append(item)

    SECTION_META = {
        "01-Carriers": ("01-Carriers", "Carriers"),
        "02-Lines-of-Business": ("02-Lines-of-Business", "Lines of Business"),
        "03-Operations": ("03-Operations", "Operations"),
        "04-Client-Service": ("04-Client-Service", "Client Service"),
        "05-Marketing": ("05-Marketing", "Marketing"),
        "06-Training": ("06-Training", "Training"),
        "07-Compliance": ("07-Compliance", "Compliance"),
        "08-CRM-and-Systems": ("08-CRM-and-Systems", "CRM & Systems"),
    }

    for section, items in section_pages.items():
        slug, label = SECTION_META.get(section, (section, section))
        page_name = f"{slug}.aspx"
        status, pages = g.call("GET", f"/sites/{rsg_id}/pages")
        match = next((p for p in pages.get("value", []) if p.get("name") == page_name), None)
        if not match:
            continue

        status, detail = g.call("GET", f"/sites/{match['id']}")
        if status != 200:
            continue
        # Rebuild section page with imported links (can't read existing canvas via app perms)
        slug, label = SECTION_META.get(section, (section, section))
        links = "".join(
            f'<li><a href="{BASE}/SitePages/{esc(i["page"])}">{esc(i["title"])}</a>'
            f' <span style="color:#666;font-size:12px;">(from {esc(i["source"])})</span></li>'
            for i in sorted(items, key=lambda x: x["title"].lower())
        )
        section_html = f"""
<div style="max-width:960px;margin:0 auto;font-family:'Segoe UI',sans-serif;">
  <p><a href="{BASE}/SitePages/Home.aspx">← Knowledge Base Home</a></p>
  <h1>{esc(label)}</h1>
  <p><a href="{BASE}/Shared%20Documents/{urllib.parse.quote(section)}"><strong>Open {esc(section)} folder →</strong></a></p>
  <h2>Knowledge pages ({len(items)})</h2>
  <ul style="line-height:1.8;">{links}</ul>
</div>"""
        g.call("PATCH", f"/sites/{rsg_id}/pages/{match['id']}/microsoft.graph.sitePage",
               {"title": label, "canvasLayout": canvas(section_html)})
        g.call("POST", f"/sites/{rsg_id}/pages/{match['id']}/microsoft.graph.sitePage/publish", beta=True)
        print(f"\nUpdated {page_name} with {len(items)} imported page links")

    # Update homepage with totals
    status, home = g.call("GET", f"/sites/{rsg_id}/pages")
    home_match = next((p for p in home.get("value", []) if p.get("name") == "Home.aspx"), None)
    if home_match:
        status, detail = g.call("GET", f"/sites/{home_match['id']}")
        html = extract_html(detail)
        banner = f'<div style="background:#dff6dd;border:1px solid #107c10;padding:14px 18px;border-radius:4px;margin-bottom:16px;"><strong>Consolidated:</strong> {len(imported)} knowledge pages imported from Operations, Coverages, Brand Guide, and Root Intranet into this single site.</div>'
        if "Consolidated:" not in html:
            html = html.replace('<div style="max-width:960px', banner + '<div style="max-width:960px', 1)
            g.call("PATCH", f"/sites/{home_match['id']}/microsoft.graph.sitePage", {"canvasLayout": canvas(html)})
            g.call("POST", f"/sites/{home_match['id']}/pages/{home_match['id']}/microsoft.graph.sitePage/publish", beta=True)

    report = {
        "completed": datetime.now(timezone.utc).isoformat(),
        "imported_count": len(imported),
        "skipped_count": len(skipped),
        "failed_count": len(failed),
        "imported": imported,
        "failed": failed[:20],
    }
    report_path = os.path.join(os.path.dirname(__file__), "..", "Reports", "content-consolidation.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n=== DONE: {len(imported)} imported, {len(skipped)} skipped, {len(failed)} failed ===")


if __name__ == "__main__":
    main()
