#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "ContractFin-research/0.1"


def request_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        value = json.load(response)
    if not isinstance(value, dict):
        raise ValueError(f"expected object from {url}")
    return value


def resolve_commit(repository: str, ref: str) -> str:
    encoded_ref = urllib.parse.quote(ref, safe="")
    value = request_json(f"https://api.github.com/repos/{repository}/commits/{encoded_ref}")
    sha = value.get("sha")
    if not isinstance(sha, str) or len(sha) < 7:
        raise ValueError(f"could not resolve {repository}@{ref}")
    return sha


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def atomic_write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def download(url: str) -> tuple[bytes, dict[str, str]]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        headers = {
            "etag": response.headers.get("ETag", ""),
            "last_modified": response.headers.get("Last-Modified", ""),
            "content_type": response.headers.get("Content-Type", ""),
        }
        return response.read(), headers


def build_manifest(config: dict[str, Any], root: Path, force: bool) -> dict[str, Any]:
    sources: list[dict[str, Any]] = []
    for source in config["sources"]:
        dataset = source["dataset"]
        repository = source["repository"]
        commit = source.get("commit") or resolve_commit(repository, source.get("ref", "main"))
        files: list[dict[str, Any]] = []
        for relative in source["files"]:
            encoded_path = "/".join(urllib.parse.quote(part, safe="") for part in relative.split("/"))
            url = f"https://raw.githubusercontent.com/{repository}/{commit}/{encoded_path}"
            target = root / "data" / "raw" / dataset / relative
            if target.exists() and not force:
                value = target.read_bytes()
                headers: dict[str, str] = {}
            else:
                value, headers = download(url)
                atomic_write_bytes(target, value)
            files.append(
                {
                    "path": relative,
                    "local_path": str(target.relative_to(root)),
                    "url": url,
                    "bytes": len(value),
                    "sha256": sha256_bytes(value),
                    "http": headers,
                }
            )
        sources.append(
            {
                "dataset": dataset,
                "repository": repository,
                "requested_ref": source.get("ref", "main"),
                "resolved_commit": commit,
                "license_note": source.get("license_note"),
                "files": files,
            }
        )
    return {
        "manifest_version": config.get("manifest_version", 1),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "financebench_pdfs": {
            "status": "deferred",
            "reason": "Bulk PDF acquisition requires a separate storage and license check.",
        },
    }


def restore_from_manifest(manifest: dict[str, Any], root: Path, force: bool) -> dict[str, Any]:
    restored = json.loads(json.dumps(manifest))
    for source in restored["sources"]:
        for item in source["files"]:
            target = root / item["local_path"]
            if target.exists() and not force:
                value = target.read_bytes()
                if sha256_bytes(value) == item["sha256"]:
                    continue
            value, headers = download(item["url"])
            actual = sha256_bytes(value)
            if actual != item["sha256"]:
                raise ValueError(f"hash mismatch for {item['url']}: {actual} != {item['sha256']}")
            atomic_write_bytes(target, value)
            item["http"] = headers
    restored["restored_at"] = datetime.now(timezone.utc).isoformat()
    return restored


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze ContractFin benchmark sources")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "config" / "data_sources.json")
    parser.add_argument("--from-manifest", type=Path)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.from_manifest:
            manifest = restore_from_manifest(
                json.loads(args.from_manifest.read_text(encoding="utf-8")), root, args.force
            )
        else:
            config = json.loads(args.config.read_text(encoding="utf-8"))
            manifest = build_manifest(config, root, args.force)
    except urllib.error.URLError as exc:
        raise SystemExit(f"network error while freezing datasets: {exc}") from exc
    output = root / "data" / "dataset_manifest.json"
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    for source in manifest["sources"]:
        byte_count = sum(item["bytes"] for item in source["files"])
        print(f"{source['dataset']}: {len(source['files'])} files, {byte_count} bytes, {source['resolved_commit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
