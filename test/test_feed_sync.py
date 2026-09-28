#!/usr/bin/env python3
"""Exercise the 'Sync packaged update feed' step of action.yml offline.

This step is the one that shipped a bug: the module's 2026.09.28 release
contained a feed advertising the previous version, because the package was
assembled before the feed was rewritten. The rewrite was added afterwards, in
the working tree, so the packaged copy was current.

The step's shell is extracted from action.yml at run time rather than copied, so
these checks cannot drift from the real logic. It makes no network calls, so no
stubs are needed -- unlike the publish step, which is covered by
test_feed_publish.py.

One check here is specifically a drift guard: the sync step and the later
publish step each carry their own copy of the same sed rewrites. That
duplication is what allowed them to disagree in the first place, so the two
expressions are compared directly and must stay byte-identical.

Run: python test/test_feed_sync.py
"""

import os
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

EXT_NAME = "mod_test"
REPO = "N6REJ/joomla-packager"
NEW = "2026.9.28"
PREV = "2026.9.27"

EXPRESSIONS = {
    "inputs.updates-xml-file": "updates.xml",
    "steps.extension_details.outputs.extension_name": EXT_NAME,
    "steps.set_version.outputs.version": NEW,
    "github.repository": REPO,
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


def feed_xml(version, url):
    return textwrap.dedent("""\
        <?xml version="1.0" encoding="utf-8"?>
        <updates>
            <update>
                <name>%s</name>
                <element>%s</element>
                <type>module</type>
                <version>%s</version>
                <downloads>
                    <downloadurl type="full" format="zip">%s</downloadurl>
                </downloads>
            </update>
        </updates>
        """) % (EXT_NAME, EXT_NAME, version, url)


def url_for(version):
    return "https://github.com/%s/releases/download/%s/%s_%s.zip" % (
        REPO, version, EXT_NAME, version)


OLD_URL = url_for(PREV)
NEW_URL = url_for(NEW)


def case(seed):
    """Fresh directory, optionally seeded with a stale feed. Returns its path."""
    root = Path(tempfile.mkdtemp(prefix="feed-sync-"))
    if seed is not None:
        (root / "updates.xml").write_text(seed, encoding="utf-8", newline="\n")
    return root


def run(script, cwd):
    return subprocess.run(["bash", "-c", script], cwd=str(cwd),
                          capture_output=True, text=True)


def read_feed(root):
    """File contents, or a marker if the step deleted or never wrote it.

    Every check must report rather than raise: a step that removes the feed is
    itself a failure worth naming, not an exception to propagate.
    """
    path = root / "updates.xml"
    if not path.exists():
        return "<feed missing>"
    return path.read_text(encoding="utf-8")


def sed_lines(script):
    return [l.strip() for l in script.splitlines() if l.strip().startswith("sed -i")]


def main():
    if not shutil.which("bash"):
        sys.exit("bash is required")

    sync = load_step("Sync packaged update feed")
    publish = load_step("Publish Joomla update feed")
    print("extracted sync (%d lines) and publish (%d lines) from action.yml\n"
          % (len(sync.splitlines()), len(publish.splitlines())))

    # 1. A stale feed is rewritten before the package is built. This is the
    #    behaviour whose absence caused the shipped regression.
    d = case(feed_xml(PREV, OLD_URL))
    p = run(sync, d)
    body = read_feed(d)
    check("sync exits 0", p.returncode == 0, p.stdout + p.stderr)
    check("version rewritten to the new one", "<version>%s</version>" % NEW in body)
    check("stale version no longer present",
          "<version>%s</version>" % PREV not in body, body)
    check("download URL rewritten to the new release", NEW_URL in body)
    check("stale download URL no longer present", OLD_URL not in body, body)
    check("feed structure preserved",
          body.count("<updates>") == 1 and body.count("</update>") == 1
          and body.count("<downloads>") == 1, body)
    check("<element> untouched", "<element>%s</element>" % EXT_NAME in body)
    shutil.rmtree(d, ignore_errors=True)

    # 2. Running twice must not churn the file.
    d = case(feed_xml(PREV, OLD_URL))
    run(sync, d)
    once = read_feed(d)
    p2 = run(sync, d)
    twice = read_feed(d)
    check("second sync is a no-op", p2.returncode == 0 and twice == once,
          p2.stdout + p2.stderr)
    check("second sync says it already advertises the version",
          "already advertises" in p2.stdout, p2.stdout)
    shutil.rmtree(d, ignore_errors=True)

    # 3. A feed that is already current must be left byte-for-byte alone.
    d = case(feed_xml(NEW, NEW_URL))
    before = read_feed(d)
    run(sync, d)
    check("already-current feed is not rewritten", read_feed(d) == before, read_feed(d))
    shutil.rmtree(d, ignore_errors=True)

    # 4. With no feed in the repository, the step must not create one: creating
    #    it is the publish step's job, and it only happens once a release exists.
    d = case(None)
    p4 = run(sync, d)
    check("missing feed: exits 0", p4.returncode == 0, p4.stdout + p4.stderr)
    check("missing feed: no file created", not (d / "updates.xml").exists())
    shutil.rmtree(d, ignore_errors=True)

    # 5. Drift guard. The two steps carry separate copies of the same rewrites;
    #    when they disagree, the packaged feed and the published feed disagree.
    check("sync and publish use identical sed expressions",
          sed_lines(sync) == sed_lines(publish),
          "sync=%r\n           publish=%r" % (sed_lines(sync), sed_lines(publish)))

    # 6. Parity: applying only the publish step's rewrites to the same input
    #    must land on exactly the bytes the sync step produced.
    header = [l for l in publish.splitlines()
              if l.strip().startswith(("EXTENSION_NAME=", "UPDATES_XML=", "VERSION=",
                                       "DOWNLOAD_URL=", "ASSET_NAME="))]
    pub_rewrites = "\n".join(header + sed_lines(publish))
    check("publish rewrites are recoverable for comparison",
          len(sed_lines(publish)) == 2, publish)

    d_sync, d_pub = case(feed_xml(PREV, OLD_URL)), case(feed_xml(PREV, OLD_URL))
    run(sync, d_sync)
    p6 = run(pub_rewrites, d_pub)
    synced = read_feed(d_sync)
    published = read_feed(d_pub)
    check("publish rewrites run cleanly", p6.returncode == 0, p6.stdout + p6.stderr)
    check("sync and publish produce byte-identical output", synced == published,
          "sync=%r\n           publish=%r" % (synced[-200:], published[-200:]))
    shutil.rmtree(d_sync, ignore_errors=True)
    shutil.rmtree(d_pub, ignore_errors=True)

    passed = sum(1 for _, ok in RESULTS if ok)
    print("\n%d/%d checks passed" % (passed, len(RESULTS)))
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
