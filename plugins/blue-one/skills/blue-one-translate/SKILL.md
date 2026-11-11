---
name: blue-one-translate
description: Translate text, images, PDFs, Word, Excel, or PowerPoint files using Blue One. Use for Blue One translation requests, document translation that preserves layout, or troubleshooting a Blue One connector or file transfer. Requires a connected Blue One MCP service.
---

# Blue One translation

Use the connected Blue One MCP tools to translate the user's content and return the actual service result. Follow the user's requested language and output format. Ask for a target language only when it cannot be inferred from the request or conversation. Reply in the user's language.

## Choose the workflow

Inspect the available Blue One tool descriptions and input schemas; tool prefixes differ between hosts. Use `translate_text` for text or an article URL. Use `translate_file` for an attached document, spreadsheet, presentation, PDF, or image. Use `translate_pdf_bilingual_reader` when the user wants side-by-side reading of a PDF. Supply only parameters supported by the connected server.

For a file, use the original attachment's bytes so Blue One can preserve its structure. If the user requests text inside embedded images as well, use the tool's `do_image_translation` option and its current cost description. Follow the tool's PDF output options when the user asks for an editable document. The language code for Japanese is `ja`.

If no Blue One tools are available, explain how to connect the bundled connector and sign in. Read [connection and error handling](references/troubleshooting.md) when connection, transfer, or translation fails. `list_jobs` with `limit: 1` is a read-only way to check MCP access; it cannot confirm the selected team's name or credit balance.

## Translate an attachment

1. Locate the actual local attachment and its extension. Call `generate_upload_url` once for that format. Read `max_bytes`, `expires_in_seconds`, and any other constraints from its response; use the live response instead of assuming service limits.
2. Save the tool's JSON result to a temporary ticket file without reconstructing the URL. Run the bundled helper from this skill's directory:

   ```sh
   python3 scripts/transfer.py upload --ticket /path/to/upload-ticket.json --input /path/to/attachment.pptx
   ```

   Wait for `ok: true`. The helper streams the bytes, checks the declared capacity, and reports a byte count and SHA-256 without printing the bearer URL. Remove temporary ticket files when finished. The helper requires Python 3; when unavailable, use an equivalent streaming HTTP client in the host environment, preserving the returned URL and handling the same errors. File contents and base64 belong in the transfer client, not in model-generated tool arguments.
3. Pass the returned `file_id` to the chosen translation tool with the requested language and options. Keep the resulting `job_id`. If the submission response is lost or interrupted, inspect recent `list_jobs` results before retrying: another submission can create another billable translation. If you cannot determine whether it was accepted, explain the uncertainty and ask how to proceed.
4. Poll `get_job_status` for that job. Respect its `retry_after_seconds`; pending and in-progress states are not failures. When the conversation's execution budget is nearly exhausted, return the pending `job_id` and resume from it later. A terminal failure ends this attempt; report the service's error without silently submitting again.
5. On success, save the status response to a temporary ticket and download the requested artifact to a new local file:

   ```sh
   python3 scripts/transfer.py download --ticket /path/to/status.json --output /path/to/translated.pptx
   ```

   The helper defaults to `download_url`; use `--field docx_download_url` for a reader's DOCX. Choose a writable output path appropriate to the host. Present that downloaded file using the host's file presentation mechanism. A URL alone or a locally reconstructed document is not a verified Blue One artifact.

If a download URL expires or has already been used, request fresh URLs for the **same job** with `get_job_status`. For a failed upload, obtain a new upload ticket before another attempt; confirm the file and network conditions first. Stop if the same cause persists and give the user the next useful action.

If the service reports success without an artifact, re-check that job as its description recommends. If the artifact remains unavailable or its retention deadline has passed, explain that result. Re-translating requires a new user decision.

## Text results and failure boundaries

For text, return the translation from the service payload, keeping extra explanations only when the user asks for them. Blue One's saved glossary and rule selections may apply; the current tool schema determines whether per-call glossary or style inputs are available. Plain text translation does not guarantee preservation of arbitrary row IDs or formatting tags.

When file translation is blocked, explain the failed stage and offer alternatives. Extracting text and rebuilding an Office file is a different workflow that can lose images, layout, notes, and formatting; get agreement before using it. Treat any such output as a separate alternative, not a successful Blue One file translation.

A translation request authorizes the requested translation under normal service charges. It does not authorize buying credits, changing organization policies, connecting a different account, uploading to an unrelated service, or invoking internal inspection tools. Keep document contents, credentials, and transfer URLs out of diagnostic reports.
