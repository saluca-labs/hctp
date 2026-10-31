"""HCTP -00 rolling-root test vectors, computed from the draft TEXT ONLY (sections 3.1 and 4).

Deliberately does not import velamen.hctp: this is the check against it, not a copy of it.
Run with --check <path-to-velamen-package-parent> to compare against the reference code.

Section 3.1 does not say how non-ASCII characters are escaped in canonical JSON. Every vector
whose blocks contain non-ASCII text is therefore computed BOTH ways and labelled; that open
choice is the first interop question for -01.
"""
import hashlib
import json
import sys
from pathlib import Path

GENESIS_SEED = b"hctp-genesis-v1"


def sha(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def canonical(block: dict, ascii_escape: bool) -> bytes:
    # exactly four members, sorted by code point, "," and ":" only
    obj = {k: block[k] for k in ("content_hash", "role", "seq", "summary")}
    return json.dumps(obj, separators=(",", ":"), sort_keys=True,
                      ensure_ascii=ascii_escape).encode("utf-8")


def block(seq: int, role: str, raw: str, summary: str) -> dict:
    return {"seq": seq, "role": role, "summary": summary,
            "content_hash": hashlib.sha256(raw.encode("utf-8")).hexdigest(), "_raw": raw}


SEQUENCES = {
    "ascii-3": [
        block(0, "user", "Hello, agent.", "greeting"),
        block(1, "agent", "Hello. What do you need?", "greeting reply"),
        block(2, "user", "Summarise RFC 6234.", "asks for RFC 6234 summary"),
    ],
    "non-ascii-1": [
        block(0, "user", "Café, naïve, 東京", "café in Tōkyō"),
    ],
}


def roots(blocks, ascii_escape):
    r = sha(GENESIS_SEED)
    out = []
    for b in blocks:
        c = canonical(b, ascii_escape)
        r = sha(r + sha(c))
        out.append({"seq": b["seq"], "canonical": c.decode("utf-8"), "root": r.hex()})
    return out


def build():
    doc = {"genesis_root": sha(GENESIS_SEED).hex(), "sequences": {}}
    for name, blocks in SEQUENCES.items():
        inputs = [{"seq": b["seq"], "role": b["role"], "raw_text": b["_raw"],
                   "summary": b["summary"], "content_hash": b["content_hash"]} for b in blocks]
        entry = {"blocks": inputs, "ascii_escaped": roots(blocks, True)}
        if any(ord(ch) > 127 for b in blocks for ch in b["_raw"] + b["summary"] + b["role"]):
            entry["raw_utf8"] = roots(blocks, False)
        doc["sequences"][name] = entry
    return doc


def check(pkg_parent: str, doc: dict) -> int:
    sys.path.insert(0, pkg_parent)
    from velamen import hctp  # noqa: PLC0415
    bad = 0
    if hctp._genesis_root().hex() != doc["genesis_root"]:
        print("MISMATCH genesis"); bad += 1
    for name, entry in doc["sequences"].items():
        r = hctp._genesis_root()
        for inp, want in zip(entry["blocks"], entry["ascii_escaped"]):
            b = hctp.ContextBlock.from_text(inp["seq"], inp["role"], inp["raw_text"], inp["summary"])
            r = hctp._fold_block(r, b)
            ok = r.hex() == want["root"]
            bad += not ok
            print(f"{name} seq={inp['seq']} ref={'==' if ok else '!='} spec-text(ascii-escaped)")
        if "raw_utf8" in entry:
            same = entry["raw_utf8"][-1]["root"] == r.hex()
            print(f"{name}: reference {'MATCHES' if same else 'DIFFERS FROM'} raw-UTF-8 encoding")
    return bad


if __name__ == "__main__":
    doc = build()
    if len(sys.argv) == 3 and sys.argv[1] == "--check":
        sys.exit(1 if check(sys.argv[2], doc) else 0)
    out = Path(__file__).with_name("vectors-00.json")
    # bytes, so the file is LF on every platform and its digest is the same everywhere
    out.write_bytes((json.dumps(doc, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    print(f"wrote {out}")
