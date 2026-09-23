"""Check the shipping library through the codecs built against it."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

bindir = Path(sys.argv[1]).resolve()
ext = '.exe' if os.name == 'nt' else ''
base_env = {k: v for k, v in os.environ.items() if not k.startswith('OPJ_OPENCL_')}
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    pixels = bytes((x * 17 + y * 11 + c * 47) % 256 for y in range(256) for x in range(256) for c in range(3))
    source = root / 'input.ppm'
    source.write_bytes(b'P6\n256 256\n255\n' + pixels)
    results = []
    for mode in ('off', 'auto', 'missing'):
        env = base_env.copy()
        if mode != 'auto':
            selector = 'off' if mode == 'off' else '__no_such_device__'
            env.update(OPJ_OPENCL_DEVICE=selector, OPJ_OPENCL_ENCODE_DEVICE=selector)
        encoded = root / (mode + '.j2k')
        decoded = root / (mode + '.ppm')
        subprocess.run([str(bindir / ('opj_compress' + ext)), '-i', str(source), '-o', str(encoded)], env=env, check=True)
        subprocess.run([str(bindir / ('opj_decompress' + ext)), '-i', str(encoded), '-o', str(decoded)], env=env, check=True)
        assert decoded.read_bytes().endswith(pixels), mode + ': lossless pixel mismatch'
        results.append(encoded.read_bytes())
    assert results[0] == results[1] == results[2], 'automatic/fallback encoding differs from CPU'
print('PASS: automatic selection and missing-device fallback match native CPU; lossless pixels exact')
