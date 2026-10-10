"""Offline portable evidence checks. No scientific executables are invoked."""
from pathlib import Path
import tempfile
import unittest
from scripts.review_qe75_baseline14_portable import (
    BOHR_A, RY_EV, close_vectors, review, safe_member, total_forces,
)


class PortableReviewTests(unittest.TestCase):
    def test_safe_paths(self):
        self.assertEqual(str(safe_member('raw/job01/input.in')), 'raw/job01/input.in')
        for name in ('../bad', '/bad', 'C:/bad', 'raw\\bad', ''):
            with self.subTest(name=name), self.assertRaises(ValueError):
                safe_member(name)

    def test_total_force_block_excludes_components(self):
        text = '''Forces acting on atoms (cartesian axes, Ry/au):

 atom 1 type 2 force = 1.0D-3 0.0 -2.0E-3

 The non-local contribution
 atom 1 type 2 force = 9 9 9
'''
        self.assertEqual(total_forces(text), [(1, 2, [.001, 0, -.002])])

    def test_missing_and_duplicate_blocks_fail(self):
        header = 'Forces acting on atoms (cartesian axes, Ry/au):\n'
        for text in ('', header+header):
            with self.assertRaises(ValueError):
                total_forces(text)

    def test_units(self):
        self.assertAlmostEqual(2 * .001 * RY_EV / BOHR_A, .0514220674763, places=12)

    def test_nonfinite_and_mismatch_fail(self):
        for rows in ([[float('nan'),0,0]], [[float('inf'),0,0]], [[1,0,0]], [[0,0]], []):
            with self.assertRaises(ValueError):
                close_vectors(rows, [[0,0,0]], 5.1e-9, 'test')

    def test_corrupt_archive_fails_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'bad.zip').write_bytes(b'not the pinned archive')
            with self.assertRaisesRegex(ValueError, 'SHA256'):
                review(root/'bad.zip', root/'out')
            self.assertFalse((root/'out').exists())

    def test_pinned_archive_and_no_overwrite(self):
        archive = Path(__file__).resolve().parents[1]/'artifacts/phase3/uio66_qe_baseline14_review_v1.zip'
        self.assertTrue(archive.is_file(), 'The portable ZIP must travel with this commit')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = review(archive, root/'out', root/'extracted')
            self.assertEqual(result['payloads_verified'], 471)
            self.assertEqual(len(result['jobs']), 14)
            self.assertEqual(result['force_vectors'], 1717)
            self.assertEqual(len(result['differences']), 4)
            self.assertTrue((root/'out/forces.csv').is_file())
            self.assertTrue((root/'extracted/frozen-package/manifest.json').is_file())
            with self.assertRaises(FileExistsError):
                review(archive, root/'out')


if __name__ == '__main__':
    unittest.main()
