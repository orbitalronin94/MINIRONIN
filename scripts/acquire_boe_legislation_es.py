#!/usr/bin/env python3
"""Acquire current Spanish consolidated legislation from the official BOE API."""
from __future__ import annotations
import argparse,concurrent.futures,datetime,hashlib,gzip,html,json,re,time
from pathlib import Path
import requests
import xml.etree.ElementTree as ET

BASE="https://www.boe.es/datosabiertos/api/legislacion-consolidada"
SOURCE="https://www.boe.es"
LICENSE="BOE reuse terms (effective 2024-06-28): commercial and non-commercial reuse and derivatives permitted; attribution required"
ATTRIBUTION="Basado en datos de la Agencia Estatal Boletín Oficial del Estado (BOE). Fuente: https://www.boe.es"
USER_AGENT="MINIRONIN-open-data-acquisition/1.0 (+https://github.com/orbitalronin94/MINIRONIN)"
TODAY=datetime.date.today().strftime("%Y%m%d")

def text(node,tag):
    if node is None:return ""
    child=node.find(tag)
    return "" if child is None or child.text is None else child.text.strip()
def norm(s):
    return re.sub(r"\s+"," ",html.unescape(str(s or ""))).strip()
def sha(s):return hashlib.sha256(norm(s).encode("utf-8")).hexdigest()
def get_json(url,params=None):
    last=None
    for attempt in range(5):
        try:
            r=requests.get(url,params=params,headers={"Accept":"application/json","User-Agent":USER_AGENT},timeout=(15,90))
            if r.status_code==429 or r.status_code>=500:
                time.sleep(min(2**attempt,12));continue
            r.raise_for_status()
            data=r.json()
            if str(data.get("status",{}).get("code","200"))!="200":raise RuntimeError(f"BOE API status: {data.get('status')}")
            return data
        except Exception as e:
            last=e
            if attempt<4:time.sleep(min(2**attempt,12))
    raise RuntimeError(f"BOE API GET failed: {last}")
def get_xml(law_id):
    url=f"{BASE}/id/{law_id}"
    last=None
    for attempt in range(5):
        try:
            r=requests.get(url,headers={"Accept":"application/xml","User-Agent":USER_AGENT},timeout=(15,120))
            if r.status_code==429 or r.status_code>=500:
                time.sleep(min(2**attempt,12));continue
            if r.status_code==404:return None,"not_consolidated"
            r.raise_for_status()
            root=ET.fromstring(r.content)
            code=root.findtext("./status/code") or "200"
            if code!="200":return None,f"api_status_{code}"
            return root,None
        except Exception as e:
            last=e
            if attempt<4:time.sleep(min(2**attempt,12))
    return None,f"request_error:{last}"
def current_version(block):
    expiry=block.attrib.get("fecha_caducidad","")
    if expiry and expiry.isdigit() and expiry<=TODAY:return None
    versions=block.findall("version")
    eligible=[]
    for idx,v in enumerate(versions):
        date=v.attrib.get("fecha_vigencia") or v.attrib.get("fecha_publicacion") or "00000000"
        if not date.isdigit() or date<=TODAY:eligible.append((date,idx,v))
    if not eligible:return None
    return max(eligible,key=lambda x:(x[0],x[1]))[2]
