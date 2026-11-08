#!/usr/bin/env python3
"""Select Japanese-language Aozora originals from Soranoha with Spain rights gates.

Only works by an explicit author whitelist (all died by 1955), with no translator
or editor contributor, and whose individual Soranoha page marks the source
public-domain are admitted. This intentionally excludes modern samurai novels
and modern translations.
"""
from __future__ import annotations
import argparse, hashlib, json, re, time, urllib.request
from pathlib import Path

AUTHORS = {
    "芥川竜之介": ("Akutagawa Ryunosuke", 1927),
    "森鴎外": ("Mori Ogai", 1922),
    "夏目漱石": ("Natsume Soseki", 1916),
    "幸田露伴": ("Koda Rohan", 1947),
    "泉鏡花": ("Izumi Kyoka", 1939),
    "国木田独歩": ("Kunikida Doppo", 1908),
    "田山花袋": ("Tayama Katai", 1930),
    "二葉亭四迷": ("Futabatei Shimei", 1909),
    "正岡子規": ("Masaoka Shiki", 1902),
    "樋口一葉": ("Higuchi Ichiyo", 1896),
    "与謝野晶子": ("Yosano Akiko", 1942),
    "太宰治": ("Dazai Osamu", 1948),
    "宮沢賢治": ("Miyazawa Kenji", 1933),
    "島崎藤村": ("Shimazaki Toson", 1943),
    "有島武郎": ("Arishima Takeo", 1923),
    "徳田秋声": ("Tokuda Shusei", 1943),
}
KEYWORDS = ("浪人","忠臣蔵","武士","侍","剣","仇討","武道","兵法","戦国","藩","武家","刀","義士","剣客","弓","合戦","城","忍者","武将","源平","平家","義経","弁慶")
BASE = "https://soranoha.org"
HEADERS = {"User-Agent":"MINIRONIN-Japanese-originals/1.0 (research corpus; attribution retained)"}

def fetch(url: str) -> bytes:
    req=urllib.request.Request(url,headers=HEADERS)
    with urllib.request.urlopen(req,timeout=90) as response: return response.read()

def person_name(row):
    return "".join(x or "" for x in (row.get("family_name"),row.get("given_name")))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",default="data/inherited/japanese-library/aozora-originals")
    ap.add_argument("--per-author",type=int,default=20)
    ap.add_argument("--max-works",type=int,default=280)
    args=ap.parse_args()
    out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    catalog=json.loads(fetch(BASE+"/catalog.json").decode("utf-8"))
    works=catalog.get("works",[])
    candidates=[]
    for work in works:
        contributors=work.get("contributors",[])
        authors=[c for c in contributors if c.get("relation_to_work") in ("著者","作者","author")]
        if len(authors)!=1: continue
        author=person_name(authors[0])
        if author not in AUTHORS: continue
        # Original Japanese works only: translated, edited or collated works are excluded.
        if any(c.get("relation_to_work") in ("翻訳者","訳者","校訂者","編者","翻案者","translator","editor") for c in contributors): continue
        title=str(work.get("title",""))
        length=int(work.get("body_character_count") or 0)
        if length < 3000: continue
        rank=0 if any(k in title for k in KEYWORDS) else 1
        candidates.append((rank,-length,author,work))
    candidates.sort(key=lambda x:(x[0],x[2],x[1],x[3].get("slug","")))
    per_author={}; selected=[]
    for rank,neglen,author,work in candidates:
        if per_author.get(author,0)>=args.per_author: continue
        selected.append((rank,author,work)); per_author[author]=per_author.get(author,0)+1
        if len(selected)>=args.max_works: break
    if len(selected)<20: raise SystemExit(f"Only {len(selected)} candidates; catalogue schema or author allowlist needs review")
    manifest={"schema":"minironin-aozora-japanese-originals-v1",
      "upstream":"Soranoha Aozora Bunko TEI Corpus; source texts from Aozora Bunko",
      "encoding_license":"Soranoha encoding and plaintext projection CC0-1.0; bibliographic catalogue CC BY 4.0, attribution retained",
      "rights_gate":"Only original Japanese works by whitelisted authors deceased by 1955, with no translator/editor contributor, and whose individual Soranoha page explicitly links the source rights status as public-domain. Every downloaded page and text is hashed.",
      "author_allowlist":{k:{"romanized":v[0],"death_year":v[1]} for k,v in AUTHORS.items()},
      "catalog_work_count":len(works),"candidates_before_page_check":len(candidates),"sources":[],"skipped":[]}
    for index,(rank,author,work) in enumerate(selected,1):
        slug=work["slug"]; page_url=f"{BASE}/works/{slug}/"
        try:
            page=fetch(page_url).decode("utf-8","replace")
            if not re.search(r'href=["\'][^"\']*public-domain',page,re.I):
                manifest["skipped"].append({"slug":slug,"title":work.get("title"),"reason":"individual page did not confirm public-domain status"})
                continue
            raw=fetch(f"{BASE}/works/{slug}/plaintext")
            body=raw.decode("utf-8").strip()
            if len(body)<3000:
                manifest["skipped"].append({"slug":slug,"title":work.get("title"),"reason":"plaintext shorter than 3000 characters"})
                continue
            safe=re.sub(r"[^\w-]+","-",slug,flags=re.UNICODE).strip("-")
            path=out/(safe+".txt"); path.write_text(body+"\n",encoding="utf-8")
            record={"slug":slug,"title":work.get("title"),"author_ja":author,"author_romanized":AUTHORS[author][0],
              "author_death_year":AUTHORS[author][1],"language":"ja","rights_status":"public-domain-confirmed-on-individual-work-page",
              "work_page":page_url,"plaintext_url":f"{BASE}/works/{slug}/plaintext",
              "catalog_source_hash":work.get("source_content_hash"),"catalog_body_character_count":work.get("body_character_count"),
              "title_keyword_match":any(k in str(work.get("title","")) for k in KEYWORDS),
              "path":path.name,"characters":len(body),"bytes":path.stat().st_size,
              "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
              "license":"Underlying source marked public domain on work page; Soranoha plaintext encoding CC0-1.0; cite Aozora Bunko and Soranoha release"}
            manifest["sources"].append(record)
            print(json.dumps({"n":index,"slug":slug,"title":work.get("title"),"author":author,"chars":len(body)},ensure_ascii=False),flush=True)
        except Exception as exc:
            manifest["skipped"].append({"slug":slug,"title":work.get("title"),"reason":str(exc)[:300]})
        time.sleep(0.35)
    manifest["total_documents"]=len(manifest["sources"])
    manifest["total_bytes"]=sum(x["bytes"] for x in manifest["sources"])
    (out/"AOZORA-ORIGINALS-MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"catalog_works":len(works),"selected_candidates":len(selected),"acquired":manifest["total_documents"],"skipped":len(manifest["skipped"]),"bytes":manifest["total_bytes"]},ensure_ascii=False))
    if manifest["total_documents"]<10: raise SystemExit("Fewer than ten rights-cleared Japanese originals were acquired")
if __name__=="__main__": main()
