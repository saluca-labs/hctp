# hctp

The Hash-Chain Context Transfer Protocol (HCTP) Internet-Draft, its test vectors, and the scripts that generate and check them, for anyone implementing or reviewing the protocol.

## Status

Maintained. This repository carries `draft-ruvalcaba-hctp-00`, the revision published on the IETF datatracker on 2026-08-11, and test vectors for it. A second, independent implementation built from the -00 text alone reported on the IETF dispatch list on 2026-10-31 that it reproduces every value in these vectors. A revision, -01, is in preparation and will be added here when it is posted to the datatracker.

HCTP carries acknowledged history between two endpoints as a single 32-octet rolling SHA-256 root and transmits only the blocks not yet acknowledged, so the per-message overhead attributable to history is constant. It defines payload octets only and relies on TLS or QUIC for confidentiality and peer authentication.

One point the -00 text leaves open: it does not say how non-ASCII characters are escaped in the canonical JSON of a block. The vectors therefore give the non-ASCII sequence under both readings, and name the one the reference implementation produces today.

## Install

Python 3.10 or later; tested with Python 3.12.10. The vector generator uses only the standard library. Rendering the draft and running the tests need xml2rfc and pytest (tested with xml2rfc 3.34.0):

```
pip install xml2rfc==3.34.0 pytest
python -m pytest tests
```

## Quickstart

Regenerate the test vectors from the specification text and confirm the file is the one in this repository:

```
$ python test-vectors/gen_vectors.py
wrote test-vectors/vectors-00.json
$ sha256sum test-vectors/vectors-00.json
e93d29441cd44175c27e00020a8ed5cae39c64d2c3782fb22729f14e553108c8  test-vectors/vectors-00.json
```

A different digest means the file was regenerated differently or its line endings were changed; the file is UTF-8 with LF line endings. An earlier copy of this file was distributed by email with CRLF line endings, and that copy's SHA-256 is `1e0c4edb8c420df061982782f5ac44268db7367c43471818b6b5f863a0e2d24d`; its content is identical.

## Usage

- `python test-vectors/gen_vectors.py` writes `test-vectors/vectors-00.json`: the genesis root, and for each block sequence the inputs, the canonical encoding of every block and the rolling root after every fold. It computes them from sections 3.1 and 4 of the draft and imports no HCTP implementation.
- `python test-vectors/gen_vectors.py --check <dir>` folds the same inputs with the reference implementation, `velamen.hctp`, found in `<dir>` (the directory that contains the `velamen` package), and reports each root as matching or not:

```
$ python test-vectors/gen_vectors.py --check path/to/velamen
ascii-3 seq=0 ref=== spec-text(ascii-escaped)
ascii-3 seq=1 ref=== spec-text(ascii-escaped)
ascii-3 seq=2 ref=== spec-text(ascii-escaped)
non-ascii-1 seq=0 ref=== spec-text(ascii-escaped)
non-ascii-1: reference DIFFERS FROM raw-UTF-8 encoding
```

- `python tools/render_draft.py draft-ruvalcaba-hctp-00.xml draft-ruvalcaba-hctp-00.txt` renders the XML source to the plain-text form, which is identical to the text published on the datatracker.

To test another implementation, fold the `blocks` of each sequence in `vectors-00.json` from `genesis_root` and compare every root.

## Architecture

| File | What it is |
|---|---|
| `draft-ruvalcaba-hctp-00.xml` | The draft's xml2rfc v3 source, the source of record; the rendered text is on the datatracker |
| `test-vectors/gen_vectors.py` | Computes the vectors from the draft text alone |
| `test-vectors/vectors-00.json` | The vectors: `genesis_root`, then per sequence the `blocks` and, for each block, `canonical` and `root` |
| `tools/render_draft.py` | Renders the XML with xml2rfc; it stubs weasyprint, which only the PDF writer needs |
| `tests/test_vectors.py` | Checks that the vectors regenerate byte for byte, that every root follows from the inputs, and that the XML renders to the published text |

The rolling root is `root_0 = SHA256("hctp-genesis-v1")` and `fold(R, B) = SHA256(R || SHA256(canonical(B)))`, where `canonical(B)` is the block's JSON with its four members `content_hash`, `role`, `seq` and `summary` in that order and no whitespace (draft section 3.1 and 4).

## Citation

No archived record yet. Cite the Internet-Draft as `draft-ruvalcaba-hctp`, https://datatracker.ietf.org/doc/draft-ruvalcaba-hctp/.

## License

Code and test vectors: Apache-2.0, see [LICENSE](LICENSE). The draft text is an IETF contribution, subject to BCP 78 and the IETF Trust's Legal Provisions as stated in the draft itself.

HCTP is royalty-free to implement. IPR disclosure 7533 (https://datatracker.ietf.org/ipr/7533/) commits to grant a royalty-free, reasonable and non-discriminatory license to all implementers, under any claims of the identified application that are or become essential to implementing the draft, solely for the purpose of implementing the specification.

## Links

- The draft on the IETF datatracker: https://datatracker.ietf.org/doc/draft-ruvalcaba-hctp/
- IPR disclosure 7533: https://datatracker.ietf.org/ipr/7533/
- Reference implementation (Python): https://github.com/saluca-labs/velamen
- Project page: https://hctp.saluca.com

_Last updated: 2026-10-31_