def extract_law(item):
    law_id=str(item.get("identificador","")).strip()
    if not law_id:return [],"missing_id"
    root,error=get_xml(law_id)
    if error:return [],error
    meta=root.find("./data/metadatos")
    law_text=root.find("./data/texto")
    if meta is None or law_text is None:return [],"missing_metadata_or_text"
    repeal=text(meta,"estatus_derogacion")
    annul=text(meta,"estatus_anulacion")
    exhausted=text(meta,"vigencia_agotada")
    # Admit only laws that remain in force. Historical/repealed acts stay out
    # of this current-law training stream.
    if repeal=="S" or annul=="S" or exhausted=="S":return [],"not_current"
    title=text(meta,"titulo") or str(item.get("titulo",""))
    law_url=text(meta,"url_html_consolidada") or str(item.get("url_html_consolidada",""))
    eli=text(meta,"url_eli") or str(item.get("url_eli",""))
    metadata={
        "law_id":law_id,"law_title":title,"url_html_consolidada":law_url,"url_eli":eli,
        "fecha_actualizacion":text(meta,"fecha_actualizacion"),
        "fecha_disposicion":text(meta,"fecha_disposicion"),
        "fecha_publicacion":text(meta,"fecha_publicacion"),
        "numero_oficial":text(meta,"numero_oficial"),
        "ambito":text(meta,"ambito"),"departamento":text(meta,"departamento"),
        "rango":text(meta,"rango"),"vigencia_agotada":exhausted,
        "estatus_derogacion":repeal,"estatus_anulacion":annul,
        "estado_consolidacion":text(meta,"estado_consolidacion")
    }
    records=[]
    for block in law_text.findall("bloque"):
        version=current_version(block)
        if version is None:continue
        pieces=[norm(x) for x in version.itertext()]
        body=norm(" ".join(x for x in pieces if x))
        if len(body)<80:continue
        block_id=block.attrib.get("id","")
        block_title=block.attrib.get("titulo","")
        block_type=block.attrib.get("tipo","")
        version_date=version.attrib.get("fecha_vigencia") or version.attrib.get("fecha_publicacion","")
        content=(f"{title}\n{block_title}\n{body}").strip()
        record={
            "id":f"boe:{law_id}:{block_id or sha(body)[:16]}",
            "text":content,"domain":"legislación española vigente","language":"es",
            "split":"train","train_eligible":True,"admission_status":"accepted",
            "synthetic":False,"license":LICENSE,"source_dataset":"BOE legislación consolidada",
            "source":SOURCE,"source_url":law_url,"source_revision":metadata["fecha_actualizacion"],
            "attribution":ATTRIBUTION,
            "informative_only":True,
            "disclaimer":"Texto consolidado de carácter meramente informativo; no tiene carácter oficial o auténtico. Para efectos jurídicos, consulte la publicación oficial en el BOE.",
            "block_id":block_id,"block_title":block_title,"block_type":block_type,
            "version_date":version_date,**metadata
        }
        records.append(record)
    return records,None
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--offset",type=int,required=True)
    ap.add_argument("--limit",type=int,default=3000)
    ap.add_argument("--output-dir",type=Path,default=Path("out"))
    ap.add_argument("--workers",type=int,default=2)
    a=ap.parse_args()
    if a.offset<0 or a.limit<1 or a.limit>4000:raise SystemExit("invalid offset/limit")
    listing=get_json(BASE,{"offset":a.offset,"limit":a.limit})
    items=listing.get("data",[])
    if isinstance(items,dict):items=items.get("item",[]) if isinstance(items.get("item",[]),list) else [items.get("item")]
    if not isinstance(items,list):raise SystemExit("unexpected BOE list schema")
    a.output_dir.mkdir(parents=True,exist_ok=True)
    out=a.output_dir/f"boe-legislation-es-{a.offset:05d}.jsonl.gz"
    digest=hashlib.sha256();seen=set()
    counts={"not_current":0,"not_consolidated":0,"missing_metadata_or_text":0}
    errors=[];laws_ok=0;records=0
    with gzip.open(out,"wt",encoding="utf-8",newline="\n",compresslevel=6) as f:
        with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
            futures={pool.submit(extract_law,item):item for item in items}
            for future in concurrent.futures.as_completed(futures):
                item=futures[future]
                try:rows,error=future.result()
                except Exception as e:rows,error=[],f"exception:{e}"
                if error:
                    if error in counts:counts[error]+=1
                    else:errors.append({"id":item.get("identificador"),"error":error[:300]})
                    continue
                if rows:laws_ok+=1
                for row in rows:
                    h=sha(row["text"])
                    if h in seen:continue
                    seen.add(h)
                    line=json.dumps(row,ensure_ascii=False,separators=(",",":"))+"\n"
                    f.write(line);digest.update(line.encode("utf-8"));records+=1
    manifest={
        "schema_version":1,"dataset":"BOE legislación consolidada vigente",
        "source_api":BASE,"source_terms":"https://www.boe.es/informacion/aviso_legal/index.php",
        "license":LICENSE,"attribution_required":True,"language":"es",
        "offset":a.offset,"limit":a.limit,"listing_records":len(items),
        "laws_with_current_text":laws_ok,"records_admitted":records,
        "excluded_or_missing_counts":counts,"other_errors":errors[:100],
        "file":out.name,"sha256_jsonl_uncompressed":digest.hexdigest(),
        "retrieved_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "deduplication":"exact SHA-256 of normalized block text within batch",
        "exclusions":[
            "Only BOE consolidated legislation API is used; Biblioteca Jurídica Digital (CC BY-NC-ND 4.0) and BORME/other announcements are excluded.",
            "Repealed, annulled or exhausted laws are excluded from the current-law stream.",
            "For each article/block, only the latest version effective on retrieval date is admitted.",
            "Each record is marked informative-only and retains the BOE source URL and attribution."
        ],
        "reuse_conditions":[
            "Commercial and non-commercial reuse and derivatives are permitted under BOE reuse terms effective 2024-06-28.",
            "Attribution to the Agencia Estatal BOE is mandatory.",
            "Consolidated texts are informative only and must not be represented as official or authentic."
        ]
    }
    (a.output_dir/f"boe-legislation-es-{a.offset:05d}.manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:manifest[k] for k in ("offset","listing_records","laws_with_current_text","records_admitted","excluded_or_missing_counts","sha256_jsonl_uncompressed")},ensure_ascii=False))
    if records==0:raise SystemExit("no current law blocks admitted in this batch")
if __name__=="__main__":main()
