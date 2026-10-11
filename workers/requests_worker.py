"""Judge hook worker. Owner: Shiv (S7). Reviewer: Talal.

Watch `requests` for status "queued" (change stream). For each:
set status "running", run one attempt with source "judge", audit it,
set status "done" with trial_id, or "error" with a message. Send request_done or request_error.
Uses the worker role.
"""


def run_forever() -> None:
    raise NotImplementedError("S7")
