# Proposed Maintenance Tasks

## 1) Typo fix task
**Task:** Fix the typo `Unbuntu` → `Ubuntu` in the cloud deployment prerequisites.

- **Why:** The typo appears in a user-facing setup section and reduces documentation quality.
- **Location:** `README.md` in the “Deploying to the Cloud” prerequisites list.
- **Acceptance criteria:**
  - The text reads `Ubuntu`.
  - Markdown formatting and surrounding list structure remain unchanged.

## 2) Bug fix task
**Task:** Make `Pipe.pipe()` robust when the request body does not contain a `messages` key.

- **Why:** `messages = body.get("messages", [])` allows a missing key, but the no-message branch later calls `body["messages"].append(...)`, which raises `KeyError` if `messages` was absent.
- **Location:** `n8n_pipe.py`, no-message branch in `Pipe.pipe()`.
- **Acceptance criteria:**
  - Calling `pipe({})` does not crash.
  - The no-message path returns a deterministic response and/or appends to an initialized `messages` list.
  - Existing behavior for valid `messages` payloads remains unchanged.

## 3) Code comment / documentation discrepancy task
**Task:** Align the `Pipe.pipe()` return type annotation and docs/comments with actual runtime behavior.

- **Why:** The function is annotated as `Optional[dict]`, but success returns a string (`n8n_response`) and failures return a dict (`{"error": ...}`). This discrepancy makes maintenance and static analysis harder.
- **Location:** `n8n_pipe.py`, `Pipe.pipe()` signature and any nearby explanatory text/comments.
- **Acceptance criteria:**
  - Return typing accurately documents all real return shapes.
  - Developers can infer success/error contract from code annotations/docs without ambiguity.

## 4) Test improvement task
**Task:** Add regression tests for malformed and missing-message request bodies in `tests/test_n8n_pipe.py`.

- **Why:** Current tests cover `messages=[]` but do not cover `body={}` or malformed message objects; these are common edge cases for webhook payloads.
- **Recommended coverage:**
  - `pipe({})` should not raise and should produce the expected fallback behavior.
  - `messages=[{"role": "user"}]` (missing `content`) should produce a controlled error path instead of an uncaught exception.
  - Optional: assert emitted status events for each edge case.
- **Acceptance criteria:**
  - New tests fail before the bug fix and pass after it.
  - Test suite remains deterministic and independent of external services.
