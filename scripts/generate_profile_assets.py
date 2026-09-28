#!/usr/bin/env python3
import json, os, urllib.request
from datetime import date, timedelta
from html import escape

TOKEN = os.environ.get("GITHUB_TOKEN", "")
USERNAME = os.environ.get("GITHUB_USERNAME", "Mahdiyar185")
ENDPOINT = "https://api.github.com/graphql"
QUERY = """
query($from: DateTime!, $to: DateTime!) {
  viewer {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100, orderBy: {field: UPDATED_AT, direction: DESC}) {
      totalCount
      nodes {
        stargazerCount
        forkCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection(from: $from, to: $to) {
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""

today=date.today(); from_date=today-timedelta(days=365)
body=json.dumps({"query":QUERY,"variables":{"from":f"{from_date.isoformat()}T00:00:00Z","to":f"{today.isoformat()}T23:59:59Z"}}).encode()
req=urllib.request.Request(ENDPOINT,data=body,headers={"Authorization":f"bearer {TOKEN}","Content-Type":"application/json","User-Agent":"Mahdiyar185-profile-assets"},method="POST")
with urllib.request.urlopen(req,timeout=30) as r: payload=json.load(r)
if payload.get("errors"): raise SystemExit(json.dumps(payload["errors"]))
v=payload["data"]["viewer"]; cc=v["contributionsCollection"]; repos=v["repositories"]
days=[d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]; days.sort(key=lambda x:x["date"])
current=0
for d in reversed(days):
    if d["contributionCount"]>0: current+=1
    else: break
longest=run=0
for d in days:
    if d["contributionCount"]>0: run+=1; longest=max(longest,run)
    else: run=0
active=sum(1 for d in days if d["contributionCount"]>0)
lang_sizes={}; lang_colors={}
stars=forks=0
for repo in repos["nodes"]:
    stars+=repo["stargazerCount"]; forks+=repo["forkCount"]
    for e in repo["languages"]["edges"]:
        n=e["node"]["name"]; lang_sizes[n]=lang_sizes.get(n,0)+e["size"]; lang_colors[n]=e["node"].get("color") or "#38BDF8"
top=sorted(lang_sizes.items(),key=lambda x:x[1],reverse=True)[:6]; total_lang=sum(lang_sizes.values()) or 1

def shell(title,h=250):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="920" height="{h}" viewBox="0 0 920 {h}" role="img" aria-label="{escape(title)}"><defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#050A18"/><stop offset=".55" stop-color="#0B1730"/><stop offset="1" stop-color="#1C0C35"/></linearGradient><linearGradient id="line" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#22D3EE"/><stop offset=".55" stop-color="#6366F1"/><stop offset="1" stop-color="#D946EF"/></linearGradient></defs><rect width="920" height="{h}" rx="22" fill="url(#bg)" stroke="#26385D"/><circle cx="820" cy="42" r="90" fill="#D946EF" opacity=".08"/><circle cx="700" cy="230" r="100" fill="#22D3EE" opacity=".05"/><text x="34" y="42" fill="#F8FAFC" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="21" font-weight="700">{escape(title)}</text><path d="M34 64H886" stroke="url(#line)" opacity=".6"/>']
def text(x,y,val,size=13,color="#CBD5E1",weight=600): return f'<text x="{x}" y="{y}" fill="{color}" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="{size}" font-weight="{weight}">{escape(str(val))}</text>'
# stats
s=shell("GitHub Activity")
metrics=[("PUBLIC REPOS",repos["totalCount"]),("FOLLOWERS",v["followers"]["totalCount"]),("COMMITS · 1Y",cc["totalCommitContributions"]),("PULL REQUESTS",cc["totalPullRequestContributions"]),("ISSUES",cc["totalIssueContributions"]),("STARS",stars)]
for (lab,val),(x,y) in zip(metrics,[(34,105),(330,105),(626,105),(34,180),(330,180),(626,180)]):
    s += [text(x,y-16,lab,11,"#7DD3FC",700),text(x,y+14,val,28,"#F8FAFC",800),f'<rect x="{x}" y="{y+28}" width="230" height="3" rx="2" fill="url(#line)" opacity=".78"/>']
s += [text(34,238,"Generated locally from GitHub data — no external stats-card service.",11,"#64748B",500),"</svg>"]
Path("assets/github-stats.svg").write_text("\n".join(s),encoding="utf-8")
# languages
l=shell("Top Languages",210); x0=34; y0=90; bw=500; cur=x0
for n,sz in top:
    w=max(16,bw*sz/total_lang); l.append(f'<rect x="{cur:.1f}" y="{y0}" width="{w:.1f}" height="16" fill="{lang_colors[n]}" opacity=".9"/>'); cur+=w
for i,(n,sz) in enumerate(top): l += [f'<circle cx="40" cy="{135+i*22}" r="5" fill="{lang_colors[n]}"/>',text(54,139+i*22,f"{n} · {sz/total_lang*100:.1f}%",12,"#CBD5E1",600)]
l.append("</svg>"); Path("assets/github-languages.svg").write_text("\n".join(l),encoding="utf-8")
# streak
st=shell("Contribution Streak",185)
st += [text(34,95,f"Current streak  {current} days",17,"#E2E8F0",700),text(330,95,f"Longest streak  {longest} days",17,"#E2E8F0",700),text(626,95,f"Active days  {active}",17,"#E2E8F0",700),text(34,126,f"{cc['contributionCalendar']['totalContributions']} contributions in the last year",12,"#94A3B8",500)]
for i in range(70):
    x=34+i*12.1; active_cell=(i < min(70,current)) if current else (i%11==0)
    st.append(f'<rect x="{x:.1f}" y="151" width="8" height="8" rx="2" fill="#38BDF8" opacity="{.85 if active_cell else .12}"/>')
st.append("</svg>"); Path("assets/github-streak.svg").write_text("\n".join(st),encoding="utf-8")
# activity grid
a=shell("Contribution Activity",270)
a += [text(34,94,f"{cc['contributionCalendar']['totalContributions']} contributions in the last year",16,"#E2E8F0",700),text(34,121,f"Current streak {current} days  ·  Longest streak {longest} days  ·  Active days {active}",12,"#94A3B8",500)]
recent=days[-182:]; cell=12; gap=3; sx=34; sy=145
for i,d in enumerate(recent):
    col,row=i%26,i//26; x=sx+col*(cell+gap); y=sy+row*(cell+gap); c=d['contributionCount']; op=.12 if c==0 else min(.95,.28+c*.10); fill='#38BDF8' if c else '#17233D'; a.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{fill}" opacity="{op:.2f}"/>')
a += [text(420,170,"Live contribution overview",12,"#C4B5FD",700),text(420,196,"Generated in-repository by GitHub Actions.",11,"#64748B",500),text(420,216,"The native GitHub profile graph remains",11,"#64748B",500),text(420,234,"the source of truth for contribution history.",11,"#64748B",500),"</svg>"]
Path("assets/github-activity.svg").write_text("\n".join(a),encoding="utf-8")
