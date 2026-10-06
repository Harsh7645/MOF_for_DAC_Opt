"""Offline guard tests; no scientific executable or real geometry is run."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts import qe75_fedora_v1 as fedora


class FedoraPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.patch = patch.object(fedora, 'ROOT', self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def fixture(self):
        package = self.root / 'package'
        package.mkdir()
        (package / 'input.in').write_text('synthetic fixture, not a QE input\n')
        (package / 'file_hashes.json').write_text(json.dumps({'input.in': fedora.sha(package / 'input.in')}))
        archive = self.root / 'release.zip'
        with zipfile.ZipFile(archive, 'w') as z:
            for p in package.iterdir():
                z.write(p, 'release/' + p.name)
        (self.root / 'receipt.json').write_text(json.dumps({
            'zip_sha256': fedora.sha(archive),
            'manifest': {'sha256': fedora.sha(package / 'file_hashes.json')}}))
        return {'package': 'package', 'archive': 'release.zip', 'receipt': 'receipt.json',
                'archive_sha256': fedora.sha(archive), 'expected_package_files': 1}

    def test_archive_and_unpacked_files_verified(self):
        self.assertEqual(fedora.verify_package(self.fixture())['verified_files'], 1)

    def test_unpacked_tamper_rejected(self):
        config = self.fixture()
        (self.root / 'package/input.in').write_text('tamper')
        with self.assertRaisesRegex(ValueError, 'Unpacked release mismatch'):
            fedora.verify_package(config)

    def test_wrong_receipt_pin_rejected(self):
        config = self.fixture()
        (self.root / 'receipt.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'Receipt does not pin'):
            fedora.verify_package(config)

    def test_missing_release_never_invokes_process(self):
        config = self.fixture()
        (self.root / 'release.zip').unlink()
        with patch.object(fedora.subprocess, 'run', side_effect=AssertionError('must not run')):
            with self.assertRaisesRegex(ValueError, 'missing'):
                fedora.stage(config)

    def test_missing_executable_never_invokes_process(self):
        with patch.object(fedora.subprocess, 'run', side_effect=AssertionError('must not run')):
            with self.assertRaisesRegex(ValueError, 'Executable absent'):
                fedora.software({'pw_executable': 'absent', 'ompi_prterun': 'absent', 'mpi_runtime_bin': 'absent'})

    def test_only_expected_empty_input_error_is_startup_evidence(self):
        output = 'Program PWSCF v.7.5\nError in routine read_namelists (2):\ncould not find namelist &control'
        self.assertTrue(fedora.expected_empty_input_startup(1, output))
        for changed in (output.replace('7.5', '7.4'), output + '\nsocket() failed',
                        output + '\nError in routine other (1)', output + '\niteration # 1'):
            self.assertFalse(fedora.expected_empty_input_startup(1, changed))
        self.assertFalse(fedora.expected_empty_input_startup(0, output))


if __name__ == '__main__':
    unittest.main()
