#!/usr/bin/env python3
"""Exercise the 'Ensure Joomla update feed fields' step of action.yml offline.

An update feed is matched against an installed extension by element + type +
client_id + folder, and the whole <update> block is discarded before that if it
has no <targetplatform> whose version regex matches the running Joomla. The
generated fallback feed used to omit <targetplatform> and <client> and write an
empty <type />, which meant the release was never offered.

The new step fills those fields in, but must not clobber a value an extension
declared for itself -- a feed pinned to Joomla 4 must stay pinned to Joomla 4.
These checks pin both halves of that behaviour, plus idempotency.

The step's shell is extracted from action.yml at run time rather than copied, so
the checks cannot drift from the real logic. It makes no network calls.

Run: python test/test_feed_fields.py
"""

import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: python -m pip install pyyaml")

ACTION_YML = (
    Path(sys.argv[1])
    if len(sys.argv) > 1
    else Path(__file__).resolve().parent.parent / "action.yml"
)

STEP_NAME = "Ensure Joomla update feed fields"
EXT_NAME = "mod_test"

EXPRESSIONS = {
    "inputs.updates-xml-file": "updates.xml",
    "steps.extension_details.outputs.extension_type": "module",
    "steps.extension_details.outputs.extension_client": "site",
    "inputs.targetplatform-name": "joomla",
    "inputs.targetplatform-version": "6.*",
}

RESULTS = []


def check(label, condition, detail=""):
    RESULTS.append((label, bool(condition)))
    print("%-4s %s%s" % ("OK" if condition else "FAIL", label,
                         "" if condition else "  <- " + str(detail)[:300]))


