<!--
Project-specific Copilot instructions for `random-scripts`.
Keep this concise and actionable — reference concrete files and patterns found in the repo.
-->

# Copilot instructions — random-scripts

Purpose: Help an AI code assistant be immediately productive in this repository.

**Big Picture**:
- **Repository type**: small collection of standalone Python scripts (utility and exploratory scripts).
- **Primary entrypoints**: top-level scripts such as `sfl.py` and small helpers like `classproperty.py`.
- **Data flow / architecture**: there is no service or package boundary — each script is self-contained and typically executed directly with `python3 <script>.py`.

**Run / dev commands**:
- Run the main loan/payoff calculator: `python3 sfl.py` (expects Python 3.9+ because of `list`/`tuple` type hints like `tuple[int, float]`).
- There are no tests, build tools, or virtualenv manifests in the repo; create a `requirements.txt` or virtualenv when adding dependencies.

**Project-specific conventions & patterns**:
- Files are small scripts — preserve simple single-file structure when adding features unless creating a clear reusable module.
- Many scripts use plain `print()` for output rather than the `logging` module. Keep changes minimal and consistent with that style unless requested otherwise.
- Several filenames in `archive/` include spaces (e.g. `Binary insertion sort.py`); when referring to or editing these files, quote or escape filenames in shell commands.
- Main-check style: some files use the reversed idiom `if "__main__" == __name__:` — do not automatically rewrite to `if __name__ == "__main__":` unless asked.

**What to change vs. what to avoid**:
- Change: fix clear bugs, add small helper functions, add type hints and docstrings consistent with existing style (see `sfl.py`).
- Avoid: large refactors that split small scripts into packages without an accompanying test harness or run instructions.

**Examples from the codebase**:
- `sfl.py`: financial simulation functions (`take_home_pay`, `get_mandatory_payment`, `month`, `get_months_until_loan_payed_off`) — keep method signatures stable when changing logic because callers are within the same file.
- `classproperty.py`: demonstrates a lightweight descriptor pattern used for class-level read-only properties. Use similar minimal helper classes for small utilities.

**Integration & external dependencies**:
- Currently none external. If adding dependencies, update `README.md` and add a `requirements.txt` or `pyproject.toml` and include run instructions.

**PR guidance for Copilot / AI**:
- Make one focused change per PR; include a short `README` or note describing how to run any new script.
- If you add a dependency, include exact install steps and a simple sanity run command.

**Open Questions / Ask the repo owner**:
- Preferred Python runtime version (I inferred 3.9+ from type hints).
- Whether you want scripts converted to a package/module layout or kept as standalone scripts.

If anything here looks incorrect or you want more/less strict rules (packaging, linting, tests), tell me which direction to take and I will update this file.
