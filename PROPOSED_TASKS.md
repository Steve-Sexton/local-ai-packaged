# Proposed Maintenance Tasks

## 1) Typo fix task
**Task:** Fix the typo in `n8n_pipe.py` where a comment says `assitant` instead of `assistant`.

- **Why:** Typos in comments reduce readability and professionalism.
- **Location:** `n8n_pipe.py` comment above the assistant message append.
- **Acceptance criteria:** The comment uses the correct spelling (`assistant`) and no new lint issues are introduced.

## 2) Bug fix task
**Task:** Fix `Pipe.pipe()` in `n8n_pipe.py` so it does not return an undefined `n8n_response` when no messages are provided.

- **Why:** In the `else` branch (`messages` is empty), `n8n_response` is never assigned, but the function still returns it, which can raise `UnboundLocalError`.
- **Location:** `n8n_pipe.py`, final `return n8n_response` in `Pipe.pipe()`.
- **Acceptance criteria:**
  - Calling `pipe()` with an empty `messages` list does not crash.
  - The method returns a deterministic response shape for the no-message case (for example, the updated `body` or a structured error object).

## 3) Comment/docs discrepancy task
**Task:** Align README references from `start-services.py` to the actual script name `start_services.py`.

- **Why:** README currently mentions `start-services.py` in multiple places, but the script in the repo is named `start_services.py`.
- **Location:** `README.md` sections discussing startup commands and environment options.
- **Acceptance criteria:** All script name references in README match the actual file name and command examples remain valid.

## 4) Test improvement task
**Task:** Add unit tests for `n8n_pipe.Pipe.pipe()` covering edge cases and response behavior.

- **Why:** There are currently no tests for key logic paths in `n8n_pipe.py`.
- **Recommended coverage:**
  - Empty `messages` payload behavior.
  - Non-200 response from n8n webhook.
  - Successful 200 response maps `response_field` correctly and appends assistant output.
  - `emit_status` throttling behavior based on `emit_interval`.
- **Acceptance criteria:**
  - Tests run in CI/local with deterministic results.
  - At least one test asserts no crash on empty `messages` input.
