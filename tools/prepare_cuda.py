"""Assemble a local CUDA 12.9 compiler SDK; never install or modify GPU drivers."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import tarfile
import urllib.request
import zipfile

BASE = "https://developer.download.nvidia.com/compute/cuda/redist/"
VERSION = "12.9.1"

def prepare(root, target):
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(BASE + "redistrib_" + VERSION + ".json") as response:
        manifest = json.load(response)
    sdk = root / "sdk"
    for name in ("cuda_nvcc", "cuda_cudart", "cuda_cccl"):
        item = manifest[name][target]
        archive = root / Path(item["relative_path"]).name
        if not archive.exists() or hashlib.sha256(archive.read_bytes()).hexdigest() != item["sha256"]:
            temporary = archive.with_suffix(archive.suffix + ".download")
            urllib.request.urlretrieve(BASE + item["relative_path"], temporary)
            if hashlib.sha256(temporary.read_bytes()).hexdigest() != item["sha256"]:
                raise RuntimeError("CUDA archive checksum mismatch: " + name)
            temporary.replace(archive)
        extracted = root / (name + "-" + manifest[name]["version"] + "-" + target)
        marker = extracted / ".complete"
        if not marker.exists():
            extracted.mkdir(exist_ok=True)
            if archive.suffix == ".zip":
                with zipfile.ZipFile(archive) as bundle:
                    for member in bundle.infolist():
                        if not (extracted / member.filename).resolve().is_relative_to(extracted):
                            raise RuntimeError("Unsafe archive path")
                    bundle.extractall(extracted)
            else:
                with tarfile.open(archive) as bundle:
                    bundle.extractall(extracted, filter="data")
            marker.touch()
        directories = [p for p in extracted.iterdir() if p.is_dir()]
        if len(directories) != 1:
            raise RuntimeError("Unexpected CUDA archive layout")
        shutil.copytree(directories[0], sdk, dirs_exist_ok=True, symlinks=True)
    return sdk

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--platform", choices=("windows-x86_64", "linux-x86_64"))
    args = parser.parse_args()
    target = args.platform or ("windows-x86_64" if os.name == "nt" else "linux-x86_64")
    if platform.machine().lower() not in ("amd64", "x86_64"):
        parser.error("The package SDK requires an x86-64 build host")
    print(prepare(args.output, target).as_posix())
