"""The vectors are what the draft text gives, the generator is independent of any implementation, and the
XML source renders to the published -00 text."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "test-vectors" / "gen_vectors.py"
VECTORS = ROOT / "test-vectors" / "vectors-00.json"
PUBLISHED_00_SHA256 = "c9e80197104083f5ec86faf4beddf66b398bb6cd4f15cd7ccd45d841b17f7ad5"  # the datatracker text


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def test_regenerating_gives_the_committed_file():
    g = load(GEN, "gen_vectors")
    text = json.dumps(g.build(), indent=2, ensure_ascii=False) + "\n"
    assert text.encode("utf-8") == VECTORS.read_bytes()


def test_committed_file_is_lf_only():
    assert b"\r\n" not in VECTORS.read_bytes()


def test_roots_follow_from_the_inputs():
    """Re-derive every root from section 4 here, without the generator."""
    v = json.loads(VECTORS.read_text(encoding="utf-8"))
    root0 = sha(b"hctp-genesis-v1")
    assert v["genesis_root"] == root0.hex()
    checked = 0
    for name, entry in v["sequences"].items():
        for variant, ensure_ascii in (("ascii_escaped", True), ("raw_utf8", False)):
            if variant not in entry:
                continue
            r = root0
            for blk, want in zip(entry["blocks"], entry[variant]):
                assert blk["content_hash"] == hashlib.sha256(blk["raw_text"].encode("utf-8")).hexdigest()
                obj = {k: blk[k] for k in ("content_hash", "role", "seq", "summary")}
                canon = json.dumps(obj, separators=(",", ":"), sort_keys=True, ensure_ascii=ensure_ascii)
                assert canon == want["canonical"], (name, variant, blk["seq"])
                r = sha(r + sha(canon.encode("utf-8")))
                assert r.hex() == want["root"], (name, variant, blk["seq"])
                checked += 1
    assert checked == 5   # 3 ASCII folds, and the non-ASCII block under both readings


def test_non_ascii_readings_differ():
    e = json.loads(VECTORS.read_text(encoding="utf-8"))["sequences"]["non-ascii-1"]
    assert e["ascii_escaped"][-1]["root"] != e["raw_utf8"][-1]["root"]


def test_generator_imports_no_hctp_implementation():
    """Only the --check path may import velamen, and only inside that function."""
    tree = ast.parse(GEN.read_text(encoding="utf-8"))
    top = set()
    for n in tree.body:
        if isinstance(n, ast.Import):
            top |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module:
            top.add(n.module.split(".")[0])
    assert top <= {"hashlib", "json", "sys", "pathlib"}, top


def test_xml_renders_to_the_published_text(tmp_path):
    rd = load(ROOT / "tools" / "render_draft.py", "render_draft")
    out = tmp_path / "draft-ruvalcaba-hctp-00.txt"
    ok, log = rd.render(str(ROOT / "draft-ruvalcaba-hctp-00.xml"), str(out))
    assert ok, log
    assert hashlib.sha256(out.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == PUBLISHED_00_SHA256
