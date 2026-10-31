# Claims

Every capability that this repo's README and llms.txt state, mapped to the code that does it, where it is
mounted, and the test that proves it.

| id | claim | source | status | code | wired | test | note |
|---|---|---|---|---|---|---|---|
| C1 | imports no HCTP implementation | README.md | shipped | test-vectors/gen_vectors.py::build | test-vectors/gen_vectors.py: doc = build() | tests/test_vectors.py::test_generator_imports_no_hctp_implementation | the only import of velamen is inside check(), used by --check |
| C2 | the file is UTF-8 with LF line endings | README.md | shipped | test-vectors/gen_vectors.py::build | test-vectors/gen_vectors.py: out.write_bytes( | tests/test_vectors.py::test_committed_file_is_lf_only | |
| C3 | renders the XML source to the plain-text form, which is identical to the text published on the datatracker | README.md | shipped | tools/render_draft.py::render | tools/render_draft.py: ok, log = render( | tests/test_vectors.py::test_xml_renders_to_the_published_text | compared by SHA-256 with the -00 text |
| C4 | the non-ASCII vector is given under both readings | llms.txt | shipped | test-vectors/gen_vectors.py::build | test-vectors/gen_vectors.py: entry["raw_utf8"] = roots(blocks, False) | tests/test_vectors.py::test_non_ascii_readings_differ | |
| C5 | computes the vectors from sections 3.1 and 4 of the draft | llms.txt | shipped | test-vectors/gen_vectors.py::roots | test-vectors/gen_vectors.py: roots(blocks, True) | tests/test_vectors.py::test_roots_follow_from_the_inputs | the test re-derives every root without the generator |
