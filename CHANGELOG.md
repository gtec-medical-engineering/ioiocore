## Changelog

### [5.0.1] - 2026-09-24

- **An error handler is told even when stopping the pipeline fails.**
  On a failure the pipeline publishes `ERROR`, stops, and then calls the
  handlers registered with `add_error_handler()`. An element whose
  `stop()` raised used to skip that last step, so no handler heard of
  the failure at all.

  The order is now documented. Whatever a handler records, a caller who
  reads it also sees `ERROR`, and a stopped pipeline unless stopping it
  failed. The converse does not hold: a caller polling `get_condition()`
  can see `ERROR` before any handler has run, and should read
  `get_last_error()`, which already has the entry.

### [5.0.0] - 2026-09-14

Major release following a full reliability audit. It adds a composable
**chain** layer and a pair of input-adaptation hooks, replaces node
authorization with a neutral provider interface, hardens the real-time
data path, threading and error handling for clinical use, and removes an
unsafe serialization path. It is also the first ioiocore release to
publish wheels for Linux and for Python 3.14.
See the [Migration Guide](https://gtec-medical-engineering.github.io/ioiocore/content/migration.html)
for how to upgrade downstream code.

- **A node whose inputs are all asynchronous no longer stalls on its
  first burst.** A source firing immediately after `start()`, while a
  silent sibling producer was still setting up, could leave the consumer
  asleep with its queue full. The first cycle waits until every input
  port has a context, and handing over that context did not wake the
  node -- only an incoming frame did, and the burst was already over.

  It recovered as soon as more data arrived, so it stalled for good only
  where every input is asynchronous and the burst ends: an event port
  fed by a marker source that has gone quiet, or two epoch streams.
  Measured before the fix: eight pushes produced zero cycles in five
  runs out of eight.

- **Wheels for Linux, and for Python 3.14.** A release now publishes 15
  wheels -- Windows, macOS and manylinux_2_28 x86_64, for CPython 3.10
  through 3.14 -- where it published 8 before, Windows and macOS only
  and 3.10 through 3.13. On Linux `pip install ioiocore` previously had
  nothing to install: no wheel, and no source distribution on PyPI
  either.

  The interpreter and platform lists are now read from
  `[tool.ioiocore] python_versions` through `scripts/ci_matrix.py`
  rather than repeated in the release workflow, so a version added there
  is built and not merely tested. The release also refuses to publish
  unless it holds every wheel that matrix calls for: a build that fails
  for one interpreter now stops the release instead of quietly shipping
  without it.

- **`Port` is exported.** `ioiocore.Port` binds the base class that
  `IPort` and `OPort` derive from, and whose `Configuration` defines the
  `name`, `type` and `timing` keys they inherit. It was documented in the
  manual but not importable from the package. `Interface` is no longer in
  the manual: it binds a class to its implementation and has no use in
  building a pipeline. It remains importable as
  `ioiocore.interface.Interface`.

- **An output port can be watched without being consumed.**
  `OPortImp.add_tap(fn)` / `remove_tap(fn)` invoke a plain callable with
  every frame the port pushes, before the fan-out copies, and
  `remove_tap` is safe while data is flowing. A port with no taps costs
  one attribute load and a branch, so nothing that does not use this
  pays for it.

  A callable rather than a node, because attaching a *node* to a
  running graph is not safe: a node with one input port gets no thread
  of its own, so it would execute inside the producer's push -- which
  for a device source is the driver's own acquisition callback -- and a
  node that was attached but never started fills an unbounded input
  queue until the pipeline's backlog monitor stops the run. A tap has
  no queue, no thread, no setup and no lifecycle, so none of that
  applies. What it owes in exchange is stated in `add_tap`: it runs on
  the producer's thread and must return immediately, and it is handed
  the producer's own buffer rather than a copy.

- **A port's connections are held in a tuple that is replaced, not a
  list that is mutated.** `push` iterates that tuple, so connecting or
  disconnecting while data flows can no longer disturb it.

  This was a silent frame loss, and it fell on a bystander. With three
  consumers `[A, B, C]`, removing `A` while `push`'s iterator is on `A`
  makes the loop visit `A, C` and skip **B** -- a filter or a file
  writer, which asked for nothing and is told nothing. Demonstrated
  both ways; `test/test_port_taps.py` reproduces it against a
  pipeline's ports. Nothing in the library disconnected a port mid-run
  until something wanted to, which is why it had not surfaced.

  Costs nothing: measured over the push path, iterating a tuple
  attribute came out marginally faster than the list it replaces (54.0
  against 59.1 ns per push).

- **An element now keeps the exception that stopped it, not only its
  message.** Every catch site wrote `log(msg=e)` and nothing more,
  which reduces an exception to its text and discards the traceback. A
  caller could be told that a node failed and never be shown where,
  because there was no object left to raise `from` -- so no amount of
  checking in the layer above could give a user their own frames back.

  `ProcessingElement.failure()` returns it whole, alongside the log
  entry rather than instead of it: the log is what a running system
  writes down, and this is what a caller raises from. All four catch
  sites record it -- `NodeImp`'s setup and cycle, and `INodeImp`'s
  direct handler and worker thread.

  The **first** failure is kept. A node whose `setup()` raises returns
  from every later cycle without processing, and the `ERROR` condition
  it leaves behind makes the next cycle look like a fresh failure;
  overwriting would replace the cause with its consequence. Cleared by
  `reset_run_state()` with the counter and the condition, so a restarted
  run does not inherit the previous one's verdict.

- **`raise_if_failed()` now chains to the line that failed.** It builds
  its message from the log entry, which carries the exception's text and
  the node's name and cannot carry a traceback -- so a script was told
  that a node failed and had to go looking for the line itself, in its
  own node if it wrote one. It raises `from` the kept exception now, so
  `__cause__` holds the original with its frames intact.

  Measured end to end: a node raising in `step()` produces a
  `RuntimeError` whose `__cause__` traceback ends in `step`, which is
  the user's own method.

  `from` only when there is a cause. `raise X from None` suppresses the
  chain, and an element that kept nothing -- an older element, or a
  failure that reached only the log -- must still raise with whatever
  context Python would have given it.

  Nothing about *when* an exception is caught changed. The batch path
  already propagated -- all three catch sites on it honour `_batch` --
  and the realtime path still catches, because an exception on a source
  thread nobody is waiting on would otherwise die silently. This adds
  what the realtime path was throwing away.

- **An element now reports whether its `setup()` raised, apart from its
  condition.** Both a `setup()` and a `step()` that raise set the element's
  condition to `ERROR`, so a caller holding only the condition cannot tell a
  graph that was never viable from a run that died on its first frame. The
  distinction matters to exactly one caller: `start()`. A configuration
  that cannot work -- a cutoff above Nyquist, a channel count that does not
  agree -- is knowable before any data flows, and the `start()` the caller
  is still inside can refuse it. A `step()` that happens to fail on cycle 1
  is an ordinary runtime failure, and making `start()` raise on that would
  turn every one of them into a start failure.

  `setup_failed()` on `ProcessingElement` therefore reports the first case
  only. It is cleared with the counter rather than with the condition,
  because the counter is what gates `setup()`: a second run sets up again,
  and must not carry the previous run's verdict on a setup that has not
  happened yet. `get_condition()` is exposed on the interface at the same
  time; it existed on the implementation and had no public reader.

- **The engine no longer decimates on top of a node's own answer.**
  `_run_cycle` gated the downstream push on `is_decimation_step()` *in
  addition to* whatever `step()` returned. `step()` returning `None` already
  means "not this cycle", and every node that decimates calls that helper
  itself and returns `None` — the four in g.Pype and this repository's own
  test template — so the extra gate only ever agreed with them.

  Where it could not agree was the case it made impossible. A cycle carries
  `frame_size` samples, so a cadence counted in *cycles* is the intended one
  only at `frame_size == 1`. A node whose decimation is semantic rather than
  paced — one that drops samples, like g.Pype's `Decimator` — therefore could
  not accept any other frame size, and carried a written-down refusal saying
  exactly that.

  `is_decimation_step()` is unchanged and remains how a node paces itself; it
  is simply no longer applied a second time. Suite: 309 passed before and
  after.

**Breaking changes**
- Removed source-code transport from (de)serialization. `Portable`/`Pipeline`
  deserialization now resolves node classes by import (`module` + `class`)
  only; any `source` field in a payload is ignored. Custom nodes must be
  importable on the target host (ship them as a package). `add_preinstalled_module()`
  is now a no-op, kept only for compatibility.
- Removed `source_delay` (the `ONode.source_delay` property, its pipeline
  "equalization", and the `IONode` stubs); it was never applied.
- The data path now copies **on push**: `OPort` hands each connected input
  port its own deep copy, and consumers no longer copy on receive. Producers
  may safely reuse output buffers; fan-out consumers are isolated.
- `Pipeline.start()` now **auto-resets** after an error (previously the
  pipeline was permanently unstartable). Retry policy (backoff, limits) is
  the caller's responsibility.
- The pipeline monitor now **stops the pipeline on excessive input backlog**
  (thresholds `ConstantsImp.BACKLOG_WARNING` / `BACKLOG_ERROR`) instead of
  letting a slow consumer grow memory unbounded.
- Chains no longer silently discard explicitly supplied `input_ports` /
  `output_ports`: a mismatch with the boundary node's ports now raises at
  construction.
- `Chain.get_counter()` / `Chain.get_context()` now delegate to the chain's
  last internal node (previously always `0` / `None`).

**Breaking changes** -- node authorization.
- Removed `NodeImp.add_authorization_key()` and the module-level
  `AUTHORIZED_NODES` set. A node no longer authorizes itself, so node
  authors have nothing to call: with no provider installed, every node
  starts. The old scheme was satisfied by calling it, which its own
  comment acknowledged, and it obliged every author to opt into their
  own authorization for no benefit.

**Added** -- batch execution, for a consumer driving a whole recording.
- `Node.process(data)` beside `Node.step(data)`. `step()` takes one frame;
  `process()` takes everything the node will ever see, in one call, which is
  what a non-causal operation needs and what lets such a node hold no buffer
  of its own. A node declares which execution modes it supports **by which
  of the two it overrides** — derived from structure, so a node cannot claim
  a mode it has no body for. Implementing neither is refused when the node
  is constructed, naming the class.
- `step()` is therefore **no longer abstract**. A node implementing only
  `process()` is valid; calling `step()` on it raises a message saying it
  runs in a batch pipeline only. The refusal for a node with neither method
  moved from `ABCMeta` to `Node.__init__`, because "one of these two" is a
  condition on a pair of methods that `abstractmethod` cannot express.
- `NodeImp.batch`, set by the pipeline before start and never per cycle,
  since a run is wholly one mode. Two things depend on it: which handler
  runs, and whether an exception is caught.
- **A batch run does not swallow exceptions.** `NodeImp._cycle`,
  `NodeImp._setup_wrapper` and `INodeImp._direct_event_handler` catch and log
  on the realtime path — where the caller is a source thread nobody is
  watching and the log is the only channel — and re-raise on the batch path,
  where the driver *is* the caller. All three, not one: a graph with fan-in
  forbidden is a synchronous call stack, so the traceback arrives through the
  caller's own line intact, and catching at any one of the three sites
  swallows it one frame further out, which looks fixed and is not. Most of
  the messages worth reading come from `setup()` rather than `step()` — a
  cutoff above Nyquist, a channel count that disagrees — which is why the
  setup path is included.

**Added**
- Chain layer: `ProcessingElement` base plus `Chain`, `IChain`, `OChain`,
  `IOChain` — reusable containers of internal nodes usable anywhere the
  equivalent node kind is expected.
- `get_input_port()` / `get_output_port()` with fixed direction on all node
  and chain types.
- A chain now *derives* which ports pair its internal nodes instead of
  assuming `out` -> `in`. Sequential wiring is unchanged; the pair is
  resolved by three rules, in order: a single output and a single input
  pair whatever they are called, equal name sets pair by name, and equal
  counts with different names pair in declaration order. Anything else is
  refused naming both sides, where it previously surfaced from inside
  `connect` as a missing port and named only one. The old assumption was
  load-bearing and wrong for any boundary node with more than one port --
  a chain exposes its first internal node's input ports as its own, so a
  transport bridge in front of a multi-port core could neither declare
  those ports nor be wired to them. More permissive than before rather
  than less: the previous form required the exact names `out` and `in`.
- `Node.is_externally_fed()` and `Node.is_externally_drained()`, which a
  node overrides to declare that something outside the pipeline supplies
  or consumes its data. A chain consults them to accept a transport
  bridge at its inlet or outlet, which it would otherwise refuse as a
  node whose ports nothing local feeds.
- `Pipeline.close()` and context-manager support (`with Pipeline() as p:`)
  to release logging resources; `Pipeline.get_backlog()` and
  `Pipeline.is_logging_persistent()`.
- `Logger.stop()`, `Logger.is_persistent()`, and `Logger.get_incident()`
  (a never-evicted last-error/last-warning channel).
- First-class optional configuration keys via `Configuration.OptionalKeys`
  (validated if present, but may be absent).
- Linux support: the default log directory is resolved lazily (XDG path);
  importing the package no longer fails on unsupported platforms.

**Added** -- input adaptation.
- `Node.pre_setup(data, port_context_in)` and `Node.pre_step(data)`, a
  symmetric pair of extension points called immediately before `setup()`
  and `step()`. Both modify their argument in place and default to doing
  nothing. `pre_step` may also return True to **withhold the cycle**:
  `step` is not called and nothing is emitted. A hook that holds frames
  back needs that -- the alternative is fabricating a frame to keep the
  cycle going, which puts invented samples at the head of the stream and
  shifts every later one. The cycle counter still advances, so `setup`
  is not repeated and any decimation phase stays aligned with the cycles
  the node was actually driven through. Together they let a consuming
  package present every node with
  uniform inputs without each node author knowing about it: `pre_setup`
  settles what the inputs *are* -- channels, rate, timing -- and
  `pre_step` supplies frames that match. Adapting only the frames would
  be too late, because a node decides its own output shape in `setup()`
  from exactly those contexts. The engine holds no opinion about what
  "uniform" means; that belongs to the domain layer.

**Added** -- a way for a *program* to learn that the run failed.
- `Pipeline.add_error_handler(handler)` is called once when the run
  fails. A failure is detected asynchronously, after `start()` has
  returned, so there is nothing for `start()` to raise -- and until now
  the only report was printed to a console, which a windowed application
  may never show. The handler runs on the monitoring thread, so it should
  hand the news to whatever owns the user interface rather than doing
  work itself; an exception raised inside it is logged and swallowed,
  because that thread is the only channel that reports failures and must
  not die reporting one.
- `Pipeline.raise_if_failed()` for a script that would otherwise carry on
  past a dead pipeline. The message names the exception, the node and the
  source location.
- `Pipeline.get_last_error()` was annotated `str` but returns a
  `LogEntry`. The annotation is corrected: it hid the node and location a
  reader needs.

**Added** -- node authorization, replacing the above.
- `set_authorization_provider(provider)` and `authorization_provider()`.
  A consuming package that must gate execution installs any object with
  `is_authorized(key) -> bool`; it is asked once per node `start()`,
  never per cycle, and receives the node's concrete type. Whatever
  secret the decision rests on stays in the consumer's package --
  ioiocore holds no policy and no secret, which is why this is an
  interface rather than an implementation.
- Registration is **one-way**: a second call raises. Otherwise
  installing a permissive provider first would defeat a real one. A
  consumer must treat a failed registration as fatal rather than
  continuing ungated.

**Added** -- serialization, so a document can be written by something
other than ioiocore itself.
- A serialized document carries `format_version` and `writer`. A document
  written by a **newer** revision than the running build is refused
  outright rather than half-understood, and one carrying no
  `format_version` is read as the pre-5.0.0 revision; re-saving it stamps
  the current one.
- A connection may name its endpoints instead of carrying port ids:
  `"gen.out"` for a named port, or `"gen"` for the node's default one.
  `serialize()` still writes ids and ids are still resolved first, so no
  existing document changes meaning. The names are for a document written
  by hand or by an authoring tool, which cannot know the ids a future
  process will mint.
- A chain no longer embeds its internal nodes in a document; the loader
  rebuilds them from the chain's own definition, so the process that
  loads a document decides a chain's composition. Set
  `INTERNALS_ARE_DERIVED = False` on a chain whose composition a document
  must pin instead.

**Fixed**
- A generated node id is sixteen hexadecimal digits every time. One value
  in sixteen was padded with spaces rather than zeros and came out short,
  so a consumer matching `[0-9A-F]{16}` -- an authoring tool keying its
  boxes on the id -- failed intermittently and for no visible reason.
- A document asking for a generated node id now gets one. The sentinel
  was compared by identity, and a document's own copy of it arrives from
  `json.loads` as a different object, so it was taken for a real id and
  two such nodes collided.
- A node whose inputs include a port that never delivers data now runs. The
  first cycle waits for a *context* on every input port instead of *data* on
  every input port, so a producer that has set up but has nothing to emit no
  longer starves its consumer.
- Port contexts are delivered when the producer sets up, not on its first data
  push, so a silent port still describes its stream.
- A multi-input node with only asynchronous inputs drains its whole queue per
  wake instead of a single item, no longer stranding queued data. This
  completes the single-input fix listed below.
- A node no longer runs `step()` or pushes data after its `setup()` fails.
- Error reporting no longer crashes on argument-less exceptions or
  non-string log messages; the log-writer thread survives a malformed entry.
- `Pipeline.start()` is atomic: a node failing to start rolls back the
  already-started nodes and re-raises, instead of leaving unstoppable ones.
- Single-input node execution no longer races between `start()` and the
  producer thread, and drains all queued items per event (no lost trailing
  samples); `stop()` no longer hangs behind an input backlog.
- The monitor thread is joined on `stop()` (no duplicate monitors after a
  restart); the logger is flushed and closed on `close()`.
- The per-cycle deep copy is no longer performed while holding the input
  port locks.
- An `IONode` with all-async outputs no longer spawns the pure-source setup
  thread (MRO hazard).
- A failed `connect()` (or deserialization) no longer leaves a half-connected
  port that still receives data.
- Error detection uses a sticky incident channel, so a burst of log entries
  can no longer evict an error before the monitor sees it; `get_last_error()`
  is likewise reliable.
- `Portable`'s id registry uses weak references (no longer keeps every node
  and port alive for the process lifetime); clearer id-conflict message.
