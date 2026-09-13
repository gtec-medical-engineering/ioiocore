# Internal changelog

The engineering record: every change with the reasoning behind it, the
measurement that settled it, and the failure mode it removes. It is
written for whoever has to touch the same code next, not for a user.

Its counterpart is the root `CHANGELOG.md`, which is **public**, and
published three times over on every release. The release job copies it
verbatim into the public mirror (`.github/workflows/deploy.yml:264`);
the doc job appends it to `README.md` before Sphinx builds the manual
(`:137-142`), and that build is pushed to the mirror's GitHub Pages
(`:242-249`). It also drives the release itself:
`sessions/utilities/changelog_parser.extract_latest_version` reads the
version out of it, and both the build job and the release job state
that version rather than deriving it from a tag (`:87-95`, `:188-196`).

This file never leaves the development repository. `setuptools_scm` puts
every tracked file in the sdist, so `prune devdoc` in `MANIFEST.in` is
the only thing keeping it out -- which is why
`test/test_devdoc_readme_is_current.py` asserts that line exists rather
than trusting it. `doc/` is the published manual and is a different
document set for a different reader.

## What goes where

One change, two entries:

* **Public** -- what a user observes: the behaviour that changed, the
  API that moved, what they have to do about it. A bold lead sentence
  and, where it helps a user decide what to do, a short paragraph
  saying why. This repository's public entries carry more than g.Pype's
  one-liners do, and deliberately: `ioiocore` is a framework people
  build on, so "a callable rather than a node" is something its reader
  needs and its reader is a developer.
* **Internal** -- everything else: what was measured, which alternative
  was rejected, what the failure mode was, and what would break if the
  change were undone. Anything naming a commit, a workflow, a file
  path, or a mistake, belongs here.

Write the internal entry first; the public one falls out of it.

A change with no user-visible effect -- a build change, a test, a
refactor -- gets an internal entry and no public one. The reverse never
happens: nothing may be announced publicly that is not recorded here.

The line between them is *audience*, not length. A release-pipeline fix
is internal-only; the same fix is public the moment it changes what a
user can install, which is exactly what happened on 2026-09-13.

## Version headings must agree

Both files carry the same version and the same date for the same
release. The heading *levels* differ on purpose: the public file opens
with `## Changelog` and lists releases as `### [X.Y.Z] - YYYY-MM-DD`,
because the release chain appends it under a heading in `README.md`.
This file has no such constraint.

What must match is the version and the date, and that is **enforced**
rather than asked for: `nox -s check` refuses to release unless
`CHANGELOG.md` carries an entry dated today, and unless
`check_changelogs_in_sync` finds both files naming the same version on
the same date. The release chain derives the published version from the
public file, so a private record filed under a version that does not
exist is worse than no record at all -- it reads as the account of a
release that never happened, and it is found only by somebody looking
for something else.

The check was ported from g.Pype on 2026-09-13, the day this file was
created. Until then ioiocore had no internal changelog for it to check,
and the two could have drifted from the moment this one existed.

---

## [5.0.0] - 2026-09-14

### The cycle-0 gate could shut a window nothing reopened, 2026-09-13

A node whose inputs are all `ASYNC` could sleep for ever with a full
queue. Found by cutting a candidate: two builds failed, on
`macos-14/3.14` and then `ubuntu-24.04/3.11`, both on
`test_regression_async_node_drains_its_queue`, both reporting **0**
cycles where 8 were expected.

**Zero, rather than a partial drain, is what identified it.** A slow
runner would have given some other number; zero meant the node never ran
at all, which is the cycle-0 context gate never opening.

`ONodeImp._push_context` hands a context to a consumer that has none --
that is the half added with the gate, so a producer with nothing to say
still opens its consumer's first cycle. But `IPortImp.put` is the *only*
thing that wakes a node, and `_push_context` did not call it. So the
ordering that fails is: consumer wakes on each of the eight pushes, gate
still shut because the silent sibling has not set up; eighth push
delivered; no events remain; the sibling's context arrives a moment
later and nothing looks at the queue again.

It self-heals when more data follows, which is why it stalls for good
only where every input is `ASYNC` and the burst ends -- and why it
survived rc1 through rc5 and two years of green Windows runs.

**Measured, not inferred.** Driven outside pytest, where it reproduces
far more readily than under it: 8 pushes gave `[0, 0, 8, 0, 8, 0, 0, 8]`
across eight runs before the change and `[8] * 12` after. The first
diagnosis attempt used a subclass defined in `__main__` and stalled in
its own control arm, which proved nothing; the control with the suite's
own classes is what made the result usable.

