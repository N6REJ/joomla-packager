#!/usr/bin/env python3
"""Exercise the 'Publish Joomla update feed' step of action.yml offline.

That step is the one the packager's own tests cannot reach: it is gated on
`create-release == 'true'`, and because the action packages the repository
root (`rsync -a ./ "$OUTER_BUILD_DIR/"`) running it in this repository would
publish a copy of the packager as a release asset. So the branch that rewrites
the feed a real Joomla site reads back has no CI coverage.

This harness sidesteps the gate instead of the network. The step's shell is
extracted from action.yml at run time -- never copied -- so it cannot drift from
the real thing, and its GitHub expressions are rewritten to read from the
environment. The two things it reaches out for, `gh` and `sleep`, are replaced
with bash function stubs prepended to the script. Functions rather than shims on
PATH: PATH ordering is not dependable for this (git-bash resolves `sleep` to
/usr/bin/sleep regardless of a shim placed ahead of it, and a shim's executable
bit cannot be set on NTFS), and a function needs neither.

Run: python test/test_feed_publish.py
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
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
STEP_NAME = "Publish Joomla update feed"
STEP_ID = "__run_publish_feed"

# Every ${{ ... }} the step is allowed to contain. An expression that is not
# listed here is a hard failure rather than a silent passthrough, so that a
# future edit to the step cannot quietly stop being exercised.
EXPRESSIONS = {
    "steps.extension_details.outputs.extension_name": "__EXT_NAME",
    "steps.extension_details.outputs.extension_type": "__EXT_TYPE",
    "steps.extension_details.outputs.extension_client": "__EXT_CLIENT",
    "inputs.updates-xml-file": "__FEED",
    "steps.set_version.outputs.version": "__VER",
    "inputs.targetplatform-name": "__TP_NAME",
    "inputs.targetplatform-version": "__TP_VERSION",
    "github.repository": "__REPO",
}

EXT_NAME = "mod_test"
EXT_TYPE = "module"
EXT_CLIENT = "site"
TP_NAME = "joomla"
TP_VERSION = "6.*"
VERSION = "2026.09.28"
REPO = "N6REJ/joomla-packager"
ASSET = "%s_%s.zip" % (EXT_NAME, VERSION)
FEED_RELPATH = "test-extensions/test-module/updates.xml"
EXPECTED_URL = "https://github.com/%s/releases/download/%s/%s" % (REPO, VERSION, ASSET)

# A feed from a previous release: stale version, stale URL, and a second
# <update> block so we can pin how the global sed treats unrelated entries.
STALE_FEED = """<?xml version="1.0" encoding="utf-8"?>
<updates>
    <update>
        <name>%s</name>
        <version>1.0.0</version>
        <downloads>
            <downloadurl type="full" format="zip">https://github.com/%s/releases/download/1.0.0/%s_1.0.0.zip</downloadurl>
        </downloads>
    </update>
    <update>
        <name>other</name>
        <version>2.0.0</version>
        <downloads>
            <downloadurl type="full" format="zip">https://example.com/other.zip</downloadurl>
        </downloads>
    </update>
</updates>
""" % (EXT_NAME, REPO, EXT_NAME)

# Prepended to the extracted script. Bash functions shadow external commands,
# so this intercepts `gh` and `sleep` regardless of PATH or file permissions.
STUB_PRELUDE = r"""
: > "$GH_LOG"
: > "$SLEEP_LOG"

gh() {
  echo "call" >> "$GH_LOG"
  count=$(wc -l < "$GH_LOG")
  case "$GH_MODE" in
    present) printf '%s\n' "$ASSET_NAME" ;;
    absent)  ;;
    flaky)
      # Fail the first $GH_FLAKY_AFTER calls, then succeed.
      if [ "$count" -gt "$GH_FLAKY_AFTER" ]; then printf '%s\n' "$ASSET_NAME"; fi
      ;;
  esac
  return 0
}

