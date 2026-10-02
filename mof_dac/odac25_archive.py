"""Bounded streaming extraction for official ODAC25 tar archives."""

import argparse
import hashlib
import json
import tarfile
import urllib.request
from pathlib import Path, PurePosixPath


class _LimitedReader:
    def __init__(self, source, limit):
        self.source, self.limit, self.bytes_read = source, limit, 0

    def read(self, size=-1):
        remaining = self.limit - self.bytes_read
        if remaining < 0:
            raise RuntimeError("Archive scan exceeded byte limit")
        requested = remaining + 1 if size < 0 else min(size, remaining + 1)
        data = self.source.read(requested)
        self.bytes_read += len(data)
        if self.bytes_read > self.limit:
            raise RuntimeError("Archive scan exceeded byte limit")
        return data


def extract_first_database(stream, prefix, output, *, max_scan_bytes,
                           max_member_bytes=10 * 1024**3):
    """Stream to the first regular ``.aselmdb`` under prefix and extract it."""
    if max_scan_bytes <= 0 or max_member_bytes <= 0:
        raise ValueError("byte limits must be positive")
    prefix = prefix.strip("/")
    if not prefix or ".." in PurePosixPath(prefix).parts:
        raise ValueError("prefix must be a safe relative archive path")
    output = Path(output)
    reader = _LimitedReader(stream, max_scan_bytes)
    selected = None
    try:
        with tarfile.open(fileobj=reader, mode="r|gz") as archive:
            for member in archive:
                if not member.name.startswith(prefix + "/") or not member.name.endswith(".aselmdb"):
                    continue
                path = PurePosixPath(member.name)
                if path.is_absolute() or ".." in path.parts or not member.isfile():
                    raise ValueError(f"Unsafe archive member: {member.name}")
                if member.size > max_member_bytes:
                    raise RuntimeError(f"Member exceeds byte limit: {member.size}")
                source = archive.extractfile(member)
                if source is None:
                    raise RuntimeError(f"Cannot read archive member: {member.name}")
                destination = output.joinpath(*path.parts)
                destination.parent.mkdir(parents=True, exist_ok=True)
                temporary = destination.with_suffix(destination.suffix + ".part")
                digest = hashlib.sha256()
                try:
                    with source, temporary.open("wb") as sink:
                        while chunk := source.read(8 * 1024 * 1024):
                            digest.update(chunk)
                            sink.write(chunk)
                    temporary.replace(destination)
                finally:
                    temporary.unlink(missing_ok=True)
                selected = {"archive_path": member.name,
                            "local_path": str(destination),
                            "size_bytes": member.size,
                            "sha256": digest.hexdigest()}
                break
    except tarfile.TarError as error:
        raise RuntimeError(f"Invalid or incomplete tar archive: {error}") from error
    if selected is None:
        raise ValueError(f"No .aselmdb member found under {prefix}")
    return {"prefix": prefix, "compressed_bytes_read": reader.bytes_read,
            "selected": selected}


def stream_extract(url, prefix, output, manifest, *, max_scan_gb=20,
                   max_member_gb=10, timeout=300):
    if max_scan_gb <= 0 or max_member_gb <= 0:
        raise ValueError("size limits must be positive")
    with urllib.request.urlopen(url, timeout=timeout) as response:
        result = extract_first_database(
            response, prefix, output,
            max_scan_bytes=int(max_scan_gb * 1024**3),
            max_member_bytes=int(max_member_gb * 1024**3),
        )
    result["archive_url"] = url
    path = Path(manifest)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--prefix", default="val/mof_plus_adsorbate")
    parser.add_argument("--output", default="data/raw/odac25")
    parser.add_argument("--manifest", default="artifacts/odac25/archive_member.json")
    parser.add_argument("--max-scan-gb", type=float, default=20)
    parser.add_argument("--max-member-gb", type=float, default=10)
    args = parser.parse_args()
    result = stream_extract(args.url, args.prefix, args.output, args.manifest,
                            max_scan_gb=args.max_scan_gb,
                            max_member_gb=args.max_member_gb)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