Four lines: wake the consumer whose context was just set. Safe on both
execution paths, and stated in the comment rather than left to be
rediscovered -- the thread path sets an `Event`, which persists if the
consumer has not started yet, and the direct path returns at once unless
`_running`, with `start()` draining the queue itself. Recorded as
`D-NODE-10`.

### A bare `nox` was a release, 2026-09-13

`noxfile.py` set `reuse_existing_virtualenvs` and nothing else. nox
marks **every** defined session as selected unless
`nox.options.sessions` says otherwise, and runs them alphabetically --
so `nox`, typed with no arguments, ran `commit` (which pushes, and
writes `git config --global user.name/user.email`, rewriting the
machine-wide git identity for every repository on the machine),
`tag_create`, `tag_create_rc` and `tag_remove`, which deletes a
published tag from origin.

No typo and no flag: the most natural thing anyone can type. The same
default was found and removed in gpype-host-dev, and the note from that
day flagged this repository and gpype-dev as probably sharing it. Both
did.

`nox.options.sessions = ["lint", "test"]`, and an **allowlist** rather
than a denylist deliberately: a session added later is excluded until
somebody names it, so the guard's own omissions fail safe. A denylist
would have to be updated by whoever adds the dangerous session, which
is exactly the person who will forget. Asserted by
`test/test_nox_default_sessions.py`, which parses the noxfile rather
than importing it -- importing pulls in every session module, which is
a lot of surface for a test whose subject is not running them.

### Linux wheels ship stripped, and it is checked, 2026-09-13

Measured on the published `5.0.0rc5` manylinux wheel, with
`scripts/check_no_debug_info.py` written for the purpose: **all 17**
extension modules carried DWARF. `i_node_imp` was 1,400,109 bytes of
debug information in a 1,604,872-byte file, 87.2%; `logging_imp`
1,859,532 of 2,117,672. The Windows build of `i_node_imp` was 135,680
bytes and carried none, so this is incremental disclosure rather than
the same information in a different container.

DWARF carries no statements -- the byte-exact source audit of those same
wheels returned zero hits on every platform -- but it carries every
local variable name, every type layout, the build-machine source paths
and a complete line table, for the modules compiled precisely so that
none of that is readable.

`auditwheel repair --strip` in `[tool.cibuildwheel.linux]`, rather than
`CFLAGS=-g0`: it strips whatever was generated instead of depending on
setuptools honouring a compiler flag it also sets itself. The flag is
not trusted either -- `scripts/check_no_debug_info.py` runs over the
result in both workflows, because a build setting that silently stops
taking effect is the failure this repository has already had once, in
`deploy.yml`. The checker parses ELF section headers with the standard
library and was validated against the unstripped rc5 wheel before being
wired in, so it is known to fail on the bad case rather than assumed to.

Not covered: the macOS wheels, which are Mach-O and embed build-host
temp paths rather than DWARF. Lesser again, and it needs a different
mechanism than `auditwheel`.

### The release builds every wheel it declares, 2026-09-13

`deploy.yml` published **8** wheels: `windows-latest` and `macos-14`,
3.10 to 3.13. `[tool.ioiocore] python_versions` declares 3.10 to
**3.14**, the classifiers say the same, `make-prerelease.yml` builds
manylinux through cibuildwheel, and `scripts/ci_matrix.py --wheel-count`
says a complete set is **15**. So two whole platforms of the candidate
that gets audited were never in a release, and 3.14 was declared,
tested by nox and built for every candidate while no released wheel
existed for it.

Linux was the worse half. There is no sdist on PyPI either -- the
release uploads `tmp_whl/*`, filled by a loop that copies `*.whl` only
-- so `pip install ioiocore` on Linux resolved nothing at all. The
manual has promised Linux support by classifier since 4.0.5.

**The matrix is now derived, not repeated.** `scripts/ci_matrix.py`
existed for exactly this and said so in its own module docstring:
"`deploy.yml` does not read it; it carries its own copy, so a Python
version added to `pyproject.toml` was tested by nox and silently not
built by CI." A new `plan` job runs it and publishes `pythons`,
`build-os`, `test-os`, `cibw-build` and `wheel-count`; every job below
reads those. The same job resolves the version once, from CHANGELOG.md,
where it used to be computed twice by two copies of the same script --
once in `build` and once in `release`.

**A `build-linux` job mirrors the candidate's**, deliberately step for
step: stage, build the sdist, run cibuildwheel over *that sdist* rather
than the working tree, import the result in the container it was built
for, and gate it with `check_wheel`. Building both the release and the
candidate the same way is the point; it is what makes the audit of a
candidate say anything about the release.

