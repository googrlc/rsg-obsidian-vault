<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RSG — Account Intel Tab Design</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f4f0; padding: 24px; color: #1a1a18; }
.shell { background: #f5f4f0; border-radius: 12px; overflow: hidden; max-width: 900px; margin: 0 auto; }

.record-header { background: #ffffff; border-bottom: 0.5px solid rgba(0,0,0,0.12); padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; }
.record-name { font-size: 16px; font-weight: 500; color: #1a1a18; }
.record-meta { font-size: 12px; color: #888780; margin-top: 2px; }
.hdr-right { display: flex; align-items: center; gap: 8px; }
.run-btn { font-size: 12px; font-weight: 500; background: #e6f1fb; color: #185fa5; border: none; padding: 6px 14px; border-radius: 4px; cursor: pointer; }
.badge-high { display: inline-block; font-size: 10px; font-weight: 500; padding: 2px 8px; border-radius: 3px; background: #eaf3de; color: #3b6d11; }

.tab-bar { background: #f1efe8; border-bottom: 0.5px solid rgba(0,0,0,0.12); padding: 0 16px; display: flex; gap: 0; }
.tab { font-size: 12px; padding: 10px 16px; cursor: pointer; color: #888780; border-bottom: 2px solid transparent; margin-bottom: -0.5px; }
.tab.active { color: #1a1a18; font-weight: 500; border-bottom-color: #1a1a18; }

.intel-body { padding: 16px; display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.full-width { grid-column: 1 / -1; }

.section { background: #ffffff; border: 0.5px solid rgba(0,0,0,0.12); border-radius: 12px; overflow: hidden; }
.section-header { padding: 9px 14px; background: #f1efe8; border-bottom: 0.5px solid rgba(0,0,0,0.12); display: flex; align-items: center; justify-content: space-between; }
.section-title { font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; color: #888780; }
.section-body { padding: 14px; }

.field-row { display: flex; gap: 8px; margin-bottom: 10px; }
.field-row:last-child { margin-bottom: 0; }
.field-label { font-size: 11px; color: #888780; min-width: 130px; padding-top: 2px; flex-shrink: 0; }
.field-value { font-size: 13px; color: #1a1a18; flex: 1; line-height: 1.5; }
.field-value.muted { color: #5f5e5a; }
.field-value.long { color: #1a1a18; font-size: 13px; line-height: 1.6; }

.ai-summary { font-size: 13px; color: #1a1a18; line-height: 1.7; padding: 12px 14px; background: #f1efe8; border-radius: 8px; border-left: 2px solid #378add; }
.opener-box { font-size: 13px; color: #1a1a18; line-height: 1.6; padding: 12px 14px; background: #f1efe8; border-radius: 8px; border-left: 2px solid #ba7517; font-style: italic; }

.pill-group { display: flex; flex-wrap: wrap; gap: 6px; }
.pill { font-size: 11px; padding: 3px 9px; border-radius: 12px; background: #f1efe8; color: #5f5e5a; border: 0.5px solid rgba(0,0,0,0.12); }
.pill-red { background: #fcebeb; color: #a32d2d; border-color: transparent; }
.pill-amber { background: #faeeda; color: #854f0b; border-color: transparent; }
.pill-blue { background: #e6f1fb; color: #185fa5; border-color: transparent; }

.meta-strip { display: flex; gap: 16px; align-items: center; margin-bottom: 14px; padding-bottom: 12px; border-bottom: 0.5px solid rgba(0,0,0,0.12); flex-wrap: wrap; }
.meta-item { font-size: 11px; color: #888780; display: flex; align-items: center; gap: 5px; }
.dot { width: 6px; height: 6px; border-radius: 50%; background: #3b6d11; }

.conf-bar { display: flex; gap: 3px; margin-top: 4px; }
.conf-seg { height: 4px; width: 28px; border-radius: 2px; background: rgba(0,0,0,0.1); }
.conf-seg.filled { background: #3b6d11; }

.divider { height: 0.5px; background: rgba(0,0,0,0.1); margin: 12px 0; }

.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.stat-box { background: #f1efe8; border-radius: 8px; padding: 10px 12px; }
.stat-label { font-size: 11px; color: #888780; margin-bottom: 3px; }
.stat-value { font-size: 13px; font-weight: 500; color: #1a1a18; }

.full-research-toggle { font-size: 12px; color: #185fa5; cursor: pointer; display: flex; align-items: center; gap: 4px; }
.research-content { margin-top: 10px; font-size: 12px; color: #5f5e5a; line-height: 1.6; display: none; padding: 10px; background: #f1efe8; border-radius: 8px; }
.research-content.open { display: block; }
</style>
</head>
<body>
<div class="shell">
  <div class="record-header">
    <div>
      <div class="record-name">Atlanta Freight Solutions</div>
      <div class="record-meta">Prospect · Commercial Auto · GL</div>
    </div>
    <div class="hdr-right">
      <span class="badge-high">Intel: High confidence</span>
      <button class="run-btn">Re-run Intel Pack</button>
    </div>
  </div>

  <div class="tab-bar">
    <div class="tab">Overview</div>
    <div class="tab">Activity</div>
    <div class="tab active">Intelligence</div>
    <div class="tab">Documents</div>
  </div>

  <div class="intel-body">

    <div class="full-width section">
      <div class="section-body" style="padding: 12px 14px;">
        <div class="meta-strip">
          <div class="meta-item"><div class="dot"></div>Last run: Mar 24, 2026</div>
          <div class="meta-item">4 of 5 sources returned data</div>
          <div class="meta-item">
            Confidence: High
            <div class="conf-bar">
              <div class="conf-seg filled"></div>
              <div class="conf-seg filled"></div>
              <div class="conf-seg filled"></div>
            </div>
          </div>
          <div class="meta-item">Run by: Lamar</div>
        </div>
        <div style="font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:0.05em;color:#888780;margin-bottom:8px;">AI Summary</div>
        <div class="ai-summary">Atlanta Freight Solutions operates a 23-truck regional fleet out of Forest Park. They've had two DOT incidents in the past 18 months and are approaching renewal — likely unhappy with their current carrier's rate increase. Strong candidate for commercial auto + GL bundle.</div>
      </div>
    </div>

    <div class="section">
      <div class="section-header"><span class="section-title">Company profile</span></div>
      <div class="section-body">
        <div class="field-row"><div class="field-label">Legal name</div><div class="field-value">Atlanta Freight Solutions LLC</div></div>
        <div class="field-row"><div class="field-label">DBA</div><div class="field-value muted">—</div></div>
        <div class="field-row"><div class="field-label">NAICS code</div><div class="field-value">484121 — General Freight Trucking, Long-Distance, TL</div></div>
        <div class="field-row"><div class="field-label">SIC code</div><div class="field-value">4213</div></div>
        <div class="field-row"><div class="field-label">Years in business</div><div class="field-value">11 years (est. 2015)</div></div>
        <div class="field-row"><div class="field-label">Entity type</div><div class="field-value">LLC</div></div>
        <div class="field-row"><div class="field-label">Employees</div><div class="field-value">41</div></div>
        <div class="field-row"><div class="field-label">Annual revenue (est.)</div><div class="field-value">$4.2M</div></div>
        <div class="field-row"><div class="field-label">Website</div><div class="field-value" style="color:#185fa5;">atlantafreightsolutions.com</div></div>
        <div class="field-row"><div class="field-label">LinkedIn</div><div class="field-value" style="color:#185fa5;">linkedin.com/company/afs</div></div>
        <div class="field-row"><div class="field-label">BBB rating</div><div class="field-value">A− · Accredited · 2 open complaints</div></div>
      </div>
    </div>

    <div class="section">
      <div class="section-header"><span class="section-title">Exposure & risk signals</span></div>
      <div class="section-body">
        <div class="two-col" style="margin-bottom:12px;">
          <div class="stat-box"><div class="stat-label">Fleet size</div><div class="stat-value">23 units</div></div>
          <div class="stat-box"><div class="stat-label">Radius</div><div class="stat-value">GA + TN routes</div></div>
          <div class="stat-box"><div class="stat-label">Cargo type</div><div class="stat-value">Refrigerated</div></div>
          <div class="stat-box"><div class="stat-label">Owner-ops</div><div class="stat-value">Yes — on payroll</div></div>
        </div>
        <div class="divider"></div>
        <div class="field-row"><div class="field-label">DOT incidents</div><div class="field-value">2 in past 18 months</div></div>
        <div class="field-row"><div class="field-label">Est. payroll</div><div class="field-value">$1.8M annually</div></div>
        <div class="field-row"><div class="field-label">OSHA violations</div><div class="field-value muted">None found</div></div>
        <div class="field-row"><div class="field-label">Underwriting flag</div><div class="field-value" style="color:#a32d2d;">DOT incidents may trigger declination at standard markets — surplus lines likely for CA</div></div>
      </div>
    </div>

    <div class="section">
      <div class="section-header"><span class="section-title">Pain points</span></div>
      <div class="section-body">
        <div class="pill-group">
          <span class="pill pill-red">Rising premiums</span>
          <span class="pill pill-red">DOT compliance burden</span>
          <span class="pill pill-amber">Driver turnover</span>
          <span class="pill pill-amber">Cargo liability gaps</span>
        </div>
        <div class="divider"></div>
        <div class="field-row"><div class="field-label">Objection risk</div><div class="field-value muted">Price-sensitive — has shopped carriers twice in 3 years</div></div>
      </div>
    </div>

    <div class="section">
      <div class="section-header"><span class="section-title">Sales intelligence</span></div>
      <div class="section-body">
        <div style="font-size:11px;color:#888780;margin-bottom:6px;">Conversation opener</div>
        <div class="opener-box">"I saw you expanded into Tennessee routes last quarter — how's that affecting your DOT compliance workload?"</div>
        <div class="divider"></div>
        <div class="field-row"><div class="field-label">News signal</div><div class="field-value">Featured in Atlanta Business Chronicle (Feb 2026) for Southeast expansion</div></div>
        <div class="field-row"><div class="field-label">LinkedIn signal</div><div class="field-value">Hiring a safety compliance officer — owner posts about fuel costs</div></div>
        <div class="field-row"><div class="field-label">Growth indicator</div><div class="field-value">Expanding routes, adding headcount — fleet likely to grow</div></div>
        <div class="field-row"><div class="field-label">Cross-sell signal</div><div class="field-value"><span class="pill pill-blue">Workers Comp</span> <span class="pill pill-blue">Occupational Accident</span></div></div>
        <div class="field-row"><div class="field-label">RSG relationship</div><div class="field-value muted">No prior RSG relationship</div></div>
      </div>
    </div>

    <div class="full-width section">
      <div class="section-header"><span class="section-title">Raw research notes</span></div>
      <div class="section-body">
        <div class="field-row"><div class="field-label">Website</div><div class="field-value long">Regional carrier specializing in temperature-controlled freight across the Southeast. Services include LTL, FTL, and dedicated contract carriage. Fleet includes refrigerated 53' trailers. Safety rating listed as Satisfactory on FMCSA.</div></div>
        <div class="divider"></div>
        <div class="field-row"><div class="field-label">News & press</div><div class="field-value long">Atlanta Business Chronicle (Feb 2026): expanding into Tennessee with two new terminal locations. No litigation, regulatory actions, or negative press found in last 12 months.</div></div>
        <div class="divider"></div>
        <div class="field-row"><div class="field-label">BBB detail</div><div class="field-value long">A− rating. Accredited since 2019. 2 open complaints — both billing disputes, one with owner response. No pattern of unresolved issues.</div></div>
        <div class="divider"></div>
        <div class="field-row"><div class="field-label">LinkedIn detail</div><div class="field-value long">41 employees on LinkedIn. Currently hiring: Safety Compliance Officer, Dispatcher, CDL Driver (Class A). Owner Marcus Webb active — recent posts about diesel prices and FMCSA rule changes.</div></div>
      </div>
    </div>

  </div>
</div>
</body>
</html>