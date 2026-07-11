# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Arggo is a Python toolkit for reproducible experiment management, inspired by Hydra and HuggingFace's `HfArgumentParser`. Given a `@dataclass` of arguments, Arggo auto-generates a CLI parser, injects the parsed arguments into a decorated main function, isolates each run in its own timestamped working directory, and persists the run's parameters to JSON for later reproduction.

## Commands

Install dependencies:
```shell
pip install -r requirements.txt -r requirements-dev.txt
```

Run all tests (with coverage):
```shell
python -m pytest --cov=arggo
```

Run a single test file / test:
```shell
python -m pytest tests/test_arggo.py
python -m pytest tests/test_arggo.py::TestSimpleAnnotation::test_function_no_arguments
```

Format code (pre-commit uses `black`):
```shell
black .
```

Lint (as run in CI):
```shell
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

The `arggo-cli` entry point (defined in `setup.py`) is installed as a console script and is also runnable via `python -m arggo.cli.main`.

## Architecture

### Decorator-driven entry point (`arggo/core.py`)

The public API (`arggo.consume`, `arggo.configure`) is a single decorator factory, `_main_annotation`, aliased two ways:
- `arggo.consume` — the decorator itself, pre-applied with defaults (used as `@arggo.consume`).
- `arggo.configure(...)` — call it with kwargs (`parser_argument_index`, `logging_dir`, `init_working_dir`, `plugins`) to customize behavior, then apply the result as a decorator.

When the decorated function is called, it:
1. Inspects the function's type hints to find the dataclass-typed argument (at `parser_argument_index`).
2. Parses "meta-arguments" (`--arggo_help`, `--arggo_interactive`, `--arggo_reproduce`) which control Arggo's own behavior, separately from the user's dataclass fields.
3. Builds (once, cached in a process-wide `GlobalStore`) a `DataClassArgumentParser` — or wraps it in an `InteractiveArgumentParser` if `--arggo_interactive` was passed — and uses it to construct a `NewExperiment` either from CLI args or from a previously reproduced parameters file.
4. Initializes an isolated working directory (`Workdir`), redirects stdout to also write to a log file in that directory (`FileLogger`), and saves the experiment's parameters as JSON.
5. Invokes the original function with the parsed dataclass instance spliced into the original argument list at `parser_argument_index`.

Because parser/workdir state is cached in a global store keyed by process, calling a `configure()`/`consume`-decorated function multiple times (e.g. in a loop) reuses the same parsed arguments and working directory rather than reparsing — see the `greet_user` loop example in the README.

### Argument parsing (`arggo/parser.py`)

`DataClassArgumentParser` extends `argparse.ArgumentParser`, introspecting dataclass fields (including special handling for `bool`, `List[T]`, and `Enum` fields) to auto-generate CLI arguments. Field-level customization (help text, choices, required-ness, custom type mappers) is attached via `dataclasses.field(metadata=...)`, which `arggo.dataclass_utils.parser_field`/`mapped_field` make ergonomic. This parser also supports `parse_json_file`/`parse_dict` for non-CLI instantiation, used when reproducing a past run.

### Experiments (`arggo/experiment/experiment.py`)

`Experiment` is the abstract notion of a run's parameters + metadata (executable, command, script path, reproduced-from path, and plugin dumps). Two concrete implementations:
- `NewExperiment` — a run being started now; built `from_arguments()` (parse CLI) or `from_reproduced()` (parse a saved `parameters.json`).
- `FinishedExperiment` — a previously completed run loaded back from its `parameters.json` on disk, used by `arggo-cli experiment reproduce` to re-invoke the original script with `--arggo_reproduce <dir>`.

### Working directory isolation (`arggo/environment/workdir.py`)

`Workdir` wraps a pluggable `DirectoryStrategy` (default: real `os.makedirs`/`os.chdir`) and tracks original/current directories in the `GlobalStore` so state survives across the decorated calls within one process. `init_workdir` creates a `<logging_dir>/%Y-%m-%d/%H-%M-%S` directory and chdirs into it — this is what gives each run its own isolated output location (see `logs/`, `my_logs/` in the repo, which are per-run output examples and are gitignored).

### Global process state (`arggo/_internal/global_store.py`)

A minimal namespaced key-value store backed by a module-level dict, used wherever Arggo needs state that must persist across multiple decorated-function invocations in the same process (parser cache, workdir, logger-bound flag) without threading it through function signatures explicitly.

### Plugins (`arggo/plugin.py`, `arggo/integration/`)

`Plugin` is an abstract hook (`name`, `parameters_dump()`) for attaching extra metadata to a saved experiment. `CondaPlugin` (`arggo/integration/conda.py`) is the only built-in plugin, recording the active conda environment when present. Default plugins are loaded in `core.py::_load_default_plugins()`; additional plugins are passed via `arggo.configure(plugins=[...])`.

### CLI (`arggo/cli/`)

Built with `click`. `cli.py` holds the actual command implementations (`experiment_create`, `experiment_run`, `experiment_reproduce`); `click_hooks.py` wires them into the `arggo-cli` command group (`experiment create|reproduce|run`); `main.py` is the `python -m` entry point. `experiment create <name>` renders `arggo/templates/experiment_create.jinja` into a new starter script. `experiment reproduce <name>` recursively searches a logging directory for saved `parameters.json` files matching the experiment name and lets the user pick one to re-run.

### Interactive mode (external `interactive_argparse` package)

Interactive prompting is delegated to the sibling `InteractiveArgparse` library (`interactive_argparse` on PyPI/import path), not implemented in-tree. `core.py` wraps the generated `DataClassArgumentParser` in the library's `InteractiveArgumentParser` when the `--arggo_interactive` meta-argument is passed; the wrapper monkeypatches `parse_known_args` to convert argparse `Action`s into prompter-agnostic `Question`s and collect answers via a `Prompter` (terminal prompts through `PyInquirerPrompter` by default). Because the library's own prompt-or-not heuristic only looks at leftover CLI args, and arggo's `--arggo_interactive` flag would itself count as one, `core.py` explicitly passes `args=[]` through `NewExperiment.from_arguments` whenever that meta-flag is set, forcing the prompt unconditionally. `arggo/cli/cli.py`'s `experiment_reproduce` also builds a `Question`/`PyInquirerPrompter` directly (instead of a raw PyInquirer dict) to let the user pick which saved run to reproduce.

## Notes for making changes

- Supported Python range per `setup.py`/CI matrix is 3.6–3.8, but development is against whatever `python3`/`pytest` resolve to locally (currently 3.11) — be wary of relying on typing features unavailable in older Pythons (e.g. `from __future__ import annotations` / PEP 563 postponed evaluation is explicitly unsupported, see the `ImportError` raised in `DataClassArgumentParser._add_dataclass_arguments`).
- `GlobalStore` state is process-global and not reset between test cases automatically; tests that touch `Workdir`/parser caching may need to account for this (see `tests/test_workdir.py`'s use of a `FakeDirectoryStrategy` and explicit `revert()` calls).