**And the release now refuses to publish an incomplete set.** A build
cell that fails to upload leaves a gap that is invisible on a release
page and on PyPI -- the version simply has no wheel for that
interpreter, and the first report is a customer who cannot install.
The count is asserted against `ci_matrix.py`, never a literal, so
adding a platform cannot leave the gate checking the old number.

`SETUPTOOLS_SCM_PRETEND_VERSION` is now scoped
`_FOR_IOIOCORE`. `sessions/build.py` records the unscoped form having
already cost one debugging session, where it stamped a *dependency*
built from source with this package's version.

Not fixed here, and still open in
[release-path-hardening](workpackages/release-path-hardening.md): the
Linux wheels ship unstripped, roughly 87% DWARF debug info.

### This documentation set exists, 2026-09-13

`devdoc/` was created today. Before it, the repository had `doc/` -- the
published Sphinx manual, written for a user -- and nothing written for a
maintainer. The reasoning behind the engine lived in source comments,
which is where most of it was recovered from: the 51 entries in
[decisions.md](decisions.md) are archaeology, not invention, and each
one cites the file it came from. Where a source records no date, the
entry says the date is the date of recovery rather than of the decision.

Two consequences worth stating. **The set is derived where it can be**:
[README.md](README.md) is generated from the workpackages'
front-matter by `scripts/generate_devdoc_readme.py`, so a status is
written in exactly one place, and `test/test_devdoc_readme_is_current.py`
fails if the committed index drifts. **And it must never ship**: the same
test asserts `prune devdoc` is in `MANIFEST.in`, because `setuptools_scm`
puts every tracked file in the sdist and that line is the only thing
standing between this directory and a release -- the lesson the entry
below was learned from.

Four work packages opened, none of them invented for the occasion: every
one is a contradiction the documents ran into and could not leave
unresolved, since an open question is either something to fix or
something to accept, and never a third thing.

### The release path shipped the source it was supposed to compile, 2026-09-13

`.github/workflows/deploy.yml` is the path that publishes: it triggers
on a push to `main` whose commit message says so, states the version
from `CHANGELOG.md`, and pushes to PyPI and to the public mirror. Until
today it built with a bare `python -m build` and no staging step.

**What that produces.** `setup.py` declares an `Extension` only for a
module whose `.pyx` already exists (`setup.py:27-40`), and no `.pyx` is
tracked -- `git ls-files '*.pyx'` returns nothing. So the existence
test failed for each of the 17 entries in `[tool.ioiocore]
cython_files`, `ext_modules` came out empty, and the build yielded a
pure-Python wheel carrying every `src/ioiocore/imp/*.py` as readable
source. The job then extracts each wheel into the public mirror's
`ioiocore/` tree (`deploy.yml:265-276`), commits and tags it
(`:289-299`), and uploads to PyPI (`:312-315`). Both are one-way. The
whole point of the `.py`/`.pyx` split is that `imp/` is the
implementation and does not ship as source; this path undid it
silently, and produced a wheel that installs and imports correctly, so
nothing downstream would have complained.

**Why the step was missing.** Staging used to live inside `setup.py`
itself, as a rename-in-place with an `atexit` restore -- the
`CythonRename` class, visible in `git show f9c3abe^:setup.py`. Commit
f9c3abe (2026-08-26, "Build and release ioiocore the way g.Pype does")
moved it to `sessions/build.py` and
`sessions/utilities/stage_cython.py`, so every path through nox kept
it. `make-prerelease.yml`, written afterwards, calls it explicitly
(`:280-289`). `deploy.yml` does not go through nox and was never given
the step in its place. It was broken from 2026-08-26 until today.

**Nothing was ever published that way.** Checked on the artifacts, not
on the calendar. In the release-branch clone
`D:/10_git/ioiocore-dev-release`, the 4.0.5, 4.0.6 and 4.0.7 `dist/`
sets contain no `py3-none-any` wheel at all; each sampled wheel carries
12 extension modules under `imp/` and exactly one `.py`
(`__init__.py`). The public mirror clone `D:/10_git/ioiocore` has the
same shape -- `ioiocore/imp/` is `__init__.py` plus `.pyd`/`.so`. The
dates agree with that: the last release cut through `deploy.yml` is
v4.0.7 (2026-02-20), and everything since -- v5.0.0rc1 to v5.0.0rc5,
2026-08-31 to 2026-09-07 -- came through `make-prerelease.yml`, which
stages and gates. The window was eighteen days wide and empty.