def load_yaml():
    try:
        return yaml.safe_load(ACTION_YML.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        sys.exit("%s is not valid YAML, so no step can be tested:\n%s"
                 % (ACTION_YML, exc))


def load_step(name):
    doc = load_yaml()
    steps = doc["runs"]["steps"]
    matches = [s for s in steps if s.get("name") == name]
    if len(matches) != 1:
        sys.exit("expected exactly one %r step, found %d" % (name, len(matches)))
    script = matches[0]["run"]
    unknown = []

    def sub(m):
        expr = m.group(1).strip()
        if expr not in EXPRESSIONS:
            unknown.append(expr)
            return m.group(0)
        return EXPRESSIONS[expr]

    script = re.sub(r"\$\{\{(.*?)\}\}", sub, script)
    if unknown:
        sys.exit("step %r contains expressions this harness does not model: %s"
                 % (name, unknown))
    return script


def legacy_feed():
    """The shape the old fallback produced: empty <type />, no client, no targetplatform."""
    return textwrap.dedent("""\
        <?xml version="1.0" encoding="utf-8"?>
        <updates>
            <update>
                <name>%s</name>
                <description />
                <element>%s</element>
                <type />
                <version>2026.09.28</version>
                <infourl />
                <downloads>
                    <downloadurl type="full" format="zip">https://example.com/%s.zip</downloadurl>
                </downloads>
            </update>
        </updates>
        """) % (EXT_NAME, EXT_NAME, EXT_NAME)


def complete_feed(version):
    """A feed that already declares everything, pinned to Joomla 4."""
    return textwrap.dedent("""\
        <?xml version="1.0" encoding="utf-8"?>
        <updates>
            <update>
                <name>%s</name>
                <element>%s</element>
                <type>module</type>
                <client>site</client>
                <version>%s</version>
                <downloads>
                    <downloadurl type="full" format="zip">https://example.com/%s-%s.zip</downloadurl>
                </downloads>
                <targetplatform name="joomla" version="4.*" />
            </update>
        </updates>
        """) % (EXT_NAME, EXT_NAME, version, EXT_NAME, version)


def two_block_feed():
    return textwrap.dedent("""\
        <?xml version="1.0" encoding="utf-8"?>
        <updates>
            <update>
                <name>%s</name>
                <element>%s</element>
                <type />
                <version>1.0.0</version>
            </update>
            <update>
                <name>other</name>
                <element>other</element>
                <type />
                <version>2.0.0</version>
            </update>
        </updates>
        """) % (EXT_NAME, EXT_NAME)


def case(seed):
    root = Path(tempfile.mkdtemp(prefix="feed-fields-"))
    if seed is not None:
        (root / "updates.xml").write_text(seed, encoding="utf-8", newline="\n")
    return root


def run(script, cwd):
    return subprocess.run(["bash", "-c", script], cwd=str(cwd),
                          capture_output=True, text=True)


def read_feed(root):
    path = root / "updates.xml"
    if not path.exists():
        return "<feed missing>"
    return path.read_text(encoding="utf-8")


def main():
    if not shutil.which("bash"):
        sys.exit("bash is required")

    script = load_step(STEP_NAME)
    print("extracted %d lines from %r\n" % (len(script.splitlines()), STEP_NAME))

    # 1. The legacy fallback shape gains every field Joomla matches on, and its
    #    other content (version, download URL) is left alone.
    d = case(legacy_feed())
    p = run(script, d)
    body = read_feed(d)
    check("fills a legacy feed and exits 0", p.returncode == 0, p.stdout + p.stderr)
    check("empty <type /> is filled", "<type>module</type>" in body, body)
    check("no empty <type /> remains", "<type />" not in body, body)
    check("<client>site</client> is added", "<client>site</client>" in body, body)
    check("targetplatform is added",
          '<targetplatform name="joomla" version="6.*" />' in body, body)
    check("version is preserved", "<version>2026.09.28</version>" in body, body)
    check("download URL is preserved", "https://example.com/%s.zip" % EXT_NAME in body, body)
    shutil.rmtree(d, ignore_errors=True)

    # 2. A complete feed must be left byte-for-byte alone: the Joomla 4 pin an
    #    extension declared for itself must survive a packager default of 6.*.
    d = case(complete_feed("2026.09.28"))
    before = read_feed(d)
    p = run(script, d)
    check("complete feed is untouched", read_feed(d) == before, read_feed(d))
    check("complete feed reports nothing to fill",
          "already carries" in p.stdout, p.stdout)
    shutil.rmtree(d, ignore_errors=True)

    # 3. Running twice must not churn the file.
    d = case(legacy_feed())
    run(script, d)
    once = read_feed(d)
    p3 = run(script, d)
    check("second run is a no-op", p3.returncode == 0 and read_feed(d) == once,
          p3.stdout + p3.stderr)
    shutil.rmtree(d, ignore_errors=True)

    # 4. With no feed present the step must not create one; that is the publish
    #    step's job, and it only happens once a release exists.
    d = case(None)
    p4 = run(script, d)
    check("missing feed: exits 0", p4.returncode == 0, p4.stdout + p4.stderr)
    check("missing feed: no file created", not (d / "updates.xml").exists())
    shutil.rmtree(d, ignore_errors=True)

    # 5. An empty <type></type> is the same defect as <type />.
    d = case(legacy_feed().replace("<type />", "<type></type>"))
    run(script, d)
    body = read_feed(d)
    check("empty <type></type> is filled", "<type>module</type>" in body, body)
    check("no empty <type></type> remains", "<type></type>" not in body, body)
    shutil.rmtree(d, ignore_errors=True)

    # 6. Every <update> block gains the fields, not just the first.
    d = case(two_block_feed())
    run(script, d)
    body = read_feed(d)
    check("both blocks gain a client", body.count("<client>site</client>") == 2, body)
    check("both blocks gain a targetplatform",
          body.count('<targetplatform name="joomla" version="6.*" />') == 2, body)
    shutil.rmtree(d, ignore_errors=True)

    passed = sum(1 for _, ok in RESULTS if ok)
    print("\n%d/%d checks passed" % (passed, len(RESULTS)))
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
