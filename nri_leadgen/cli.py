"""CLI entry point.

    python -m nri_leadgen.cli --config config.yaml --out-csv leads.csv --out-xlsx leads.xlsx

With no config it runs the offline seed source only.
"""
from __future__ import annotations
import argparse, os, sys
from .pipeline import run
from .export import to_csv, to_excel


def load_config(path):
    if not path:
        return {"sources": {"seed_csv": {"enabled": True}}, "min_liquid_usd_m": 30.0}
    if not os.path.exists(path):
        sys.exit(f"Config not found: {path}")
    try:
        import yaml
    except ImportError:
        sys.exit("PyYAML not installed. Run: pip install -r requirements.txt")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Signal-driven UHNW NRI/OCI lead generator")
    ap.add_argument("--config", help="YAML config (see config.example.yaml)")
    ap.add_argument("--out-csv", default="output/leads.csv")
    ap.add_argument("--out-xlsx", default="output/leads.xlsx")
    ap.add_argument("--top", type=int, default=0)
    args = ap.parse_args(argv)
    cfg = load_config(args.config)
    print("Running lead pipeline...")
    leads = run(cfg)
    os.makedirs(os.path.dirname(args.out_csv) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(args.out_xlsx) or ".", exist_ok=True)
    to_csv(leads, args.out_csv)
    try:
        to_excel(leads, args.out_xlsx)
        print(f"Wrote {len(leads)} leads -> {args.out_csv} and {args.out_xlsx}")
    except SystemExit as e:
        print(f"CSV written ({args.out_csv}); Excel skipped: {e}")
    n = args.top or min(10, len(leads))
    print(f"\nTop {n} leads (signal-driven):")
    for l in leads[:n]:
        ev = f"{l.event_type or '-'} {l.event_date or ''}".strip()
        print(f"  [{l.lead_score:>3}] {l.priority:<11} {l.name[:26]:<26} {l.company[:18]:<18} {ev:<22} {l.exchange_ticker}")


if __name__ == "__main__":
    main()