- `Configuration` and `Context` now block `del` (implement `__delitem__`).
- Chain deserialization rebinds subclass node handles to the restored nodes;
  chain port configuration is deep-copied (no shared mutable state).
- Removed unconditional 10 ms sleep in node setup; removed the shared mutable
  default `data={}` on the cycle entry points; removed dead code
  (`PortImp.get_state`, node authorization key fields).

**Fixed** -- error reporting, which is the code path that reaches a user
at the worst possible moment.
- A logged exception lost its type. `str(e)` alone was used whenever it
  produced any text, so a `KeyError` reached the user as
  `*** 'sampling_rate' ***` -- the one word carrying the meaning was the
  word that got dropped. Now `KeyError: 'sampling_rate'`.
- The error banner did not say which node failed. It rebuilt a bare file
  path while the log entry already carried an unused `summary` reading
  `Class.function() [file:line]`. That is now shown, together with the
  node's instance name: a graph with three `Bandpass` nodes previously
  gave no way to tell which one stopped.
- ANSI colour codes were emitted unconditionally. Redirected to a file,
  captured by a test harness or displayed in a notebook, the most
  important message a user ever receives arrived wrapped in literal
  `[31m`. Colour is now used only when stdout is a terminal, and
  `NO_COLOR` and `TERM=dumb` are honoured.
