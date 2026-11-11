# Connection and error handling

Use observed tool/HTTP results and distinguish what was tested from what is inferred. A reachable `/health` endpoint proves only the execution environment can reach the service; it does not authenticate the user, prove file access, or establish that a translation will succeed.

| Observation | Next action |
| --- | --- |
| No Blue One MCP tools | Open the installed plugin's connector settings, add/connect Blue One, and complete OAuth with the intended account and team. Team/Enterprise owners may first need to allow the connector. |
| MCP call returns 401 | Ask the user to reconnect or sign in. Avoid paid translation calls as authentication probes. |
| MCP call returns 403 | Check the reported team access, MCP switch, membership, or IP restriction. A 403 alone does not identify which setting caused it. |
| MCP works but file HTTP fails | Run `python3 scripts/transfer.py probe` from this skill's directory. It makes a read-only request to `/health` on the bundled MCP origin. MCP connectivity and code-execution network access are separate. |
| Probe reports `network_unreachable` | Ask the Claude organization owner to check Code execution / network egress and the allowlist for the host declared in this plugin's MCP configuration. DNS or TLS failure can also have other causes; do not assert an organization setting was inspected. |
| HTTP 403 on a transfer | Check both organization network restrictions and Blue One's transfer access/IP restrictions. If the probe works, the server or an intervening gateway may still reject the transfer. Report the status, not an invented cause. |
| Helper reports `invalid_url` | Confirm the ticket is from this connector and the server supports self-domain transfers. A legacy storage URL requires a compatible server deployment, not a guessed replacement URL. |
| HTTP 404 or 409 | The transfer may be expired, used, or the file unavailable. Refresh the upload ticket, or fetch a fresh download URL for the existing job. Confirm the file still exists before retrying. |
| HTTP 413 / `file_too_large` | Compare the file size with the upload ticket's current `max_bytes`. Ask the user to choose a smaller file or another workflow. |
| HTTP 429 | Report the applicable capacity/rate/concurrency limit. Respect Retry-After when provided. Stop repeated attempts; later use or an administrator decision may be needed. |
| Transfer interrupted / HTTP 408 or 5xx | The URL may already have been consumed. Preserve the file and obtain a new ticket for a subsequent attempt. A translation submission with an uncertain outcome must first be checked through job history. |
| Job status is failure | Report the error for that job. Keep the job ID for support. Offer another attempt only after explaining it may consume credits. |

For Claude Team/Enterprise, an owner configures external network access in organization settings. A plugin cannot grant itself that permission or perform the user's OAuth consent. The owner can allow the MCP host as a specific destination; all-domain access is not required by this plugin.

Keep the user-facing report short: failed stage, observed code, job ID if present, and who can take the next action. Exclude file contents, headers, raw exceptions, bearer URLs, and tokens. When contacting support is needed, let the user decide to send the report.
