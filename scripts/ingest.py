"""S1 data ingest. Owner: Shiv. Rules in DECISIONS D11 and D12.

Steps, in order:
  probe                        check archive paths, timestamp units and 1mo ranking files
  pool [--rank-interval 1mo]   point-in-time top 30 per month -> data/pool.json
  download [--interval 1h]     hourly spot + premium for the pool, checksum-verified
  load --test|--live           split at RESEARCH_END and insert into research_bars / vault_bars
  universe --test|--live       insert universe rows for research months
  verify --test|--live         counts against data/manifest-*.json, no research row past the cutoff

Admin role (CLAUDE.md rule 3) for load and universe only: insert-only, and refuses to run if a
target collection already has data. verify uses the researcher role and never reads vault_bars.
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.config import env  # noqa: E402
from core.data import binance, universe as uni  # noqa: E402
from core.data.load import Window, load_symbol  # noqa: E402
from core.db import get_db  # noqa: E402

WORKERS = 16
POOL_MAX = 100
POOL_FILE = binance.DATA_DIR / "pool.json"


def manifest_file(test: bool) -> Path:
    return binance.DATA_DIR / f"manifest-{'test' if test else 'live'}.json"


def ym(s: str) -> date:
    y, m = s.split("-")[:2]
    return date(int(y), int(m), 1)


def key(m: date) -> str:
    return f"{m.year}-{m.month:02d}"


def pmap(fn, items):
    with ThreadPoolExecutor(WORKERS) as ex:
        return list(ex.map(fn, items))


def window_months() -> tuple[Window, list[date], date]:
    w = Window.from_env()
    months = uni.month_range(w.start.date(), w.end.date())
    return w, months, w.cutoff.date()


def cmd_probe(_args) -> int:
    sym = "BTCUSDT"
    listed = {}
    for interval in ("1mo", "1d"):
        months = listed[interval] = binance.list_months(sym, interval, "spot")
        print(f"spot {interval} files for {sym}: {len(months)}"
              + (f" ({months[0]} to {months[-1]})" if months else ""))
    prem = binance.list_months(sym, "1h", "premium")
    print(f"premium 1h files for {sym}: {len(prem)}" + (f" ({prem[0]} to {prem[-1]})" if prem else ""))
    rank_interval = "1mo" if listed["1mo"] else "1d"
    print(f"ranking interval to use: {rank_interval}")
    checks = [("spot", "1h", 2024, 12, True), ("spot", "1h", 2025, 1, True),
              ("premium", "1h", 2025, 1, True), ("spot", rank_interval, 2024, 12, False)]
    for kind, interval, y, m, verify in checks:
        path = binance.download_month(sym, interval, y, m, kind, verify=verify)
        raw = binance._read_csv(path)["open_time"].iloc[0]
        df = binance.parse_klines(path, kind)
        size = Path(path).stat().st_size
        print(f"{kind:<8}{interval:<4}{y}-{m:02d}  checksum={'ok' if verify else 'skipped':<8}"
              f"{size / 1024:6.1f} KB  rows={len(df):<4} raw_first={raw}  ts_first={df.ts.iloc[0]}"
              + (f"  qv={df.qv.sum():.0f}" if kind == "spot" else ""))
    return 0


def cmd_pool(args) -> int:
    _, months, cutoff = window_months()
    size = int(env("UNIVERSE_SIZE"))
    symbols = binance.list_symbols("spot")
    eligible = uni.eligible_symbols(symbols)
    print(f"spot symbols in archive: {len(symbols)}; eligible USDT pairs: {len(eligible)}")

    available = dict(zip(eligible, pmap(lambda s: binance.list_months(s, args.rank_interval, "spot"),
                                        eligible)))
    needed = {uni.prev_month(m) for m in months}
    jobs = [(s, y, mo) for s, ms in available.items() for (y, mo) in ms if date(y, mo, 1) in needed]
    print(f"ranking files to download ({args.rank_interval}, no checksum): {len(jobs)}")

    def fetch(job):
        s, y, mo = job
        path = binance.download_month(s, args.rank_interval, y, mo, "spot", verify=False)
        return s, date(y, mo, 1), float(binance.parse_klines(path, "spot").qv.sum())

    volumes: dict[str, dict[date, float]] = {}
    for s, m, qv in pmap(fetch, jobs):
        volumes.setdefault(s, {})[m] = qv

    universe = uni.monthly_universe(volumes, months, size)
    research, vault_only = uni.split_pool(universe, cutoff)
    pool = sorted(research | vault_only)

    latest = max((ms[-1] for ms in available.values() if ms), default=None)
    ended = sorted(s for s, ms in available.items() if ms and ms[-1] < latest)
    ended_in_pool = sorted(set(ended) & set(pool))
    POOL_FILE.parent.mkdir(parents=True, exist_ok=True)
    POOL_FILE.write_text(json.dumps({
        "rank_interval": args.rank_interval,
        "universe_size": size,
        "universe": {key(m): syms for m, syms in universe.items()},
        "research_pairs": sorted(research),
        "vault_only_pairs": sorted(vault_only),
        "ended_before_latest_month": ended,
    }, indent=1))
    print(f"pool: {len(pool)} pairs ({len(research)} research, {len(vault_only)} vault-only)")
    print(f"vault-only: {', '.join(sorted(vault_only)) or 'none'}")
    print(f"eligible pairs whose archive ends before {latest}: {len(ended)}; in pool: "
          f"{', '.join(ended_in_pool) or 'none'}")
    print(f"wrote {POOL_FILE}")
    if len(pool) > POOL_MAX:
        print(f"STOP: pool {len(pool)} is above {POOL_MAX}")
        return 1
    return 0


def read_pool() -> dict:
    pool = json.loads(POOL_FILE.read_text())
    n = len(pool["research_pairs"]) + len(pool["vault_only_pairs"])
    if n > POOL_MAX:
        sys.exit(f"pool {n} is above {POOL_MAX}; not continuing")
    return pool


def cmd_download(args) -> int:
    w, months, cutoff = window_months()
    pool = read_pool()
    research = set(pool["research_pairs"])
    symbols = sorted(research | set(pool["vault_only_pairs"]))
    wanted = {s: {(m.year, m.month) for m in months if s in research or m >= cutoff} for s in symbols}

    pairs = [(s, k) for s in symbols for k in binance.KIND_PREFIX]
    listed = pmap(lambda p: binance.list_months(p[0], args.interval, p[1]), pairs)
    jobs = [(s, k, y, m) for (s, k), ms in zip(pairs, listed) for (y, m) in ms if (y, m) in wanted[s]]
    print(f"hourly files to download (checksum-verified): {len(jobs)}")

    def fetch(job):
        s, k, y, m = job
        try:
            return job, Path(binance.download_month(s, args.interval, y, m, k)).stat().st_size, None
        except Exception as exc:  # report every failure, keep going
            return job, 0, str(exc)

    results = pmap(fetch, jobs)
    failures = [(j, e) for j, _, e in results if e]
    total = sum(b for _, b, _ in results)
    print(f"downloaded or reused {len(jobs) - len(failures)} files, {total / 1e6:.1f} MB")
    for (s, k, y, m), e in failures:
        print(f"FAILED {k} {s} {y}-{m:02d}: {e}")
    return 1 if failures else 0


def ensure_empty(db, names: list[str]) -> None:
    for name in names:
        if db[name].find_one({}, {"_id": 1}) is not None:
            sys.exit(f"{db.name}.{name} already has data; refusing to insert. Drop it first.")


def month_filter(args) -> set[tuple[int, int]] | None:
    if not (args.from_month or args.to_month):
        return None
    lo, hi = ym(args.from_month or "1900-01"), ym(args.to_month or "2999-12")
    after_hi = date(hi.year + 1, 1, 1) if hi.month == 12 else date(hi.year, hi.month + 1, 1)
    return {(m.year, m.month) for m in uni.month_range(lo, after_hi)}


def cmd_load(args) -> int:
    w, _, _ = window_months()
    pool = read_pool()
    research = set(pool["research_pairs"])
    symbols = sorted(research | set(pool["vault_only_pairs"]))
    if args.symbols:
        symbols = [s for s in args.symbols.split(",") if s in symbols]
    db = get_db("admin", test=args.test)
    ensure_empty(db, ["research_bars", "vault_bars"])
    months = month_filter(args)
    manifest = {"db": db.name, "months": sorted(months) if months else "all", "symbols": {}}
    for s in symbols:
        counts = load_symbol(db, s, w, s in research, args.interval, months=months)
        manifest["symbols"][s] = {"in_research": s in research, **counts}
        print(f"{s:<14} research={counts['research']:<7} vault={counts['vault']}")
    manifest_file(args.test).write_text(json.dumps(manifest, indent=1))
    tot_r = sum(c["research"] for c in manifest["symbols"].values())
    tot_v = sum(c["vault"] for c in manifest["symbols"].values())
    print(f"{db.name}: inserted {tot_r} research_bars, {tot_v} vault_bars; "
          f"wrote {manifest_file(args.test)}")
    return 0


def cmd_universe(args) -> int:
    _, _, cutoff = window_months()
    pool = read_pool()
    db = get_db("admin", test=args.test)
    ensure_empty(db, ["universe"])
    universe = {ym(k): v for k, v in pool["universe"].items()}
    n = uni.build_universe(db, universe, cutoff)
    print(f"{db.name}: inserted {n} universe rows (months before {cutoff})")
    return 0


def cmd_verify(args) -> int:
    w, months, cutoff = window_months()
    manifest = json.loads(manifest_file(args.test).read_text())
    db = get_db("researcher", test=args.test)
    rows = []

    def check(name, ok, detail=""):
        rows.append(ok)
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))

    for s, c in manifest["symbols"].items():
        for kind, k in c["kinds"].items():
            check(f"{s} {kind}: source == research + vault + skipped",
                  k["source"] == k["research"] + k["vault"] + k["skipped"],
                  f"{k['source']} vs {k['research']}+{k['vault']}+{k['skipped']}")

    late = db.research_bars.count_documents({"ts": {"$gte": w.cutoff}})
    early = db.research_bars.count_documents({"ts": {"$lt": w.start}})
    check("no research_bars row at or after RESEARCH_END", late == 0, f"{late} rows")
    check("no research_bars row before RESEARCH_START", early == 0, f"{early} rows")

    actual = {(d["_id"]["s"], d["_id"]["k"]): d["n"] for d in db.research_bars.aggregate(
        [{"$group": {"_id": {"s": "$meta.symbol", "k": "$meta.kind"}, "n": {"$sum": 1}}}])}
    for s, c in manifest["symbols"].items():
        in_db = 0
        for kind, k in c["kinds"].items():
            got = actual.pop((s, kind), 0)
            in_db += got
            check(f"{s} {kind}: research_bars count matches manifest", got == k["research"],
                  f"db {got}, manifest {k['research']}")
        if not c["in_research"]:
            check(f"{s}: vault-only pair has no research_bars rows", in_db == 0, f"{in_db} rows")
    check("no research_bars rows outside the manifest", not actual, f"{len(actual)} extra groups")

    late_months = db.universe.count_documents({"month": {"$gte": w.cutoff}})
    check("no universe row at or after RESEARCH_END", late_months == 0, f"{late_months} rows")
    if not args.test:
        n_univ = db.universe.count_documents({})
        expected = sum(1 for m in months if m < cutoff)
        check("one universe row per research month", n_univ == expected, f"{n_univ} vs {expected}")

    print(f"\n{sum(rows)}/{len(rows)} checks passed. vault_bars was not read; "
          f"its counts come from the insert results in the manifest.")
    return 0 if all(rows) else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe")
    sp = sub.add_parser("pool")
    sp.add_argument("--rank-interval", default="1mo", choices=["1mo", "1d"])
    sd = sub.add_parser("download")
    sd.add_argument("--interval", default=env("BAR_INTERVAL", "1h"))
    for name in ("load", "universe", "verify"):
        s = sub.add_parser(name)
        target = s.add_mutually_exclusive_group(required=True)
        target.add_argument("--test", action="store_true", help="strata_test")
        target.add_argument("--live", action="store_true", help="strata")
        if name == "load":
            s.add_argument("--interval", default=env("BAR_INTERVAL", "1h"))
            s.add_argument("--symbols", help="comma-separated subset of the pool")
            s.add_argument("--from", dest="from_month", help="YYYY-MM, inclusive")
            s.add_argument("--to", dest="to_month", help="YYYY-MM, inclusive")
    args = p.parse_args()
    return {"probe": cmd_probe, "pool": cmd_pool, "download": cmd_download, "load": cmd_load,
            "universe": cmd_universe, "verify": cmd_verify}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
