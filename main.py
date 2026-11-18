#!/usr/bin/env python3
"""news-image-20261117 — V6 Dense C entry.

The finished front page ("THE WORLD", Tuesday 17 November 2026: hero photo
of the burning Kerch Bridge, map label strip, six headline cards with icons,
and an 18-story list) was made with Generate Image and lives in this repo as
image.jpg. This program draws nothing: it checks the bundled JPEG against the
competition's output contract and copies it byte for byte to
/output/entry.png, so every run writes identical bytes.

Contract (RULES.txt): a whole PNG or JPEG, at most 1 MiB and at most
1024x1024 pixels; the file is told apart by its first bytes and the name
stays entry.png either way. No network is used anywhere.
"""

import hashlib
import os
import sys

SOURCE_NAME = "image.jpg"
TARGET_NAME = "entry.png"
MAX_BYTES = 1048576
MAX_EDGE = 1024
SOI = b"\xff\xd8"
EOI = b"\xff\xd9"
# Markers that carry a frame header with width/height (baseline + progressive).
FRAME_MARKERS = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
# Standalone markers: no length field follows them.
STANDALONE = {0x01, 0xD0, 0xD1, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9}


class JpegInspector:
    """Walks a JPEG byte string and reports its frame dimensions."""

    def __init__(self, blob):
        self.blob = blob
        self.pos = 0

    def _expect_soi(self):
        if self.blob[:2] != SOI:
            raise ValueError("not a JPEG: missing SOI marker")

    def _next_marker(self):
        """Return the next marker code after the current position."""
        blob, n = self.blob, len(self.blob)
        i = self.pos
        while i < n and blob[i] != 0xFF:
            i += 1
        if i + 1 >= n:
            raise ValueError("ran out of bytes looking for a marker")
        # Skip padding 0xFF bytes; the first non-0xFF byte is the code.
        while i < n and blob[i] == 0xFF:
            i += 1
        if i >= n:
            raise ValueError("ran out of bytes inside a marker")
        self.pos = i + 1
        return blob[i]

    def frame_size(self):
        """Return (width, height) from the first frame (SOF) segment."""
        self._expect_soi()
        self.pos = 2
        while True:
            code = self._next_marker()
            if code in FRAME_MARKERS:
                seg = self.blob[self.pos:self.pos + 7]
                if len(seg) < 7:
                    raise ValueError("truncated frame segment")
                height = (seg[3] << 8) | seg[4]
                width = (seg[5] << 8) | seg[6]
                return width, height
            if code == 0xDA:  # start of scan: no frame header before it
                raise ValueError("no frame segment before scan data")
            if code in STANDALONE:
                continue
            seg = self.blob[self.pos:self.pos + 2]
            if len(seg) < 2:
                raise ValueError("truncated segment length")
            self.pos += (seg[0] << 8) | seg[1]


def load_source():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, SOURCE_NAME)
    with open(path, "rb") as handle:
        return handle.read()


def check_contract(blob):
    """Validate the bundled image; return (width, height)."""
    if len(blob) > MAX_BYTES:
        raise ValueError("image is %d bytes, over the 1 MiB limit"
                         % len(blob))
    if blob[:2] != SOI or blob[-2:] != EOI:
        raise ValueError("image is not a whole JPEG (SOI/EOI check failed)")
    width, height = JpegInspector(blob).frame_size()
    if width > MAX_EDGE or height > MAX_EDGE:
        raise ValueError("image is %dx%d, over the 1024x1024 limit"
                         % (width, height))
    return width, height


def resolve_output_dir():
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def emit(blob, outdir):
    os.makedirs(outdir, exist_ok=True)
    target = os.path.join(outdir, TARGET_NAME)
    with open(target, "wb") as handle:
        handle.write(blob)
    with open(target, "rb") as handle:
        written = handle.read()
    if hashlib.sha256(written).hexdigest() != hashlib.sha256(blob).hexdigest():
        raise ValueError("read-back mismatch: output digest differs from source")
    return target


def self_test():
    """Validate the bundled image and report, without writing output."""
    blob = load_source()
    width, height = check_contract(blob)
    print("self-test OK: %dx%d, %d bytes, sha256 %s"
          % (width, height, len(blob), hashlib.sha256(blob).hexdigest()))
    return 0


def main(argv):
    if "--self-test" in argv:
        return self_test()
    blob = load_source()
    width, height = check_contract(blob)
    target = emit(blob, resolve_output_dir())
    digest = hashlib.sha256(blob).hexdigest()
    print("wrote %s (%dx%d, %d bytes, sha256 %s)"
          % (target, width, height, len(blob), digest))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
