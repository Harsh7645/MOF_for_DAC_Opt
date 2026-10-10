"""Create corrected review archive offline; retain the original archive unchanged."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / 'evidence/qe75-fedora-completion-v5/launch02'


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    old = ROOT / 'artifacts/phase3/uio66_qe600_completion_v5_review.zip'
    target = old.with_name('uio66_qe600_completion_v5_review_v2.zip')
    assert digest(old) == '3dc362b2e6fb594e562402e569ea3c47f4f8b6c800c998339773a96c6228100c'
    assert json.loads((EV / 'assessment-v2.json').read_text())['ready_for_independent_assessment']
    extra = {}
    for name in ['assessment-v2.json', 'completed-SCF-pending-independent-assessment-v2.json',
                 'postflight-followup.json', 'reassessment-integrity.json',
                 'portable-review-receipt.json', 'finalization-complete.json']:
        extra['evidence/launch02/' + name] = EV / name
    for name in ['assess_qe75_completion_v5_v2.py', 'package_qe75_completion_v5_v2.py',
                 'assess_qe75_rho625_v1.py', 'qe75_fedora_v1.py', 'run_qe_water_pilot.py']:
        extra['controller/' + name] = ROOT / 'scripts' / name
    extra['REVIEW_REPORT.md'] = ROOT / 'docs/UIO66_QE75_FEDORA_COMPLETION_V5.md'
    extra['updated-execution-config.json'] = ROOT / 'configs/qe75-fedora-completion-v5.json'
    source = ROOT / 'local/qe75-fedora-v1/q-e-qe-7.5/PW/src/forces.f90'
    source_note = ('QE 7.5 PW/src/forces.f90; source SHA256 ' + digest(source) +
                   '\nExcerpt lines 348-409; total forces then verbose components:\n' +
                   '\n'.join(source.read_text().splitlines()[347:409]) + '\n').encode()
    sums = {}
    with zipfile.ZipFile(old) as original, zipfile.ZipFile(target, 'x', zipfile.ZIP_DEFLATED, compresslevel=3) as new:
        old_sums = json.loads(original.read('SHA256SUMS.json'))
        for item in original.infolist():
            if item.is_dir():
                continue
            name = item.filename
            outname = {'REVIEW_REPORT.md': 'original-automatic-REVIEW_REPORT.md',
                       'SHA256SUMS.json': 'original-automatic-SHA256SUMS.json'}.get(name, name)
            h = hashlib.sha256()
            with original.open(item) as src, new.open(outname, 'w', force_zip64=True) as dest:
                while chunk := src.read(1024 * 1024):
                    h.update(chunk)
                    dest.write(chunk)
            value = h.hexdigest()
            if name in old_sums:
                assert value == old_sums[name], name
            sums[outname] = value
        for name, path in extra.items():
            assert name not in sums, name
            new.write(path, name)
            sums[name] = digest(path)
        new.writestr('source/forces-excerpt.txt', source_note)
        sums['source/forces-excerpt.txt'] = hashlib.sha256(source_note).hexdigest()
        new.writestr('SHA256SUMS.json', json.dumps(sums, indent=2) + '\n')
    # Verify every archived payload, streaming to keep this offline audit small.
    with zipfile.ZipFile(target) as z:
        manifest = json.loads(z.read('SHA256SUMS.json'))
        assert set(z.namelist()) == set(manifest) | {'SHA256SUMS.json'}
        for name, expected in manifest.items():
            with z.open(name) as src:
                assert hashlib.file_digest(src, 'sha256').hexdigest() == expected, name
    receipt = {'archive': str(target.relative_to(ROOT)), 'sha256': digest(target),
               'size_bytes': target.stat().st_size, 'verified_payload_files': len(sums),
               'created_UTC': datetime.now(timezone.utc).isoformat(),
               'original_archive_unchanged': digest(old) == '3dc362b2e6fb594e562402e569ea3c47f4f8b6c800c998339773a96c6228100c',
               'scope': 'Offline parser correction and review packaging after terminal run; no new calculation or allocation.'}
    (EV / 'portable-review-v2-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    target.with_suffix('.zip.sha256').write_text(receipt['sha256'] + '  ' + target.name + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
