"""Run the SDK's RGS verification on the exact files in library/publish_files - after finish_luts.py and
shrink_books.py have rewritten them - and print the 3-star numbers per mode.

run.py --checks reads books_<mode>.verification.json, a sidecar written by the sims with the SHA-256 of
the books as they were simulated; shrink_books.py rewrites the books (same ids, payouts and events,
compact winInfo), so that hash no longer matches and the fast path would stop on it. This moves the stale
sidecars aside, runs utils/rgs_verification.execute_all_tests on its full path (every book read, its
payoutMultiplier compared with the lookup table's), then writes fresh sidecars for the files as they are.

    python verify_publish.py          (PYTHONPATH = math-sdk)
"""
import hashlib
import io
import json
import os
import pickle
import sys

import zstandard

HERE = os.path.dirname(os.path.abspath(__file__))
SDK = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [HERE, SDK]

from game_config import GameConfig  # noqa: E402
from src.write_data.write_data import get_sha_256  # noqa: E402
from utils.rgs_verification import execute_all_tests  # noqa: E402

KEYS = ("rtp", "std", "non_zero_hr", "prob_nil", "hr_max", "max_win", "prob5k", "prob10k", "etl40b",
        "etl10k", "cvar", "m2m", "num_non_zero_payouts")


def book_payouts(path):
    out = []
    with open(path, "rb") as fh:
        for line in io.TextIOWrapper(zstandard.ZstdDecompressor().stream_reader(fh, read_across_frames=True),
                                     encoding="utf-8"):
            if line.strip():
                out.append(json.loads(line)["payoutMultiplier"])
    return out


def main():
    os.chdir(SDK)   # rgs_verification writes games/<id>/library/stats_summary.json relative to the SDK root
    config = GameConfig()
    cfg_dir = os.path.join(config.library_path, "configs")
    for bm in config.bet_modes:
        side = os.path.join(cfg_dir, f"books_{bm.get_name()}.verification.json")
        if os.path.exists(side):
            os.replace(side, side + ".stale")
    execute_all_tests(config)
    for bm in config.bet_modes:
        name = bm.get_name()
        book = os.path.join(config.publish_path, f"books_{name}.jsonl.zst")
        payouts = book_payouts(book)
        side = os.path.join(cfg_dir, f"books_{name}.verification.json")
        with open(side, "w", encoding="UTF-8") as f:
            json.dump({"payout_hash": hashlib.md5(pickle.dumps(payouts)).hexdigest(),
                       "file_hash": get_sha_256(book), "num_entries": len(payouts)}, f, indent=2)
        if os.path.exists(side + ".stale"):
            os.remove(side + ".stale")
    stats = json.load(open(os.path.join(config.library_path, "stats_summary.json"), encoding="UTF-8"))
    print("\nmode           " + "  ".join(f"{k:>11}" for k in KEYS))
    for name, s in stats.items():
        print(f"{name:<14} " + "  ".join(f"{s.get(k) if not isinstance(s.get(k), float) else round(s.get(k), 6):>11}"
                                        for k in KEYS))
    print("\n3-star limits: rtp <= 0.967, etl10k <= 0.8, etl40b <= 0.9, prob5k <= 0.01, prob10k <= 0.005, cvar <= 800")


if __name__ == "__main__":
    main()
