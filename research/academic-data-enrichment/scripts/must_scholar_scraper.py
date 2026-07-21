#!/usr/bin/env python3
"""Scrape MUST scholar database and cross-reference with OpenAlex."""
import urllib.request
import re
import json
import time
import sys


def get_scholar_list(departments_code="", name=""):
    """Fetch scholar list from MUST scholar database."""
    url = f"https://scholar.must.edu.mo/scholar/page?nameAcronym=&realName={urllib.request.quote(name)}&departmentsCode={departments_code}&page=1"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode("utf-8")

    scholars = re.findall(r'href="/scholar/(\d+)"[^>]*title="([^"]+)"', html)
    total = re.search(r'totalCount\s*=\s*"(\d+)"', html)
    unpublished = re.findall(r'href="javascript:tiaozhuan\(\);"[^>]*title="([^"]+)"', html)

    return {
        "total": int(total.group(1)) if total else 0,
        "scholars": [{"id": sid, "name": name} for sid, name in scholars],
        "unpublished": unpublished,
    }


def get_scholar_profile(scholar_id):
    """Fetch individual scholar profile."""
    url = f"https://scholar.must.edu.mo/scholar/{scholar_id}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read().decode("utf-8")

    # Extract key stats
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"&nbsp;", " ", text)

    stats = {}
    for pattern, key in [
        (r"WOS核心合集引用[：:](\d+)", "wos_citations"),
        (r"H Index[：:](\d+)", "h_index"),
        (r"WOS收錄[：:](\d+)", "wos_papers"),
        (r"SCOPUS收錄[：:](\d+)", "scopus_papers"),
        (r"論文[：:]\s*(\d+)", "total_papers"),
        (r"科研項目[：:](\d+)", "projects"),
        (r"專利[：:](\d+)", "patents"),
    ]:
        m = re.search(pattern, text)
        if m:
            stats[key] = int(m.group(1))

    return stats


def search_openalex(name, country_code="MO"):
    """Search OpenAlex for a professor."""
    url = f"https://api.openalex.org/authors?search={urllib.request.quote(name)}&filter=last_known_institutions.country_code:{country_code}&per_page=5&fields=id,display_name,works_count,cited_by_count,summary_stats,last_known_institutions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read()).get("results", [])


def get_openalex_papers(author_id, limit=10):
    """Get top papers for an OpenAlex author."""
    url = f"https://api.openalex.org/works?filter=author.id:{author_id}&sort=cited_by_count:desc&per_page={limit}&select=title,publication_year,cited_by_count,concepts"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read()).get("results", [])


if __name__ == "__main__":
    # Example: list all CS scholars
    result = get_scholar_list("672339")
    print(f"CS department: {result['total']} scholars")
    for s in result["scholars"]:
        print(f"  {s['id']}: {s['name']}")
    if result["unpublished"]:
        print(f"  Unpublished: {result['unpublished']}")