sleep() {
  # The real step sleeps 5s between attempts. Record it and move on, so the
  # exhausted-retry case does not take 45 real seconds.
  echo "slept" >> "$SLEEP_LOG"
  return 0
}
"""


def load_yaml():
    try:
        return yaml.safe_load(ACTION_YML.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        sys.exit("%s is not valid YAML, so no step can be tested:\n%s"
                 % (ACTION_YML, exc))


def load_step():
    """Pull the step's shell out of action.yml, and make it env-driven."""
    doc = load_yaml()
    steps = doc["runs"]["steps"]
    matches = [s for s in steps if s.get("name") == STEP_NAME]
    if len(matches) != 1:
        sys.exit("expected exactly one %r step, found %d" % (STEP_NAME, len(matches)))
    script = matches[0]["run"]

    unknown = []

    def sub(m):
        expr = m.group(1).strip()
        if expr not in EXPRESSIONS:
            unknown.append(expr)
            return m.group(0)
        return "${%s}" % EXPRESSIONS[expr]

    script = re.sub(r"\$\{\{(.*?)\}\}", sub, script)
    if unknown:
        sys.exit("step contains expressions this harness does not model: %s" % unknown)
    return script


def run_step(script, feed, mode, flaky_after=0, seed=None):
    """Run the extracted step in a throwaway tree. Returns (proc, feed_path)."""
    root = Path(tempfile.mkdtemp(prefix="feed-publish-"))
    feed_path = root / feed
    feed_path.parent.mkdir(parents=True, exist_ok=True)
    if seed is not None:
        feed_path.write_text(seed, encoding="utf-8", newline="\n")

    env = dict(os.environ)
    env.update(
        __EXT_NAME=EXT_NAME,
        __EXT_TYPE=EXT_TYPE,
        __EXT_CLIENT=EXT_CLIENT,
        __FEED=feed,
        __VER=VERSION,
        __TP_NAME=TP_NAME,
        __TP_VERSION=TP_VERSION,
        __REPO=REPO,
        GH_MODE=mode,
        GH_LOG=str(root / "gh.log"),
        GH_FLAKY_AFTER=str(flaky_after),
        SLEEP_LOG=str(root / "sleep.log"),
        ASSET_NAME=ASSET,
        GITHUB_TOKEN="offline",
    )

    proc = subprocess.run(
        ["bash", "-c", STUB_PRELUDE + "\n" + script],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
    )
    proc.sh_root = str(root)
    proc.sh_feed = feed_path
    return proc


def feed_values(path):
    """Return (version, downloadurl, element) from the first <update> block.

    A feed that is not well-formed XML is the failure this most needs to report,
    so a parse error becomes a marker in the version slot rather than an
    exception: the surrounding check then fails with the parser's own message.
    """
    try:
        root = ET.parse(str(path)).getroot()
    except (ET.ParseError, OSError) as exc:
        return ("<not well-formed: %s>" % exc, None, None)
    update = root.find("update")
    if update is None:
        return "<no <update> block>", None, None
    element = update.findtext("element")
    url = update.find("downloads/downloadurl")
    return update.findtext("version"), (url.text if url is not None else None), element


def feed_identity(path):
    """Return (type, client, targetplatform_name, targetplatform_version).

    These are the fields an installed site matches the feed entry against. A
    generated feed that omits them is the bug this harness exists to catch, so
    a parse failure degrades to None rather than raising.
    """
    try:
        update = ET.parse(str(path)).getroot().find("update")
    except (ET.ParseError, OSError):
        return (None, None, None, None)
    if update is None:
        return (None, None, None, None)
    tp = update.find("targetplatform")
    return (
        update.findtext("type"),
        update.findtext("client"),
        (tp.get("name") if tp is not None else None),
        (tp.get("version") if tp is not None else None),
    )


def calls(proc):
    text = (Path(proc.sh_root) / "gh.log").read_text(encoding="utf-8")
    return len([l for l in text.splitlines() if l.strip()])


def sleeps(proc):
    text = (Path(proc.sh_root) / "sleep.log").read_text(encoding="utf-8")
    return len([l for l in text.splitlines() if l.strip()])


RESULTS = []


def check(label, condition, detail=""):
    RESULTS.append((label, bool(condition), detail))
    print("%-4s %s%s" % ("OK" if condition else "FAIL", label,
                         "" if condition else "  <- " + str(detail)))