- The banner joined the directory and filename with a hard-coded
  backslash, which is wrong on macOS.
- A failed deserialization raised `TypeError` without chaining, so a
  missing port id surfaced with no trace of the real cause. Now chained.
- When a log file could not be created the reason was discarded, in two
  separate handlers, and the banner then told the reader to consult it:
  `See log file for details: None`. Both handlers now record the cause
  and the attempted path, `Logger` exposes them, and the banner says
  `No log file was written at <path> (<reason>). This message is all
  there is.` The warning at construction names the cause as well, which
  is the moment a user can still act on it.
- A node that failed to start reported `TypeError: Argument 'msg' has
  incorrect type` instead of why it failed. `Pipeline.log` takes a `str`
  while the node loggers take `str` or `Exception`, and the partial-start
  recovery path passed the exception object -- so the logging call inside
  the handler raised, replacing the error being handled and pre-empting
  the `raise` on the next line. A regression test for this had been
  failing.

**Changed** -- the release chain, which is now g.Pype's.

- The version comes from the git tag via `setuptools_scm`, read from
  CHANGELOG.md by `nox -s tag_create`, instead of from a hand-maintained
  `VERSION` tuple. `src/ioiocore/__version__.py` is generated and no longer
  in the repository, so a source checkout needs its git history to report a
  version; `ioiocore.__version__` is unchanged for anyone installing a
  wheel. `VERSION` itself is gone -- nothing read it.
