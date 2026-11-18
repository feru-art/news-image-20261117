#!/usr/bin/env python3
"""The World — 17 November 2026 (V6 Dense F).

Entry for make.fun news-image-20261117: sums up the world's news of
Tuesday 17 November 2026 in one image. The program does not draw
anything — it copies the finished front page (generated with
Generate Image) from image.jpg beside this file to /output/entry.png,
after checking the bytes satisfy the competition gate:

  * a whole JPEG, SOI at the start and EOI at the end
  * at most 1 MiB and at most 1024 by 1024 pixels
  * deterministic: every run writes exactly the same bytes

Standard library only; no network access.
"""

import hashlib
import os
import sys

SOURCE_NAME = "image.jpg"
OUTPUT_NAME = "entry.png"
MAX_BYTES = 1_048_576
MAX_SIDE = 1024

SOI = b"\xff\xd8"          # JPEG start of image
EOI = b"\xff\xd9"          # JPEG end of image
# Start-of-frame markers that carry width/height (baseline + extended,
# excluding the DHT/DAC/JPGn markers that share the 0xC0-0xCF range).
SOF_MARKERS = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
               0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}


class GateError(Exception):
    """Raised when the image bytes fail the competition gate."""


def frame_size(payload):
    """Walk the JPEG marker segments and return (width, height).

    Skips standalone markers (RSTn, TEM) and reads each segment's
    declared length to jump to the next marker. Raises GateError when
    no start-of-frame segment is found before the scan data.
    """
    pos = 2  # past SOI
    end = len(payload)
    while pos + 1 < end:
        if payload[pos] != 0xFF:
            raise GateError("expected marker prefix 0xFF at offset %d" % pos)
        marker = payload[pos + 1]
        if marker == 0xDA:  # start of scan: frame data follows, stop here
            raise GateError("no start-of-frame segment before scan data")
        if marker == 0x01 or 0xD0 <= marker <= 0xD7:
            pos += 2  # standalone marker, no length field
            continue
        if pos + 4 > end:
            raise GateError("truncated segment header at offset %d" % pos)
        seg_len = (payload[pos + 2] << 8) | payload[pos + 3]
        if seg_len < 2 or pos + 2 + seg_len > end:
            raise GateError("segment overruns file at offset %d" % pos)
        if marker in SOF_MARKERS:
            if seg_len < 7:
                raise GateError("start-of-frame segment too short")
            height = (payload[pos + 5] << 8) | payload[pos + 6]
            width = (payload[pos + 7] << 8) | payload[pos + 8]
            return width, height
        pos += 2 + seg_len
    raise GateError("ran out of markers before a start-of-frame segment")


def check_payload(payload):
    """Validate the image bytes against the gate; return (w, h)."""
    if len(payload) > MAX_BYTES:
        raise GateError("image is %d bytes, over the 1 MiB cap"
                        % len(payload))
    if len(payload) < 4 or payload[:2] != SOI:
        raise GateError("missing JPEG start-of-image marker")
    if payload[-2:] != EOI:
        raise GateError("missing JPEG end-of-image marker")
    width, height = frame_size(payload)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise GateError("image is %dx%d, over the 1024x1024 cap"
                        % (width, height))
    return width, height


def output_path():
    """Where the entry goes: MAKEFUN_OUTPUT_DIR or /output."""
    base = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    return os.path.join(base, OUTPUT_NAME)


def emit():
    """Copy the validated image to the output path; report the result.

    After writing, the output file is read back and compared byte for
    byte with the validated payload, so a partial or corrupted write
    fails loudly instead of shipping a broken entry.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, SOURCE_NAME), "rb") as handle:
        payload = handle.read()
    width, height = check_payload(payload)
    target = output_path()
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "wb") as handle:
        handle.write(payload)
    with open(target, "rb") as handle:
        written = handle.read()
    if written != payload:
        raise GateError("read-back mismatch: output differs from source")
    digest = hashlib.sha256(payload).hexdigest()
    return {"bytes": len(payload), "width": width, "height": height,
            "sha256": digest, "path": target}


def main(argv):
    try:
        report = emit()
    except GateError as problem:
        print("gate failed: %s" % problem, file=sys.stderr)
        return 1
    except OSError as problem:
        print("io failed: %s" % problem, file=sys.stderr)
        return 1
    print("wrote %(path)s: %(bytes)d bytes, %(width)dx%(height)d, "
          "sha256 %(sha256)s" % report)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