def main():
    if not shutil.which("bash"):
        sys.exit("bash is required")

    script = load_step()
    print("extracted %d lines from %r\n" % (len(script.splitlines()), STEP_NAME))

    # 1. Feed absent: the step must create a valid, minimal feed.
    p = run_step(script, FEED_RELPATH, "present")
    ok = p.returncode == 0 and p.sh_feed.is_file()
    check("creates a feed when none exists", ok, p.stdout + p.stderr)
    if ok:
        v, url, element = feed_values(p.sh_feed)
        check("created feed is well-formed XML with the right version",
              v == VERSION, "got %r" % v)
        check("created feed advertises the release download URL",
              url == EXPECTED_URL, "got %r" % url)
        check("created feed names the extension element",
              element == EXT_NAME, "got %r" % element)
        typ, client, tpname, tpver = feed_identity(p.sh_feed)
        check("created feed carries the extension type",
              typ == EXT_TYPE, "got %r" % typ)
        check("created feed carries the site client",
              client == EXT_CLIENT, "got %r" % client)
        check("created feed carries the targetplatform",
              (tpname, tpver) == (TP_NAME, TP_VERSION),
              "got name=%r version=%r" % (tpname, tpver))
        check("created feed verifies the asset before writing",
              calls(p) == 1, "gh called %d times" % calls(p))
    shutil.rmtree(Path(p.sh_root), ignore_errors=True)

    # 2. Feed present but stale: version and URL must be rewritten.
    p = run_step(script, FEED_RELPATH, "present", seed=STALE_FEED)
    ok = p.returncode == 0
    check("succeeds against an existing stale feed", ok, p.stdout + p.stderr)
    if ok:
        v, url, _ = feed_values(p.sh_feed)
        check("stale feed version is rewritten", v == VERSION, "got %r" % v)
        check("stale feed URL is rewritten", url == EXPECTED_URL, "got %r" % url)
        # The sed expressions are global, so every <version> in the file moves.
        # Pinned here deliberately: a feed in an extension repository is
        # single-extension, and changing this is a behaviour change, not a fix.
        text = p.sh_feed.read_text(encoding="utf-8")
        check("documents global <version> replacement (see comment)",
              text.count("<version>%s</version>" % VERSION) == 2, text)
    shutil.rmtree(Path(p.sh_root), ignore_errors=True)

    # 3. The 404 guard: no matching asset must fail and leave the feed alone.
    p = run_step(script, FEED_RELPATH, "absent", seed=STALE_FEED)
    check("fails when the release asset is missing", p.returncode != 0,
          "rc=%d" % p.returncode)
    check("failure names the missing asset",
          ASSET in p.stdout + p.stderr, p.stdout[-300:])
    check("failure states the feed was NOT published",
          "update feed NOT published" in p.stdout + p.stderr, p.stdout[-300:])
    check("guard retries the full 10 attempts", calls(p) == 10,
          "gh called %d times" % calls(p))
    check("guard sleeps between attempts", sleeps(p) == 9,
          "slept %d times" % sleeps(p))
    # Deleting the feed counts as a failure too, and must report as one rather
    # than raising: removing it is worse than leaving it stale.
    actual = (p.sh_feed.read_text(encoding="utf-8")
              if p.sh_feed.exists() else "<file deleted>")
    check("feed is left untouched when the asset is missing", actual == STALE_FEED,
          actual[:200])

    # 4. The feed must not be advertised at all if the asset never appears:
    #    with no pre-existing feed, nothing may be written.
    p = run_step(script, FEED_RELPATH, "absent", seed=None)
    check("no feed is created when the asset is missing",
          not p.sh_feed.exists() and p.returncode != 0,
          "rc=%d exists=%s" % (p.returncode, p.sh_feed.exists()))
    shutil.rmtree(Path(p.sh_root), ignore_errors=True)

    # 5. Retry loop recovers: a late-appearing asset must still publish.
    p = run_step(script, FEED_RELPATH, "flaky", flaky_after=3, seed=None)
    check("recovers when the asset appears on a later attempt",
          p.returncode == 0, p.stdout[-300:] + p.stderr[-300:])
    if p.returncode == 0:
        v, url, _ = feed_values(p.sh_feed)
        check("recovered run still writes a correct feed",
              v == VERSION and url == EXPECTED_URL, "%r / %r" % (v, url))
        check("recovered after retrying, not on the first try",
              calls(p) == 4, "gh called %d times" % calls(p))
    shutil.rmtree(Path(p.sh_root), ignore_errors=True)

    passed = sum(1 for _, ok, _ in RESULTS if ok)
    print("\n%d/%d checks passed" % (passed, len(RESULTS)))
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