- `pyproject.toml` now carries the project metadata and the dependency
  extras that the `requirements-*.txt` files held, and declares which
  modules are compiled (`[tool.ioiocore] cython_files`). `setup.py` is
  reduced to building the extensions it finds.
- Builds, tests, linting, cleaning and tagging run as nox sessions, shared
  with g.Pype file for file; `scripts/make_*.bat` are thin wrappers around
  them. `setup.py` no longer renames the sources in place and restores them
  from an `atexit` hook, so a build that fails can no longer leave the
  package as a directory of `.pyx` files with nothing to import.

**Deprecated**
- `Chain.get_port()` — use `get_input_port()` / `get_output_port()`.
- `Portable.add_preinstalled_module()` — no-op (source transport removed).

**Security**
- Removed `exec()` of serialized class source during deserialization (an
  arbitrary-code-execution surface reachable from `Pipeline.deserialize()`).


### [4.0.7] - 2026-02-20
- Fixed reference leakage in context propagation
- Added direct execution policy in consecutive nodes
- Removed pipeline load monitoring (not accurate)
- Added support for macOS 14+

### [4.0.6] - 2026-01-21
- Made put/get at port level thread-safe
- Fixed bug in data availability condition

### [4.0.5] - 2026-01-14
- Fixed some bugs in the de/serialization procedure

### [4.0.4] - 2026-01-07
- Asynchronous/synchronous data propagation decoupled in step() function

### [4.0.3] - 2025-12-01
- Asynchronous data propagation improved

### [4.0.2] - 2025-07-11
- Source delay handling implemented

### [4.0.1] - 2025-07-11
- Minor bugfixes
- Improved logging & exception handling

### [4.0.0] - 2025-07-10
- Updated interface
- Improved logging

### [3.0.0] - 2025-07-03
- Moved from metadata to contexts
- Bugfixing

### [2.3.1] - 2025-06-16
- Added multirate support
- Bugfixing

### [2.3.0] - 2025-04-16
- Increase unit test coverage
- Added support for Python 3.8 and 3.9

### [2.2.6] - 2025-02-24
- Added Changelog to README.md
- Added support for Python 3.10

### [2.2.5] - 2025-02-24
- Skipped

### [2.2.4] - 2025-02-21
- Updated documentation
- Added support for macOS
- Added support for Python 3.11

### [2.2.3] - 2025-02-20
- First public beta release
