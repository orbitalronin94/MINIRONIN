#!/usr/bin/env python3
"""Inspect BNE public-domain metadata and discover reusable OCR text links."""
from __future__ import annotations
import argparse, csv, hashlib, io, json, re, time, urllib.request, zipfile
from datetime import datetime, timezone
from pathlib import Path

URL="https://www.bne.es/media/datosgob/bdh/dominiopublico/dominiopublico_csv-utf8.zip"
LICENSE="CC BY 4.0 (BNE public-domain dataset distribution)"
USER_AGENT="MINIRONIN-open-data-audit/1.0 (+https://github.com/orbitalronin94/MINIRONIN)"

def download(url: str) -> bytes:
    last=None
    for attempt in range(4):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT})
            with urllib.request.urlopen(req,timeout=120) as response:
                if response.status != 200: raise RuntimeError(f"HTTP {response.status}")
                data=response.read()
                if not data: raise RuntimeError("empty download")
                return data
        except Exception as exc:
            last=exc
            if attempt < 3: time.sleep(2**attempt)
    raise RuntimeError(f"download failed after retries: {last}")

def clean(v,limit=500):
    s=str(v or "").strip()
    return s[:limit]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",default="data/manifests/bne-pd-metadata-audit.json")
    args=ap.parse_args()
    raw=download(URL)
    zip_sha=hashlib.sha256(raw).hexdigest()
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        candidates=[i for i in zf.infolist() if not i.is_dir() and i.filename.lower().endswith((".csv",".txt"))]
        if not candidates: raise SystemExit("BNE ZIP contains no CSV/TXT metadata file")
        member=max(candidates,key=lambda x:x.file_size)
        if member.file_size > 500_000_000: raise SystemExit(f"metadata CSV unexpectedly large: {member.file_size}")
        content=zf.read(member)
    csv_sha=hashlib.sha256(content).hexdigest()
    text=content.decode("utf-8-sig",errors="replace")
    sample=text[:100_000]
    try: dialect=csv.Sniffer().sniff(sample,delimiters=",;|\t")
    except csv.Error: dialect=csv.excel
    reader=csv.DictReader(io.StringIO(text),dialect=dialect)
    fields=list(reader.fieldnames or [])
    if len(fields)<5: raise SystemExit(f"unexpected BNE metadata schema: {fields}")
    normalized={f:re.sub(r"[^a-z0-9]","",f.casefold()) for f in fields}
    url_fields=[f for f,n in normalized.items() if any(k in n for k in ("url","link","enlace","uri","http"))]
    text_fields=[f for f,n in normalized.items() if any(k in n for k in ("ocr","texto","text","txt","transcripcion","fulltext"))]
    subject_fields=[f for f,n in normalized.items() if any(k in n for k in ("materia","subject","tema","descriptor","keyword","asunto"))]
    title_fields=[f for f,n in normalized.items() if any(k in n for k in ("titulo","title","nombre","denominacion"))]
    author_fields=[f for f,n in normalized.items() if any(k in n for k in ("autor","author","creador","responsable"))]
    count=0; ocr_count=0; url_count=0; topic_counts={"filosofia":0,"matematicas":0,"ciencia":0,"historia":0}
    samples=[]; topic_samples={k:[] for k in topic_counts}
    for row in reader:
        count+=1
        values=[str(v or "") for v in row.values()]
        urls=[v for v in values if v.startswith("http")]
        url_count += bool(urls)
        text_urls=[v for v in urls if re.search(r"(\.txt\b|\.xml\b|ocr|texto|full.?text)",v,re.I)]
        ocr_count += bool(text_urls)
        combined=" ".join(values).casefold()
        for topic,terms in {
            "filosofia":("filosof","metafis","etica","moral","logica","ontologia"),
            "matematicas":("matematic","algebra","geometr","aritmet","calculo"),
            "ciencia":("ciencia","fisica","quimica","biologia","astronomia","medicina"),
            "historia":("historia","cronica","geografia","arqueologia","histori"),
        }.items():
            if any(t in combined for t in terms):
                topic_counts[topic]+=1
                if len(topic_samples[topic])<5:
                    topic_samples[topic].append({k:clean(row.get(k)) for k in fields if k in title_fields+author_fields+subject_fields+url_fields+text_fields})
        if len(samples)<12:
            samples.append({k:clean(row.get(k)) for k in fields if k in title_fields+author_fields+subject_fields+url_fields+text_fields})
    if count < 100: raise SystemExit(f"unexpectedly small BNE metadata set: {count}")
    report={
        "schema":"minironin-bne-public-domain-metadata-audit-v1",
        "source":"Biblioteca Nacional de España — BNE Digital, documentos en dominio público",
        "metadata_url":"https://datos.gob.es/es/catalogo/ea0019768-biblioteca-digital-documentos-en-dominio-publico1",
        "download_url":URL,"license":LICENSE,"retrieved_at_utc":datetime.now(timezone.utc).isoformat(),
        "zip_bytes":len(raw),"zip_sha256":zip_sha,"member":member.filename,
        "csv_bytes":len(content),"csv_sha256":csv_sha,"record_count":count,"fields":fields,
        "url_fields":url_fields,"text_or_ocr_fields":text_fields,"subject_fields":subject_fields,
        "title_fields":title_fields,"author_fields":author_fields,
        "rows_with_any_url":int(url_count),"rows_with_probable_ocr_url":ocr_count,
        "topic_keyword_counts":topic_counts,"sample_rows":samples,"topic_samples":topic_samples,
        "admission_status":"metadata audit only; no full-text documents admitted yet",
        "next_gate":"Confirm OCR URL field and per-item rights/attribution, then download a stratified sample and audit text quality before bulk admission."
    }
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:report[k] for k in ("record_count","fields","url_fields","text_or_ocr_fields",
        "rows_with_any_url","rows_with_probable_ocr_url","topic_keyword_counts","zip_sha256","csv_sha256")},ensure_ascii=False))

if __name__=="__main__": main()