**The fix, and why the gate now runs twice.** `deploy.yml` gained the
staging step (`:97-107`) and two `check_wheel` invocations: over
`dist/` in each build cell (`:113-121`), and over `tmp_whl/`
immediately before the two irreversible steps (`:278-287`). The second
is not redundant. `tmp_whl/` is assembled by a batch loop that copies
wheels out of every downloaded artifact (`:265-270`); it is a set no
single build cell ever saw, and it is the set that is actually
published. Before today `check_wheel` ran only in
`make-prerelease.yml` -- that is, only on the path that publishes
nothing permanent.

**`MANIFEST.in`, measured at both ends.** The published
`ioiocore-5.0.0rc5.tar.gz` has **129 members, 116 of them files**. It
carried `sessions/` (17 entries), `scripts/` (10), `.github/` with both
CI workflows (4), `.vscode/` (3), `CLAUDE.md`, `noxfile.py`,
`make.bat`, all four `requirements-*.txt`, `.coveragerc`, `.flake8` and
`.gitignore` -- the release topology, the secret names, the committer
address and the agent instructions, in an archive anyone can download.
An sdist built today lists **85 members, 78 files**: `src/`, `doc/`, and
eight root files plus what the build writes. Measured in a clean clone at
`b398091`, and identical whether or not the modules are staged first --
`include src/ioiocore/imp/*.pyx` matches the staged copies exactly as the
package's own `.py` would have been counted.

What stays is deliberate. The sdist is not a convenience artifact here
-- the manylinux wheels are built *from it*
(`make-prerelease.yml:291-338`) -- so only files the build genuinely
does not read are pruned; `setup.py` needs `pyproject.toml` and the
staged `.pyx`, and imports nothing from `sessions/` or `scripts/`
(`MANIFEST.in:7-16`). That is also why `src/ioiocore/imp/` in the rc5
archive is 17 `.pyx` and a single `.py`: the staged source of every
compiled module is in the sdist on purpose, because the Linux build
needs it. Which is a separate exposure, and the reason the upload
globs in `deploy.yml` matter -- see the workpackage.

**Validated.** A wheel built from the pruned sdist
(`ioiocore-5.0.0rc5-cp313-cp313-win_amd64.whl`) carries 17 extension
modules and one `.py` under `imp/`, and passes `python -m
sessions.utilities.check_wheel`. The pruning does not remove anything
the build reads.

**The audit that made this worth doing.** All 15 published 5.0.0rc5
wheels were checked for recoverable source before the release was cut:
for every compiled module, each non-docstring source line of at least
20 characters was tested for byte-exact presence in its own binary --
**zero hits**, on Windows, Linux and macOS separately. Reproduced here
on two modules of the cp313 manylinux wheel, excluding string-literal
lines by tokenising rather than by eye: `i_node_imp`, 126 code lines
and 59 comment lines, 0 hits; `node_imp`, 116 and 82, 0 hits. The compiled
artifacts are clean. It was the paths around them that were not.

**What a compiled module does still give away**, which the audit result
should never be read without:

* **Docstrings survive verbatim**, because they are `__doc__`. 26 of
  `i_node_imp`'s docstring lines are byte-exact in the `.so`. That is
  by design and is the same text the manual publishes.
* **The Linux wheels ship unstripped.**
  `i_node_imp.cpython-313-x86_64-linux-gnu.so` is 1,604,872 bytes, of
  which the `.debug_*` sections are 1,397,756 -- 87.1%. `node_imp` is
  979,584 of 1,131,800, 86.6%. For comparison `i_node_imp` is 135,680
  bytes as a Windows `.pyd` and 380,792 bytes in the macOS
  universal2 wheel, which holds two architecture slices. DWARF does not
  carry statements, which is why the byte-exact test comes back clean,
  but it carries every local name, every type layout, the source file
  paths and a full line table. That is a real if lesser exposure, and it
  exists only on the platform whose wheels are newest. **Fixed later the
  same day** with `auditwheel repair --strip` and a checker that asserts
  the result -- see the entry above and D-BUILD-13.

### The record starts partway through this release, 2026-09-13

`devdoc/` was created on 2026-09-13, while 5.0.0 was still unreleased
and most of its public entry already written. Everything above this line
is the record kept as it happened; for the part of 5.0.0 that predates
this file there is no private account to give, and inventing one after
the fact would be worse than the gap.

What that earlier part changed is in the public `CHANGELOG.md`, which
for this release is unusually full: the chain layer, the
input-adaptation hooks, the neutral authorization provider, the
real-time hardening. The reasoning behind those changes was recovered
instead into [decisions.md](decisions.md), from the source comments that
recorded it, and every entry there says which file it came from.

This release was dated 2026-09-05 in its public heading while it was
still unreleased, and the work that followed went on landing under
`[Unreleased]` above it. Both were merged on 2026-09-14, the day it
actually shipped -- the same trap, and the same fix, as g.Pype's.
