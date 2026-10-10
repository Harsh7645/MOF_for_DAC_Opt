"""Verify the pinned v2 ZIP and safely extract a NEW directory; no compute launch."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile

ZIP_SHA = '4ea11e147c529d8b893d2131c06812ec5978b24f0c7d8905c116c22e4e6d0554'
MANIFEST_SHA = '716b281245bee302cc6cb574c0e724aaf2dcec66a5480d34ae52893c47b21032'


def extract(archive, receipt, destination):
    if destination.exists():raise FileExistsError('Preserve existing extraction')
    data=archive.read_bytes();meta=json.loads(receipt.read_text())
    if hashlib.sha256(data).hexdigest()!=ZIP_SHA or meta['zip_sha256']!=ZIP_SHA:
        raise ValueError('Pinned ZIP mismatch')
    with zipfile.ZipFile(archive) as z:
        raw=z.read('file_hashes.json')
        if hashlib.sha256(raw).hexdigest()!=MANIFEST_SHA or meta['hash_manifest_sha256']!=MANIFEST_SHA:
            raise ValueError('Pinned hash manifest mismatch')
        hashes=json.loads(raw)
        if len(hashes)!=140 or meta['verified_file_count']!=140:raise ValueError('Expected 140 files')
        if set(z.namelist())!=set(hashes)|{'file_hashes.json'} or len(z.namelist())!=141:
            raise ValueError('Unexpected or duplicate members')
        for entry in z.infolist():
            path=PurePosixPath(entry.filename)
            if path.is_absolute() or '..' in path.parts or '\\' in entry.filename or ':' in entry.filename or stat.S_ISLNK(entry.external_attr>>16):
                raise ValueError('Unsafe archive member')
            content=z.read(entry)
            if entry.filename in hashes and hashlib.sha256(content).hexdigest()!=hashes[entry.filename]:
                raise ValueError('Member checksum mismatch')
        destination.mkdir()
        for entry in z.infolist():
            target=destination/entry.filename;target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as out:out.write(z.read(entry))
        for name,expected in hashes.items():
            if hashlib.sha256((destination/name).read_bytes()).hexdigest()!=expected:raise ValueError('Extracted hash mismatch')
    return {'zip_sha256':ZIP_SHA,'verified_files':140,'created_directory':str(destination.resolve()),
            'directories_created':[str(destination.resolve())]+[str(p.resolve()) for p in sorted(destination.rglob('*')) if p.is_dir()],
            'status':'verified extraction; no SCF'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--zip',type=Path,required=True)
    p.add_argument('--receipt',type=Path,required=True);p.add_argument('--destination',type=Path,required=True)
    a=p.parse_args();print(json.dumps(extract(a.zip,a.receipt,a.destination),indent=2))
