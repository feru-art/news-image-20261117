"""news-image-20261117 V5 (slot 2) — magazine-cover entry.

Writes the bundled V5 image ("THE WORLD" magazine cover: hero shot of the
Kerch Bridge burning, plus Hormuz, summit and jets thumbnails, dated
17 NOVEMBER 2026) to /output/entry.png.

Deterministic: the output is a byte-for-byte copy of the bundled JPEG.
No network, no randomness, no timestamps, standard library only.
The image was made with Generate Image via Milku; this program only
copies its finished bytes to the output path.
"""

import hashlib
import os
import sys

IMAGE_NAME = "image.jpg"
OUTPUT_NAME = "entry.png"
MAX_BYTES = 1024 * 1024
MAX_SIDE = 1024

JPEG_SOI = b"\xff\xd8"
JPEG_EOI = b"\xff\xd9"


def bundled_image_path():
    """Absolute path of the image bundled next to this script."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, IMAGE_NAME)


def output_path():
    """Where the harness collects the entry image."""
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    return os.path.join(out_dir, OUTPUT_NAME)


def jpeg_dimensions(data):
    """Read width/height from a JPEG's first SOF marker (SOF0/SOF2).

    Walks the marker segments; raises ValueError if no frame header
    is found or the stream is truncated.
    """
    pos = 2  # skip the SOI marker
    while pos + 4 <= len(data):
        if data[pos] != 0xFF:
            raise ValueError("bad marker at offset %d" % pos)
        marker = data[pos + 1]
        if marker == 0xD9:  # EOI before any frame header
            break
        if marker in (0xC0, 0xC2):  # SOF0 / SOF2: precision, height, width
            height = int.from_bytes(data[pos + 5:pos + 7], "big")
            width = int.from_bytes(data[pos + 7:pos + 9], "big")
            return width, height
        size = int.from_bytes(data[pos + 2:pos + 4], "big")
        if size < 2:
            raise ValueError("bad segment size at offset %d" % pos)
        pos += 2 + size
    raise ValueError("no JPEG frame header found")


def validate_image(data):
    """Check the bundled bytes against the competition's image gate."""
    if len(data) > MAX_BYTES:
        raise ValueError("image over 1 MiB: %d bytes" % len(data))
    if not data.startswith(JPEG_SOI):
        raise ValueError("image does not start with the JPEG SOI marker")
    if not data.endswith(JPEG_EOI):
        raise ValueError("image is missing its JPEG end marker")
    width, height = jpeg_dimensions(data)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError("image too large: %dx%d" % (width, height))
    return width, height


def main():
    source = bundled_image_path()
    with open(source, "rb") as handle:
        data = handle.read()
    width, height = validate_image(data)

    dest = output_path()
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as handle:
        handle.write(data)

    # Post-write verification: re-read what landed on disk and prove it
    # is byte-for-byte the validated image before reporting success, so a
    # truncated or partial write can never pass as a good run.
    with open(dest, "rb") as handle:
        written = handle.read()
    if written != data:
        raise ValueError("written output differs from the bundled image")

    digest = hashlib.sha256(written).hexdigest()
    print("wrote %s (%d bytes, %dx%d JPEG, sha256 %s)"
          % (dest, len(data), width, height, digest))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        print("error: %s" % error, file=sys.stderr)
        sys.exit(1)
