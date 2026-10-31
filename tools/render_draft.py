"""Render an xml2rfc v3 draft to text: python render_draft.py <in.xml> <out.txt>, or render(src, dst) from code.
Same stubs as ../render.py (weasyprint is broken on Windows and only the PDF writer needs it)."""
import contextlib
import io
import sys
import types

for name in ("weasyprint", "weasyprint.text", "weasyprint.text.ffi"):
    sys.modules.setdefault(name, types.ModuleType(name))
sys.modules["weasyprint.text.ffi"].pango = object()
sys.modules["weasyprint"].HTML = object
sys.modules["weasyprint"].default_url_fetcher = lambda *a, **k: None

import xml2rfc  # noqa: E402


def render(src: str, dst: str) -> tuple[bool, str]:
    """(ok, log). Captures xml2rfc's own output so a caller can keep it beside the draft."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            xmlrfc = xml2rfc.XmlRfcParser(src, quiet=False).parse()
            prep = xml2rfc.PrepToolWriter(xmlrfc, quiet=False, liberal=True, keep_pis=[])
            prep.options.accept_prepped = True
            xmlrfc.tree = prep.prep()
            if xmlrfc.tree is None:
                return False, buf.getvalue() + "PREP FAILED\n"
            xml2rfc.TextWriter(xmlrfc, quiet=False).write(dst)
    except Exception as e:  # noqa: BLE001 - any render failure is reported, never swallowed
        return False, buf.getvalue() + f"{type(e).__name__}: {e}\n"
    return True, buf.getvalue() + "TEXT RENDER OK\n"


if __name__ == "__main__":
    ok, log = render(sys.argv[1], sys.argv[2])
    print(log, end="")
    sys.exit(0 if ok else 1)
