# Implementation Plan: Prompt to install requests when the dependency is missing

## Summary
Add a graceful dependency check for the `requests` package at script start‑up. If `requests` is not installed, display a clear explanatory message and prompt the user to install it now. On confirmation, invoke `pip` to install the package, handle any errors, and exit with instructions to re‑run the scraper. The change must never perform an unattended installation.

## Affected Modules
- **menu_entries.py** – primary entry point; imports `requests` and contains all scraper logic.
- *(optional)* **utils/dependency_check.py** – if a small helper module is introduced for reusable checks (still within the same repository).

## Milestones
1. **Create dependency‑check helper**
   - Scope: Add a new function (`ensure_requests()`) that attempts to import `requests`, catches `ModuleNotFoundError`, and returns a boolean indicating presence.
   - Done when: Function exists, unit‑tested (manual) in isolation, and no import errors are raised when `requests` is installed.

2. **Add interactive prompt & install logic**
   - Scope: In the helper, after detecting missing `requests`, print a friendly message, ask “Would you like to install it now? [y/N]”, read user input, and on affirmative run `[sys.executable, "-m", "pip", "install", "requests"]` via `subprocess.check_call`. Capture any exception and report failure.
   - Done when: Running the script without `requests` displays the message, prompts correctly, attempts installation on “y”, reports success or error, and then exits.

3. **Integrate helper at top of `menu_entries.py`**
   - Scope: Call `ensure_requests()` before any other imports that require `requests`. If the function returns false (install declined or failed), exit with status 1.
   - Done when: The script starts cleanly on a system where `requests` is present, and aborts early with the prompt on a system where it’s missing.

4. **Refactor existing imports to use the ensured module**
   - Scope: Move the original top‑level `import requests` inside the helper or after the check so that the rest of the file can safely reference `requests`.
   - Done when: No `ImportError` occurs in any code path when `requests` is installed, and the script’s functional behavior (fetching links, menus, searching) remains unchanged.

5. **Manual verification & edge‑case handling**
   - Scope: Test the script in three scenarios:
     1. `requests` present – normal execution.
     2. `requests` missing – user answers “n”. Script exits with explanatory message.
     3. `requests` missing – user answers “y” and pip succeeds. Script reports success and instructs to re‑run.
   - Done when: All three scenarios behave as described, error messages are clear, and no silent failures occur.

## Data Model Changes
None

## Risks & Edge Cases
- **Permission issues**: `pip install` may fail due to lack of write permission or virtual‑env constraints. The script must catch this and display the underlying error without crashing.
- **Non‑standard Python environments**: Users might be running the script with a custom interpreter where `pip` isn’t available or is aliased differently. Provide a fallback message suggesting manual installation.
- **Repeated runs after install**: After a successful auto‑install, the process exits; users must re‑run the script to load the newly installed package. Ensure the exit status makes this clear.
- **User aborts**: If the user types anything other than “y” (case‑insensitive), treat it as a decline and exit cleanly.
- **Network failures during pip install**: Network errors should be reported, and the script should not hang indefinitely; `subprocess.check_call` will raise an exception that we capture.