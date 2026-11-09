#!/usr/bin/env python3
"""Audit the immutable Wikimedia ES 100k release against the current MINIRONIN corpus."""
from __future__ import annotations
import argparse, gzip, hashlib, json, re, sys, unicodedata
from pathlib import Path

LICENSE = "CC BY-SA 3.0 (dataset card) / GFDL dual-licensed source; retain attribution and share-alike"
URL_PREFIX = "https://es.wikipedia.org/wiki/"

def norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    return re.sub(r"\W+", " ", text, flags=re.UNICODE).strip()

def sha(text: str) -> str:
    return hashlib.sha256(norm(text).encode("utf-8")).hexdigest()

def existing_hashes(root: Path) -> tuple[dict[str,str], int]:
    hashes: dict[str,str] = {}
    scanned = 0
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".txt", ".jsonl"}:
            continue
        if path.name.lower() in {"readme.md"} or ".git" in path.parts:
            continue
        try:
            if path.suffix.lower() == ".jsonl":
                with path.open(encoding="utf-8") as f:
                    for line_no, line in enumerate(f, 1):
                        try:
                            row=json.loads(line)
                        except Exception:
                            continue
                        for field in ("text","content","body","answer"):
                            value=row.get(field)
                            if isinstance(value,str) and len(value.strip()) >= 250:
                                hashes.setdefault(sha(value), f"{path}:{line_no}:{field}")
                                scanned += 1
            else:
                value=path.read_text(encoding="utf-8", errors="strict")
                if len(value.strip()) >= 250:
                    hashes.setdefault(sha(value), str(path))
                    scanned += 1
        except (UnicodeError, OSError):
            continue
    return hashes, scanned

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--root",type=Path,default=Path("."))
    ap.add_argument("--input",type=Path,default=Path("wikipedia-es-100k.jsonl.gz"))
    ap.add_argument("--manifest",type=Path,default=Path("WIKIMEDIA-ES-100K-MANIFEST.json"))
    ap.add_argument("--report",type=Path,default=Path("wikimedia-es-100k-global-audit.json"))
    a=ap.parse_args()
    m=json.loads(a.manifest.read_text(encoding="utf-8"))
    assert m.get("document_count")==100000, "manifest count is not 100000"
    assert m.get("unique_normalized_texts")==100000, "source manifest does not assert 100k unique texts"
    docs=m.get("documents",[])
    assert len(docs)==100000, "manifest document index is incomplete"
    manifest_by_id={str(x.get("id")):x for x in docs}
    assert len(manifest_by_id)==100000, "duplicate IDs in manifest"
    existing, existing_scanned=existing_hashes(a.root)
    seen_ids=set(); seen_urls=set(); seen_text=set()
    source_duplicates=[]; global_duplicates=[]; errors=[]
    valid=0
    with gzip.open(a.input,"rt",encoding="utf-8") as f:
        for line_no,line in enumerate(f,1):
            try:
                row=json.loads(line)
                page_id=str(row["id"]); title=str(row["title"]); url=str(row["url"])
                text=row["text"]; lic=row["license"]; meta=row["metadata"]
                if not isinstance(text,str) or len(text.strip())<800: raise ValueError("text_short")
                if not url.startswith(URL_PREFIX): raise ValueError("bad_url")
                if lic != LICENSE: raise ValueError("license_mismatch")
                source_dataset=str(row.get("source_dataset") or row.get("source") or "").casefold()
                if not any(token in source_dataset for token in ("wikipedia","wikimedia")): raise ValueError(f"source_mismatch:{source_dataset[:100]}")
                if meta.get("page_id")!=page_id or meta.get("url")!=url: raise ValueError("metadata_mismatch")
                if meta.get("license")!=LICENSE: raise ValueError("metadata_license_mismatch")
                if page_id in seen_ids: raise ValueError("duplicate_page_id")
                if url in seen_urls: raise ValueError("duplicate_url")
                digest=sha(text)
                if digest in seen_text:
                    source_duplicates.append({"line":line_no,"id":page_id,"reason":"duplicate_text_in_batch"})
                else:
                    seen_text.add(digest)
                    if digest in existing:
                        global_duplicates.append({"line":line_no,"id":page_id,"existing":existing[digest]})
                if page_id not in manifest_by_id: raise ValueError("id_absent_from_manifest")
                md=manifest_by_id[page_id]
                if md.get("url")!=url or md.get("title")!=title: raise ValueError("manifest_row_mismatch")
                if md.get("text_sha256_normalized")!=meta.get("text_sha256_normalized"): raise ValueError("normalized_hash_metadata_mismatch")
                seen_ids.add(page_id); seen_urls.add(url); valid+=1
            except Exception as e:
                errors.append({"line":line_no,"error":str(e)})
                if len(errors)>=100: break
    source_unique=len(seen_text)
    net_new=max(0,source_unique-len(global_duplicates))
    report={
      "schema":"minironin-global-corpus-audit-v1",
      "source_release":"wikimedia-es-100k-v1",
      "source_expected":100000,
      "source_records_validated":valid,
      "source_unique_page_ids":len(seen_ids),
      "source_unique_urls":len(seen_urls),
      "source_unique_normalized_texts":source_unique,
      "source_duplicates":len(source_duplicates),
      "global_exact_duplicates":len(global_duplicates),
      "global_existing_text_units_scanned":existing_scanned,
      "global_exact_net_new_estimate":net_new,
      "existing_exact_hash_count":len(existing),
      "validation_errors":errors,
      "global_duplicate_samples":global_duplicates[:100],
      "source_duplicate_samples":source_duplicates[:100],
      "admission_decision":"PASS_SOURCE_AND_EXACT_DEDUP" if valid==100000 and source_unique==100000 and not errors else "REJECT_OR_REVIEW",
      "limitations":["Exact normalized-text dedup only; no semantic near-duplicate detector in this audit.",
                     "Wikipedia content is community-authored and not independently fact-checked.",
                     "CC BY-SA/GFDL attribution and share-alike obligations must be preserved in downstream adaptations.",
                     "This audit does not itself modify training manifests or admit data to training."]
    }
    a.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:report[k] for k in ("source_records_validated","source_unique_normalized_texts","global_exact_duplicates","global_exact_net_new_estimate","validation_errors","admission_decision")},ensure_ascii=False))
    if report["admission_decision"]!="PASS_SOURCE_AND_EXACT_DEDUP": return 2
    return 0
if __name__=="__main__": raise SystemExit(main())
