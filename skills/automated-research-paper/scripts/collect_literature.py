#!/usr/bin/env python3
"""Collect real literature metadata from public scholarly APIs."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Iterable


USER_AGENT = "automated-research-paper-skill/1.0 (mailto:research@example.com)"


def fetch_json(url: str, timeout: int = 30) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_text(url: str, timeout: int = 30) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def make_cite_key(authors: list[str], year: Any, title: str) -> str:
    lead = "anon"
    if authors:
        lead = re.sub(r"[^A-Za-z0-9]", "", authors[0].split()[-1]).lower() or "anon"
    first_word = ""
    for token in re.findall(r"[A-Za-z0-9]+", title.lower()):
        if token not in {"a", "an", "the", "of", "for", "and", "to", "in", "on", "with"}:
            first_word = token
            break
    return f"{lead}{year or 'nd'}{first_word}"


def openalex(topic: str, limit: int, year_min: int | None) -> Iterable[dict[str, Any]]:
    params = {
        "search": topic,
        "per-page": str(limit),
        "sort": "cited_by_count:desc",
    }
    if year_min:
        params["filter"] = f"from_publication_date:{year_min}-01-01"
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    data = fetch_json(url)
    for item in data.get("results", []):
        authors = [
            a.get("author", {}).get("display_name", "")
            for a in item.get("authorships", [])
            if a.get("author", {}).get("display_name")
        ]
        title = clean_text(item.get("title"))
        year = item.get("publication_year")
        doi = item.get("doi")
        yield {
            "id": item.get("id"),
            "title": title,
            "source": "openalex",
            "url": item.get("primary_location", {}).get("landing_page_url") or item.get("id"),
            "year": year,
            "venue": clean_text((item.get("primary_location", {}).get("source") or {}).get("display_name")),
            "doi": doi,
            "arxiv_id": "",
            "authors": authors,
            "abstract": clean_text(" ".join(reconstruct_abstract(item.get("abstract_inverted_index")).split())),
            "cite_key": make_cite_key(authors, year, title),
        }


def reconstruct_abstract(index: Any) -> str:
    if not isinstance(index, dict):
        return ""
    pairs: list[tuple[int, str]] = []
    for word, positions in index.items():
        for pos in positions:
            pairs.append((int(pos), word))
    return " ".join(word for _, word in sorted(pairs))


def semantic_scholar(topic: str, limit: int, year_min: int | None) -> Iterable[dict[str, Any]]:
    fields = "title,abstract,year,venue,url,authors,externalIds,citationCount"
    params = {"query": topic, "limit": str(min(limit, 100)), "fields": fields}
    url = "https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(params)
    data = fetch_json(url)
    for item in data.get("data", []):
        year = item.get("year")
        if year_min and year and int(year) < year_min:
            continue
        authors = [a.get("name", "") for a in item.get("authors", []) if a.get("name")]
        external = item.get("externalIds") or {}
        title = clean_text(item.get("title"))
        yield {
            "id": item.get("paperId"),
            "title": title,
            "source": "semantic_scholar",
            "url": item.get("url"),
            "year": year,
            "venue": clean_text(item.get("venue")),
            "doi": external.get("DOI", ""),
            "arxiv_id": external.get("ArXiv", ""),
            "authors": authors,
            "abstract": clean_text(item.get("abstract")),
            "citation_count": item.get("citationCount"),
            "cite_key": make_cite_key(authors, year, title),
        }


def arxiv(topic: str, limit: int, year_min: int | None) -> Iterable[dict[str, Any]]:
    query = urllib.parse.quote(f'all:"{topic}"')
    url = f"https://export.arxiv.org/api/query?search_query={query}&start=0&max_results={limit}&sortBy=relevance"
    text = fetch_text(url)
    root = ET.fromstring(text)
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    for entry in root.findall("atom:entry", ns):
        title = clean_text(entry.findtext("atom:title", default="", namespaces=ns))
        published = entry.findtext("atom:published", default="", namespaces=ns)
        year = int(published[:4]) if published[:4].isdigit() else None
        if year_min and year and year < year_min:
            continue
        authors = [
            clean_text(a.findtext("atom:name", default="", namespaces=ns))
            for a in entry.findall("atom:author", ns)
        ]
        arxiv_url = entry.findtext("atom:id", default="", namespaces=ns)
        arxiv_id = arxiv_url.rsplit("/", 1)[-1] if arxiv_url else ""
        yield {
            "id": arxiv_id,
            "title": title,
            "source": "arxiv",
            "url": arxiv_url,
            "year": year,
            "venue": "arXiv",
            "doi": "",
            "arxiv_id": arxiv_id,
            "authors": authors,
            "abstract": clean_text(entry.findtext("atom:summary", default="", namespaces=ns)),
            "cite_key": make_cite_key(authors, year, title),
        }


def dedupe(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    output: list[dict[str, Any]] = []
    collected_at = dt.datetime.now(dt.timezone.utc).isoformat()
    for record in records:
        title = normalize_title(record.get("title", ""))
        doi = str(record.get("doi") or "").lower()
        arxiv_id = str(record.get("arxiv_id") or "").lower()
        key = doi or arxiv_id or title
        if not key or key in seen:
            continue
        seen.add(key)
        record["collected_at"] = collected_at
        output.append(record)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--year-min", type=int, default=None)
    parser.add_argument("--limit-per-source", type=int, default=40)
    parser.add_argument("--sources", default="openalex,semantic_scholar,arxiv")
    args = parser.parse_args()

    source_map = {
        "openalex": openalex,
        "semantic_scholar": semantic_scholar,
        "arxiv": arxiv,
    }
    records: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for source in [s.strip() for s in args.sources.split(",") if s.strip()]:
        func = source_map.get(source)
        if func is None:
            errors.append({"source": source, "error": "unknown source"})
            continue
        try:
            records.extend(func(args.topic, args.limit_per_source, args.year_min))
        except (urllib.error.URLError, TimeoutError, ET.ParseError, json.JSONDecodeError) as exc:
            errors.append({"source": source, "error": str(exc)})
        time.sleep(1.0)

    output = dedupe(records)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        for record in output:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    summary = {
        "topic": args.topic,
        "records": len(output),
        "out": str(out_path),
        "errors": errors,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
