#!/usr/bin/env python3

import hashlib
import os
import argparse
import unittest
import shutil

def sha256sum(filename):
    """Calculate SHA256 sum of a file."""
    try:
        with open(filename, "rb") as f:
            h = hashlib.sha256()
            while True:
                data = f.read(4096)
                if not data:
                    break
                h.update(data)
            return h.hexdigest()
    except FileNotFoundError:
        print(f"sha256sum: {filename}: No such file or directory")
        return None
    except OSError as e:
        print(f"sha256sum: {filename}: {e}")
        return None

def tree_sha256(dirpath, output_dir):
    """Generate SHA256 tree for a directory."""
    try:
        for root, _, files in os.walk(dirpath):
            rel_root = os.path.relpath(root, dirpath)
            out_dir = os.path.join(output_dir, rel_root)
            os.makedirs(out_dir, exist_ok=True)
            for file in files:
                filepath = os.path.join(root, file)
                sha = sha256sum(filepath)
                if sha:
                    with open(os.path.join(out_dir, file + ".sha256"), "w") as f:
                        f.write(sha + "\n")
        return True
    except OSError as e:
        print(f"tree_sha256: {dirpath}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate SHA256 tree for directories.")
    parser.add_argument("dirs", nargs="+", help="Directories to process")
    parser.add_argument("-o", "--output", default=".", help="Output directory")
    args = parser.parse_args()

    for dirpath in args.dirs:
        if not tree_sha256(dirpath, args.output):
            print(f"Failed to process {dirpath}")

class TestTreeSha256(unittest.TestCase):
    def setUp(self):
        self.test_dir1 = "test_dir1"
        self.test_dir2 = "test_dir2"
        self.output_dir = "test_output"

        os.makedirs(self.test_dir1, exist_ok=True)
        os.makedirs(os.path.join(self.test_dir1, "subdir"), exist_ok=True)
        with open(os.path.join(self.test_dir1, "file1.txt"), "w") as f:
            f.write("test content 1")
        with open(os.path.join(self.test_dir1, "subdir", "file2.txt"), "w") as f:
            f.write("test content 2")

        os.makedirs(self.test_dir2, exist_ok=True)
        with open(os.path.join(self.test_dir2, "file1.txt"), "w") as f:
            f.write("test content 1")
        with open(os.path.join(self.test_dir2, "file3.txt"), "w") as f:
            f.write("different content")

        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir1)
        shutil.rmtree(self.test_dir2)
        shutil.rmtree(self.output_dir)

    def test_tree_sha256(self):
        self.assertTrue(tree_sha256(self.test_dir1, self.output_dir))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, self.test_dir1, "file1.txt.sha256")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, self.test_dir1, "subdir", "file2.txt.sha256")))

if __name__ == "__main__":
    if 'unittest' in sys.argv[0]:
        unittest.main()
    else:
        main()
