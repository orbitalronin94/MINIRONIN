#!/usr/bin/env python3
"""Build a 2M source-traceable factual/persona corpus from World Bank WDI.

The unit of factual knowledge is a country-indicator-year observation.
Millions of rows are created by combining those observations with controlled
question and voice templates; the manifest reports independent observations
separately from generated examples. No projections/forecasts are included.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import gzip
import hashlib
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.worldbank.org/v2"
SOURCE_ID = 2
SOURCE_NAME = "World Development Indicators"
LICENSE = "CC BY 4.0 (World Bank default; verify indicator-specific metadata)"
START_YEAR, END_YEAR = 1960, 2025
TARGET = 2_000_000
SHARD_SIZE = 100_000
INDICATORS = {
    "SP.POP.TOTL": "Population, total",
    "SP.POP.GROW": "Population growth (annual %)",
    "NY.GDP.MKTP.CD": "GDP (current US$)",
    "NY.GDP.PCAP.CD": "GDP per capita (current US$)",
    "NY.GDP.MKTP.KD.ZG": "GDP growth (annual %)",
    "NY.GDP.PCAP.KD.ZG": "GDP per capita growth (annual %)",
    "NY.GNP.PCAP.CD": "GNI per capita (current US$)",
    "FP.CPI.TOTL.ZG": "Inflation, consumer prices (annual %)",
    "SL.UEM.TOTL.ZS": "Unemployment, total (% of total labor force)",
    "SP.DYN.LE00.IN": "Life expectancy at birth, total (years)",
    "SP.URB.TOTL.IN.ZS": "Urban population (% of total population)",
    "SP.RUR.TOTL.ZS": "Rural population (% of total population)",
    "IT.NET.USER.ZS": "Individuals using the Internet (% of population)",
    "IT.CEL.SETS.P2": "Mobile cellular subscriptions (per 100 people)",
    "EG.ELC.ACCS.ZS": "Access to electricity (% of population)",
    "EG.USE.ELEC.KH.PC": "Electric power consumption (kWh per capita)",
    "EG.FEC.RNEW.ZS": "Renewable energy consumption (% of total final energy consumption)",
    "EN.ATM.CO2E.PC": "CO2 emissions (metric tons per capita)",
    "EN.ATM.PM25.MC.M3": "PM2.5 air pollution (micrograms per cubic meter)",
    "AG.LND.FRST.ZS": "Forest area (% of land area)",
    "NE.TRD.GNFS.ZS": "Trade (% of GDP)",
    "NE.EXP.GNFS.ZS": "Exports of goods and services (% of GDP)",
    "NE.IMP.GNFS.ZS": "Imports of goods and services (% of GDP)",
    "SE.ADT.LITR.ZS": "Literacy rate, adult total (% of people ages 15 and above)",
    "SE.PRM.ENRR": "School enrollment, primary (% gross)",
    "SE.XPD.TOTL.GD.ZS": "Government expenditure on education, total (% of GDP)",
    "SH.XPD.CHEX.GD.ZS": "Current health expenditure (% of GDP)",
    "SP.DYN.TFRT.IN": "Fertility rate, total (births per woman)",
    "SP.DYN.IMRT.IN": "Mortality rate, infant (per 1,000 live births)",
    "SH.STA.BASS.ZS": "People using at least basic sanitation services (% of population)",
    "SH.H2O.BASW.ZS": "People using at least basic drinking water services (% of population)",
    "MS.MIL.XPND.GD.ZS": "Military expenditure (% of GDP)",
    "NV.AGR.TOTL.ZS": "Agriculture, forestry, and fishing, value added (% of GDP)",
    "NV.IND.TOTL.ZS": "Industry (including construction), value added (% of GDP)",
    "NV.SRV.TOTL.ZS": "Services, value added (% of GDP)",
    "GC.DOD.TOTL.GD.ZS": "Central government debt, total (% of GDP)",
    "SI.POV.DDAY": "Poverty headcount ratio at $2.15 a day (2017 PPP) (% of population)",
}
QUESTION_FRAMES = [
    "¿Qué valor registró {country} en {year} para «{indicator}»?",
    "Consulta factual: ¿cuál fue «{indicator}» en {country} durante {year}?",
    "Sin adornos: dame el dato de {indicator} para {country} en {year}.",
    "¿Qué cifra publica el Banco Mundial para {indicator}, {country}, {year}?",
    "En la serie histórica, ¿qué valor aparece para {country} en {year} respecto a {indicator}?",
    "Comprueba el dato: {indicator} de {country} en el año {year}.",
    "¿Qué consta en World Development Indicators sobre {indicator} en {country} para {year}?",
    "Necesito la observación de {year}: {indicator}, {country}.",
    "¿Cuál es el registro disponible de {indicator} para {country} ({year})?",
    "Expediente estadístico. Identifica el valor de {indicator} en {country} durante {year}.",
]
VOICE_ENDINGS = [
    "La cifra no necesita maquillaje; ya tiene bastante trabajo siendo una cifra.",
    "No confundas el dato publicado con una explicación causal. Son deportes distintos.",
    "La realidad, esa vieja enemiga de las opiniones improvisadas.",
    "El sarcasmo es gratis; alterar el dato saldría bastante más caro.",
    "Si alguien discrepa, que discuta la serie y el método, no el volumen de su voz.",
    "La fuente ofrece una observación, no una revelación metafísica.",
    "La precisión sigue siendo menos costosa que inventarse una estadística.",
    "Qué contratiempo para quien había preparado la conclusión antes de mirar el número.",
    "No extrapoles alegremente: un año, un indicador y un país no son el planeta entero.",
    "Ahí tienes el registro. La fanfarria interpretativa queda bajo tu responsabilidad.",
]

def fetch_json(url: str, attempts: int = 5):
    request = urllib.request.Request(url, headers={"User-Agent": "MINIRONIN-dataset-builder/1.0 (research; contact: repository maintainer)", "Accept": "application/json"})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            if attempt + 1 == attempts:
                raise RuntimeError(f"World Bank API request failed: {url}: {exc}") from exc
            time.sleep(1.5 * (attempt + 1))

def api_url(path: str, **params) -> str:
    query = urllib.parse.urlencode(params)
    return f"{API}/{path}?{query}"

def fetch_indicator(code: str):
    meta_url = api_url(f"indicator/{urllib.parse.quote(code, safe='.')}", format="json", source=SOURCE_ID)
    meta_payload = fetch_json(meta_url)
    if not isinstance(meta_payload, list) or len(meta_payload) < 2 or not meta_payload[1]:
        return code, None, [], meta_url
    indicator_meta = meta_payload[1][0]
    data_url = api_url(
        f"country/all/indicator/{urllib.parse.quote(code, safe='.')}",
        source=SOURCE_ID, date=f"{START_YEAR}:{END_YEAR}", format="json", per_page=20000, page=1
    )
    first = fetch_json(data_url)
    if not isinstance(first, list) or len(first) < 2 or first[1] is None:
        return code, indicator_meta, [], data_url
    pagination = first[0] or {}
    records = list(first[1] or [])
    pages = int(pagination.get("pages") or 1)
    for page in range(2, pages + 1):
        page_url = api_url(
            f"country/all/indicator/{urllib.parse.quote(code, safe='.')}",
            source=SOURCE_ID, date=f"{START_YEAR}:{END_YEAR}", format="json", per_page=20000, page=page
        )
        payload = fetch_json(page_url)
        if isinstance(payload, list) and len(payload) > 1 and payload[1]:
            records.extend(payload[1])
    return code, indicator_meta, records, data_url

def number_text(value) -> str:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"Invalid numeric value: {value!r}")
    if not number.is_finite():
        raise ValueError(f"Non-finite numeric value: {value!r}")
    rendered = format(number, "f")
    if "." in rendered:
        rendered = rendered.rstrip("0").rstrip(".")
    return rendered or "0"

def make_fact(code, record, meta, data_url):
    country = record.get("country") or {}
    region = country.get("region") or {}
    iso3 = record.get("countryiso3code") or ""
    if len(iso3) != 3 or region.get("value") == "Aggregates":
        return None
    if record.get("value") is None:
        return None
    status = str(record.get("obs_status") or "").strip()
    # Forecasts are not presented as historical observations.
    if "F" in status.upper():
        return None
    year = str(record.get("date") or "")
    if not year.isdigit():
        return None
    try:
        value = number_text(record["value"])
    except ValueError:
        return None
    indicator_name = (meta or {}).get("name") or INDICATORS[code]
    unit = str((meta or {}).get("unit") or record.get("unit") or "").strip()
    country_name = (country.get("value") or iso3).strip()
    fact_id = f"wdi:{iso3}:{code}:{year}"
    fact_payload = {
        "fact_id": fact_id, "country_code": iso3, "country": country_name,
        "indicator_code": code, "indicator": indicator_name, "year": int(year),
        "value": value, "unit": unit, "obs_status": status,
    }
    fact_sha = hashlib.sha256(json.dumps(fact_payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    epistemic = "estimated_by_source" if "E" in status.upper() else "reported_observation"
    return {
        **fact_payload,
        "fact_sha256": fact_sha,
        "source": "World Bank — World Development Indicators",
        "source_url": data_url,
        "source_id": SOURCE_ID,
        "source_note": str((meta or {}).get("sourceNote") or ""),
        "source_organization": str((meta or {}).get("sourceOrganization") or "World Bank"),
        "epistemic_status": epistemic,
        "license": LICENSE,
    }

def make_example(fact, variant: int, index: int):
    q = QUESTION_FRAMES[variant % len(QUESTION_FRAMES)].format(
        country=fact["country"], year=fact["year"], indicator=fact["indicator"]
    )
    voice = VOICE_ENDINGS[(variant // len(QUESTION_FRAMES)) % len(VOICE_ENDINGS)]
    value = fact["value"] + (f" {fact['unit']}" if fact["unit"] else "")
    answer = (
        f"World Development Indicators registra {value} para {fact['indicator']} "
        f"en {fact['country']} ({fact['country_code']}) durante {fact['year']}."
    )
    if fact["epistemic_status"] == "estimated_by_source":
        answer += " La observación está marcada como estimada por la fuente."
    answer += " " + voice
    context = (
        f"Fuente: World Bank, {SOURCE_NAME} (source_id={SOURCE_ID}). "
        f"Indicador: {fact['indicator_code']}. País: {fact['country_code']}. "
        f"Año: {fact['year']}. Estado epistemológico: {fact['epistemic_status']}. "
        "Es una observación de esa serie y ese año; no demuestra causalidad ni describe por sí sola el presente."
    )
    return {
        "id": f"wdi-example-{index:08d}",
        "fact_id": fact["fact_id"],
        "fact_sha256": fact["fact_sha256"],
        "variant": variant,
        "tag": "verifiable_world_bank_statistic",
        "topic": "world_development_indicators",
        "context": context,
        "question": q,
        "answer": answer,
        "source": fact["source"],
        "source_url": fact["source_url"],
        "source_id": SOURCE_ID,
        "source_note": fact["source_note"],
        "source_organization": fact["source_organization"],
        "license": fact["license"],
        "epistemic_status": fact["epistemic_status"],
        "country_code": fact["country_code"],
        "indicator_code": fact["indicator_code"],
        "year": fact["year"],
        "value": fact["value"],
        "unit": fact["unit"],
        "generation_method": "wdi_observation_x_question_frame_x_erudite_cynical_voice_v1",
    }

def write_shards(facts, target, shard_size, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    variants_per_fact = math.ceil(target / len(facts))
    if variants_per_fact > len(QUESTION_FRAMES) * len(VOICE_ENDINGS):
        raise SystemExit(
            f"Not enough independent observations: {len(facts)} facts × "
            f"{len(QUESTION_FRAMES) * len(VOICE_ENDINGS)} variants cannot reach {target:,}"
        )
    shard_meta = []
    buffer, written, shard_no = [], 0, 1
    def flush(rows, number):
        path = out_dir / f"minironin-worldbank-verifiable-2m-v1-part{number:02d}.jsonl.gz"
        raw = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n" for row in rows).encode("utf-8")
        packed = gzip.compress(raw, compresslevel=6, mtime=0)
        path.write_bytes(packed)
        return {"file": str(path.relative_to(ROOT)), "records": len(rows), "bytes": len(packed), "sha256": hashlib.sha256(packed).hexdigest()}
    for fact in facts:
        for variant in range(variants_per_fact):
            if written >= target:
                break
            row = make_example(fact, variant, written + 1)
            buffer.append(row)
            written += 1
            if len(buffer) >= shard_size:
                shard_meta.append(flush(buffer, shard_no))
                buffer = []
                shard_no += 1
        if written >= target:
            break
    if buffer:
        shard_meta.append(flush(buffer, shard_no))
    return written, variants_per_fact, shard_meta

def self_test():
    assert number_text("100.0000") == "100"
    assert number_text("0.1250") == "0.125"
    meta = {"name": "Population, total", "unit": "", "sourceNote": "Test note", "sourceOrganization": "World Bank"}
    record = {
        "country": {"value": "Testland", "region": {"value": "Latin America"}},
        "countryiso3code": "TST", "date": "2020", "value": 12345,
        "obs_status": "",
    }
    fact = make_fact("SP.POP.TOTL", record, meta, "https://api.worldbank.org/test")
    assert fact and fact["value"] == "12345" and fact["epistemic_status"] == "reported_observation"
    assert make_example(fact, 0, 1)["fact_id"] == "wdi:TST:SP.POP.TOTL:2020"
    forecast = dict(record, obs_status="F")
    assert make_fact("SP.POP.TOTL", forecast, meta, "https://api.worldbank.org/test") is None
    print("self_test=passed")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=TARGET)
    parser.add_argument("--shard-size", type=int, default=SHARD_SIZE)
    parser.add_argument("--output-dir", default="data/curated/minironin-worldbank-verifiable-2m-v1")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.target < 1 or args.shard_size < 1:
        parser.error("target and shard-size must be positive")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(fetch_indicator, code) for code in INDICATORS]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: item[0])
    facts, indicator_audit = [], []
    for code, meta, records, data_url in results:
        before = len(facts)
        if meta:
            for record in records:
                fact = make_fact(code, record, meta, data_url)
                if fact:
                    facts.append(fact)
        indicator_audit.append({
            "indicator_code": code,
            "indicator_name": (meta or {}).get("name") or INDICATORS[code],
            "api_records_returned": len(records),
            "independent_observations_accepted": len(facts) - before,
            "source_note": str((meta or {}).get("sourceNote") or ""),
            "source_organization": str((meta or {}).get("sourceOrganization") or ""),
            "source_url": data_url,
            "metadata_available": bool(meta),
        })
    unique = {}
    for fact in facts:
        unique[fact["fact_id"]] = fact
    facts = sorted(unique.values(), key=lambda f: (f["indicator_code"], f["country_code"], f["year"]))
    minimum = math.ceil(args.target / (len(QUESTION_FRAMES) * len(VOICE_ENDINGS)))
    if len(facts) < minimum:
        raise SystemExit(
            f"Only {len(facts):,} independent observations found; at least {minimum:,} "
            "are required for the requested volume without recycling the same fact excessively."
        )
    output = ROOT / args.output_dir
    written, variants, shards = write_shards(facts, args.target, args.shard_size, output)
    manifest = {
        "dataset": "MINIRONIN World Bank verifiable statistics with erudite cynical voice",
        "version": 1,
        "target_examples": args.target,
        "records_written": written,
        "independent_observations": len(facts),
        "unique_fact_ids": len({f["fact_id"] for f in facts}),
        "indicators_requested": len(INDICATORS),
        "indicators_with_observations": sum(1 for x in indicator_audit if x["independent_observations_accepted"]),
        "year_range": [START_YEAR, END_YEAR],
        "source_database": SOURCE_NAME,
        "source_id": SOURCE_ID,
        "source_api": API,
        "source_license": LICENSE,
        "attribution": "World Bank, World Development Indicators; data retrieved through the World Bank Indicators API v2. Changes: Spanish questions/answers and original dry-humour framing generated from numeric observations.",
        "variants_per_fact": variants,
        "maximum_templates_per_fact": len(QUESTION_FRAMES) * len(VOICE_ENDINGS),
        "method": "country-indicator-year observations × controlled question frames × original dry-humour voice endings",
        "indicator_audit": indicator_audit,
        "shards": shards,
        "quality_policy": {
            "only_non_null_numeric_observations": True,
            "forecast_status_F_excluded": True,
            "estimated_observations_labeled": True,
            "historical_year_preserved": True,
            "country_and_indicator_codes_preserved": True,
            "no_causal_claims_added": True,
            "no_fact_recycling_beyond_template_combinations": True,
        },
        "training_status": "candidate_only_not_wired_into_training",
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
