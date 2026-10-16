"""Robusthetstest: gir Luna pålitelige svar under last når 429 håndteres?

Se docs/ki-logg/2026-10-16-robusthet-luna.md. Uten --live er dette en tørrkjøring.
call_with_policy er en prototype for retry-politikken i adaptere/ki, ikke appkode.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import random
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone

import modelltest_beslutning as decision
import modelltest_openrouter as base

ROOT = base.ROOT
MODEL = "openai/gpt-6-luna"
OUT = ROOT / "docs/ki-logg/robusthetstest"
# Recommended policy: at most 5 calls in flight, retry 429 and transient errors with
# backoff (or Retry-After), and give up after 25 s so the row shows the fallback text.
POLICY = {"navn": "anbefalt", "samtidige": 5, "budsjett_s": 25.0,
          "backoff_s": [1.0, 2.0, 4.0, 8.0], "retry_after_maks_s": 10.0}
BASELINE = {"navn": "ingen", "samtidige": 1000, "budsjett_s": 0.0, "backoff_s": [],
            "retry_after_maks_s": 0.0}
RETRYABLE = {429, 500, 502, 503, 504, "nettverksfeil"}
HEADER_PREFIXES = ("x-ratelimit", "retry-after")

# Each wave: (start offset in seconds, kind, number of calls). A shift has 10 candidates.
SCENARIOS = {
    "S1_en_vakt": [(0, "forklaring", 10)],
    "S2_to_vakter_samtidig": [(0, "forklaring", 10), (0, "forklaring", 10)],
    "S3_fem_vakter_5s_mellom": [(5 * i, "forklaring", 10) for i in range(5)],
    "S4_tre_vakter_gjenapnet": [(0, "forklaring", 10)] * 3 + [(3, "forklaring", 10)] * 3,
    "S5_tolk_30_preferanser": [(0, "preferanse", 30)],
}


def request_once(key, payload):
    """One HTTP request. Keeps rate-limit headers and limit metadata, never prompt text."""
    request = base.Request(base.BASE + "chat/completions", data=json.dumps(payload).encode("utf-8"),
                           headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    start = time.monotonic()
    result = {"status": None, "headers": {}, "content": None, "usage": None}
    try:
        with base.build_opener(base.NoRedirect).open(request, timeout=45) as response:
            body = json.load(response)
        result["status"] = 200
        choice = (body.get("choices") or [{}])[0]
        result["content"] = (choice.get("message") or {}).get("content")
        result["finish_reason"] = choice.get("finish_reason")
        result["usage"] = body.get("usage")
    except base.HTTPError as error:
        result["status"] = error.code
        result["headers"] = {k.lower(): v for k, v in (error.headers or {}).items()
                             if k.lower().startswith(HEADER_PREFIXES)}
        try:
            meta = (json.load(error).get("error") or {}).get("metadata") or {}
            result["limit_source"] = meta.get("limit_source")
        except (ValueError, AttributeError):
            pass
    except (base.URLError, TimeoutError, OSError):
        result["status"] = "nettverksfeil"
    result["seconds"] = round(time.monotonic() - start, 3)
    return result


def retry_wait(result, attempt, policy, rng):
    header = result.get("headers", {}).get("retry-after")
    try:
        if header is not None:
            return min(float(header), policy["retry_after_maks_s"])
    except ValueError:
        pass
    return policy["backoff_s"][attempt] * (1 + 0.25 * rng.random())


def call_with_policy(key, payload, case, policy, gate, rng, send=request_once,
                     sleep=time.sleep, clock=time.monotonic):
    """Returns ok, ubrukelig (answer unusable) or feilet (gave up), with every attempt."""
    attempts = []
    with gate:
        start = clock()
        for attempt in range(len(policy["backoff_s"]) + 1):
            result = send(key, payload)
            attempts.append({k: result.get(k) for k in ["status", "seconds", "headers", "limit_source"]})
            if result["status"] == 200:
                answer, errors = base.check_format(case, result["content"])
                usable = not errors and result.get("finish_reason") == "stop"
                return {"utfall": "ok" if usable else "ubrukelig", "forsok": attempts,
                        "sekunder": round(clock() - start, 3), "usage": result.get("usage")}
            if result["status"] not in RETRYABLE or attempt == len(policy["backoff_s"]):
                break
            wait = retry_wait(result, attempt, policy, rng)
            if clock() - start + wait > policy["budsjett_s"]:
                break
            sleep(wait)
    return {"utfall": "feilet", "forsok": attempts, "sekunder": round(clock() - start, 3), "usage": None}


def run_scenario(key, waves, policy, rng, cases):
    gate = threading.BoundedSemaphore(policy["samtidige"])
    by_kind = {kind: [c for c in cases if c["kind"] == kind] for kind in ("preferanse", "forklaring")}
    jobs = []
    for index, (offset, kind, count) in enumerate(waves):
        for i in range(count):
            case = by_kind[kind][i % len(by_kind[kind])]
            jobs.append((index, offset, case, decision.payload_for(case, MODEL, "B")))
    t0 = time.monotonic()

    def job(item):
        index, offset, case, payload = item
        time.sleep(max(0.0, t0 + offset - time.monotonic()))
        outcome = call_with_policy(key, payload, case, policy, gate, rng)
        outcome.update({"bolge": index, "sak": case["id"],
                        "ferdig_etter_bolgestart_s": round(time.monotonic() - t0 - offset, 3)})
        return outcome

    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        outcomes = list(pool.map(job, jobs))
    return outcomes


def summarize(outcomes):
    waves = {}
    for o in outcomes:
        waves.setdefault(o["bolge"], []).append(o["ferdig_etter_bolgestart_s"])
    return {
        "kall": len(outcomes),
        "ok": sum(o["utfall"] == "ok" for o in outcomes),
        "ubrukelig": sum(o["utfall"] == "ubrukelig" for o in outcomes),
        "feilet": sum(o["utfall"] == "feilet" for o in outcomes),
        "http_429": sum(a["status"] == 429 for o in outcomes for a in o["forsok"]),
        "andre_feil": sum(a["status"] not in (200, 429) for o in outcomes for a in o["forsok"]),
        "kall_med_nytt_forsok": sum(len(o["forsok"]) > 1 for o in outcomes),
        "maks_kall_s": max(o["sekunder"] for o in outcomes),
        "bolge_ferdig_maks_s": round(max(max(v) for v in waves.values()), 3),
        "kostnad_usd": round(sum((o["usage"] or {}).get("cost") or 0 for o in outcomes), 7),
        "limit_source": sorted({a.get("limit_source") or "" for o in outcomes for a in o["forsok"]} - {""}),
        "retry_after_sett": sorted({a["headers"].get("retry-after") for o in outcomes for a in o["forsok"]
                                    if a.get("headers", {}).get("retry-after")}),
        "ratelimit_headere_sett": sorted({k for o in outcomes for a in o["forsok"] for k in a.get("headers", {})}),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Send betalte modellkall.")
    parser.add_argument("--runder", type=int, default=2, help="Gjentakelser av S1–S5 med anbefalt politikk.")
    parser.add_argument("--pause", type=float, default=60.0, help="Sekunder mellom scenarioer.")
    parser.add_argument("--max-kostnad", type=float, default=0.10)
    args = parser.parse_args()
    plan = [("S2_to_vakter_samtidig", BASELINE), ("S4_tre_vakter_gjenapnet", BASELINE)]
    plan += [(name, POLICY) for _ in range(args.runder) for name in SCENARIOS]
    calls = sum(n for name, _ in plan for _, _, n in SCENARIOS[name])
    if not args.live:
        print(f"Tørrkjøring: {len(plan)} scenariokjøringer, {calls} kall mot {MODEL}, ingen nettverk.")
        return 0
    key, _ = base.configuration(MODEL)
    cases = decision.load_cases()
    rng = random.Random(20261016)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    OUT.mkdir(parents=True, exist_ok=True)
    output = OUT / f"robusthet-{stamp}.json"
    report = {"started_utc": stamp, "model": MODEL, "policy": POLICY, "baseline": BASELINE,
              "scenarios": SCENARIOS, "script_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest(),
              "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "python": sys.version.split()[0], "runs": [], "status": "in-progress"}
    spent = 0.0
    for number, (name, policy) in enumerate(plan):
        if number:
            time.sleep(args.pause)
        started = datetime.now(timezone.utc).isoformat(timespec="seconds")
        outcomes = run_scenario(key, SCENARIOS[name], policy, rng, cases)
        summary = summarize(outcomes)
        spent += summary["kostnad_usd"]
        report["runs"].append({"scenario": name, "politikk": policy["navn"], "start_utc": started,
                               "summary": summary, "outcomes": outcomes})
        base.write_report(output, report, key)
        print(f"{name} [{policy['navn']}]: ok {summary['ok']}/{summary['kall']}, feilet {summary['feilet']}, "
              f"429 {summary['http_429']}, maks bølge {summary['bolge_ferdig_maks_s']}s", flush=True)
        if spent > args.max_kostnad:
            report["status"] = "stopped-budget"
            break
    else:
        report["status"] = "completed"
    report["spent_usd"] = round(spent, 7)
    base.write_report(output, report, key)
    print(f"Kostnad USD {report['spent_usd']}. Rapport: {output.relative_to(ROOT)}")
    return 0 if report["status"] == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
