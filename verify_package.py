"""Check the shipping library through the codecs built against it."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("bindir", type=Path)
parser.add_argument("--require-cuda", action="store_true", help="Require automatic CUDA selection on a local NVIDIA GPU")
args = parser.parse_args()
bindir = args.bindir.resolve()
ext = '.exe' if os.name == 'nt' else ''
base_env = {k: v for k, v in os.environ.items() if not k.startswith(('OPJ_OPENCL_', 'OPJ_CUDA_', 'OPJ_DECODE_'))}
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    pixels = bytes((x * 17 + y * 11 + c * 47) % 256 for y in range(256) for x in range(256) for c in range(3))
    source = root / 'input.ppm'
    source.write_bytes(b'P6\n256 256\n255\n' + pixels)
    results = []
    for mode in ('off', 'auto', 'missing', 'cuda-missing'):
        env = base_env.copy()
        if mode in ('off', 'missing'):
            selector = 'off' if mode == 'off' else '__no_such_device__'
            env.update(OPJ_OPENCL_DEVICE=selector, OPJ_OPENCL_ENCODE_DEVICE=selector)
        if mode == 'off':
            env['OPJ_DECODE_BACKEND'] = 'cpu'
        if mode == 'cuda-missing':
            env.update(OPJ_DECODE_BACKEND='cuda', OPJ_CUDA_DEVICE='__no_such_device__', OPJ_OPENCL_ENCODE_DEVICE='off')
        encoded = root / (mode + '.j2k')
        decoded = root / (mode + '.ppm')
        subprocess.run([str(bindir / ('opj_compress' + ext)), '-i', str(source), '-o', str(encoded)], env=env, check=True)
        result = subprocess.run([str(bindir / ('opj_decompress' + ext)), '-i', str(encoded), '-o', str(decoded)], env=env, check=True, capture_output=True, text=True)
        log = result.stdout + result.stderr
        print(log)
        if mode == 'auto' and args.require_cuda:
            assert 'CUDA decoded tile' in log, 'Automatic CUDA execution was not observed'
        if mode in ('off', 'missing', 'cuda-missing'):
            assert 'CUDA decoded tile' not in log and 'OpenCL decoded tile' not in log, 'Fallback unexpectedly used a GPU'
        assert decoded.read_bytes().endswith(pixels), mode + ': lossless pixel mismatch'
        results.append(encoded.read_bytes())
    assert all(result == results[0] for result in results), 'automatic/fallback encoding differs from CPU'
print('PASS: automatic selection and missing-device fallback match native CPU; lossless pixels exact')
