#!/usr/bin/env python3
"""Bounded, single-attempt file transfers for Blue One's bearer-capability URLs."""
import argparse
import hashlib
import http.client
import json
import os
import re
import socket
import ssl
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CHUNK = 64 * 1024
# Client-local disk safety budget, independent of the service's authoritative limit.
DOWNLOAD_BUDGET = 128 * 1024 * 1024


class TransferError(Exception):
    def __init__(self, code, message, status=None):
        self.code, self.message, self.status = code, message, status
        super().__init__(message)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def origin_from_plugin():
    config = Path(__file__).resolve().parents[3] / "mcp.json"
    return origin(json.loads(config.read_text())["mcpServers"]["blue-one"]["url"])


def origin(url):
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username
            or parsed.password or parsed.port not in (None, 443)):
        raise TransferError("invalid_url", "Expected the configured HTTPS MCP origin.")
    return f"https://{parsed.hostname}"


def transfer_url(url, expected_origin):
    if not isinstance(url, str) or origin(url) != expected_origin:
        raise TransferError("invalid_url", "Transfer URL must use the configured MCP origin.")
    parsed = urllib.parse.urlsplit(url)
    if parsed.query or parsed.fragment or not re.fullmatch(r"/files/[A-Za-z0-9_-]{43}", parsed.path):
        raise TransferError("invalid_url", "Expected a Blue One file transfer capability URL.")
    return url


def positive_integer(value):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise TransferError("invalid_ticket", "Expected a positive byte limit from the upload ticket.")
    return value


class UploadBody:
    def __init__(self, stream, size):
        self.stream, self.size, self.sent = stream, size, 0
        self.digest = hashlib.sha256()

    def read(self, size=CHUNK):
        data = self.stream.read(min(size if size >= 0 else CHUNK, self.size - self.sent + 1))
        self.sent += len(data)
        if self.sent > self.size or (not data and self.sent != self.size):
            raise TransferError("file_changed", "The input file changed during upload; request a new ticket.")
        self.digest.update(data)
        return data


def upload(ticket, path, expected_origin, opener):
    url = transfer_url(ticket.get("upload_url"), expected_origin)
    limit = positive_integer(ticket.get("max_bytes"))
    with Path(path).open("rb") as source:
        size = os.fstat(source.fileno()).st_size
        if size == 0 or size > limit:
            raise TransferError("file_too_large", "The input must be non-empty and within the ticket's max_bytes.")
        body = UploadBody(source, size)
        request = urllib.request.Request(url, data=body, method="PUT", headers={"Content-Length": str(size), "Content-Type": "application/octet-stream"})
        with opener.open(request, timeout=60) as response:
            if response.status not in (200, 201, 204):
                raise TransferError("http_error", "Upload did not succeed.", response.status)
        if body.sent != size:
            raise TransferError("incomplete_upload", "Upload completion could not be verified.")
        return {"ok": True, "bytes": size, "sha256": body.digest.hexdigest()}


def download(ticket, field, output, expected_origin, opener, max_bytes=DOWNLOAD_BUDGET):
    url = transfer_url(ticket.get(field), expected_origin)
    positive_integer(max_bytes)
    target = Path(output)
    if target.exists():
        raise TransferError("output_exists", "Choose a new output filename; existing files are preserved.")
    temporary = None
    digest, count = hashlib.sha256(), 0
    try:
        with opener.open(urllib.request.Request(url, method="GET"), timeout=60) as response:
            if response.status != 200:
                raise TransferError("http_error", "Download did not succeed.", response.status)
            length = response.headers.get("Content-Length")
            if length is not None and (not length.isdigit() or int(length) > max_bytes):
                raise TransferError("download_too_large", "Download exceeds the local disk safety budget.")
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".blue-one-", delete=False) as destination:
                temporary = Path(destination.name)
                while chunk := response.read(CHUNK):
                    count += len(chunk)
                    if count > max_bytes:
                        raise TransferError("download_too_large", "Download exceeds the local disk safety budget.")
                    digest.update(chunk)
                    destination.write(chunk)
            if length is not None and count != int(length):
                raise TransferError("incomplete_download", "Download was interrupted; obtain a fresh URL for the same job.")
        # Atomic no-clobber publication on the same filesystem.
        os.link(temporary, target)
        return {"ok": True, "bytes": count, "sha256": digest.hexdigest(), "output": str(target)}
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def probe(expected_origin, opener):
    with opener.open(urllib.request.Request(expected_origin + "/health", method="GET"), timeout=15) as response:
        if response.status != 200 or json.loads(response.read(4096)).get("status") != "ok":
            raise TransferError("unexpected_response", "The execution environment did not receive the expected health response.")
    return {"ok": True, "stage": "network", "authenticated": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("probe", help="Check sandbox reachability, without consuming a transfer URL or authenticating.")
    up = commands.add_parser("upload")
    up.add_argument("--ticket", required=True)
    up.add_argument("--input", required=True)
    down = commands.add_parser("download")
    down.add_argument("--ticket", required=True)
    down.add_argument("--output", required=True)
    down.add_argument("--field", choices=["download_url", "docx_download_url"], default="download_url")
    down.add_argument("--max-bytes", type=int, default=DOWNLOAD_BUDGET, help="Client-local disk safety budget.")
    args = parser.parse_args(argv)
    try:
        expected = origin_from_plugin()
        opener = urllib.request.build_opener(NoRedirect())
        if args.command == "probe":
            result = probe(expected, opener)
        else:
            ticket = json.loads(Path(args.ticket).read_text())
            if not isinstance(ticket, dict):
                raise TransferError("invalid_ticket", "Save the tool's JSON object as the ticket.")
            if args.command == "upload":
                result = upload(ticket, args.input, expected, opener)
            else:
                result = download(ticket, args.field, args.output, expected, opener, args.max_bytes)
    except urllib.error.HTTPError as error:
        result = {"ok": False, "code": "http_error", "http_status": error.code, "message": "Request failed. Check the observed HTTP status before obtaining another ticket."}
    except (urllib.error.URLError, socket.timeout, TimeoutError, ssl.SSLError, http.client.HTTPException):
        result = {"ok": False, "code": "network_unreachable", "message": "The execution environment could not reach the MCP host. Check network access; no organization setting was inspected."}
    except TransferError as error:
        result = {"ok": False, "code": error.code, "message": error.message}
        if error.status is not None:
            result["http_status"] = error.status
    except (OSError, ValueError, KeyError, TypeError):
        result = {"ok": False, "code": "local_error", "message": "Check the ticket JSON, configuration, local paths, and file permissions."}
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
