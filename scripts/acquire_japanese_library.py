#!/usr/bin/env python3
"""Acquire Spain-screened Japanese classics and warrior/ronin literature."""
from __future__ import annotations
import argparse, hashlib, json, re, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REGISTRY=ROOT/"data/japan/SOURCES.json"
START=re.compile(r"\*\*\* START OF THE PROJECT GUTENBERG EBOOK .*?\*\*\*",re.I)
END=re.compile(r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK",re.I)
def clean(raw:bytes)->str:
    text=raw.decode("utf-8-sig",errors="strict").replace("\r\n","\n").replace("\r","\n")
    a,b=START.search(text),END.search(text)
    if not a or not b or b.start()<=a.end(): raise ValueError("Malformed Gutenberg boundaries")
    body=re.sub(r"\n{4,}","\n\n\n",text[a.end():b.start()].strip())
    if len(body)<5000: raise ValueError(f"Suspiciously short source: {len(body)}")
    return body
def download(row):
    req=urllib.request.Request(row["plain_text_url"],headers={"User-Agent":"MINIRONIN-Japanese-Library/1.0 (GitHub Actions; attribution retained)"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req,timeout=120) as response: return response.read()
        except Exception:
            if attempt==3: raise
            time.sleep(2**attempt)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",default="data/inherited/japanese-library"); args=ap.parse_args()
    out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    registry=json.loads(REGISTRY.read_text(encoding="utf-8"))
    approved=[x for x in registry["sources"] if x.get("rights_status")=="approved_for_spain_training"]
    if len(approved)<10: raise SystemExit("Expected at least ten approved Japanese sources")
    manifest={"schema":"minironin-japanese-library-acquisition-v1","rights_policy":registry["rights_policy"],"sources":[]}
    with ThreadPoolExecutor(max_workers=6) as pool:
        for row,raw in zip(approved,pool.map(download,approved)):
            body=clean(raw); path=out/(row["id"].lower()+".txt")
            path.write_text(body+"\n",encoding="utf-8")
            manifest["sources"].append({**row,"path":path.name,"bytes":path.stat().st_size,"characters":len(body),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"upstream_sha256":hashlib.sha256(raw).hexdigest()})
            print(json.dumps(manifest["sources"][-1],ensure_ascii=False),flush=True)
    manifest["total_documents"]=len(manifest["sources"]); manifest["total_bytes"]=sum(x["bytes"] for x in manifest["sources"])
    (out/"JAPANESE-LIBRARY-MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"acquired":manifest["total_documents"],"bytes":manifest["total_bytes"]}))
if __name__=="__main__": main()
