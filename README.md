# 3p-openjpeg

Autobuild packaging for VulkanStorm's [OpenJPEG fork](https://github.com/anne-skydancer/openjpeg), based on Second Life's package recipe.

The source submodule pins the CUDA decoder and existing OpenCL decoder/encoder acceleration work. Windows x64 ships `openjp2.dll` and its import library; Linux x64 ships `libopenjp2.a`. The package remains named `openjpeg`.

CUDA decoding is selected automatically on a compatible NVIDIA GPU. OpenCL acceleration remains automatic on other capable GPUs and for encoding. The driver is loaded dynamically; absent or unsuitable OpenCL devices fall back to native CPU OpenJPEG. No CUDA/OpenCL SDK or activation environment variable is needed on the user's machine. GPU execution is validated locally on NVIDIA Windows for CUDA and on AMD Windows for OpenCL; hosted CI verifies both platforms' CPU fallback, not GPU hardware compatibility.

Release builds retain precise floating-point behavior. Windows also uses link-time optimization. Development experiments and reference capture are excluded from the shipping library. Codec command-line tools are built for the CI roundtrip checks but are not packaged.

Each archive contains `SOURCE_REVISION.txt`, public headers, and the OpenJPEG BSD and bundled Khronos headers Apache-2.0 licenses. The Build workflow produces downloadable autobuild archives for Windows and Linux, checking automatic selection and missing-device fallback against native CPU lossless output.

## Build

Clone with submodules, install autobuild 3.9.3, and point `AUTOBUILD_VARIABLES_FILE` at a Second Life build-variables checkout. The recipe obtains a checksum-verified CUDA 12.9.1 compiler SDK for Windows/Linux x64 (no GPU driver installation). To reuse an SDK, set `OPJ_CUDA_ROOT` or `CUDA_PATH`. Then run:

```sh
autobuild build -A 64 -c Release --no-configure --id BUILD_ID
autobuild package -A 64 --archive-format tzst --archive-name ARCHIVE_NAME
```

Consumers install normally through `autobuild.xml`; no local package override is required.

On a local NVIDIA machine, `python verify_package.py openjpeg/bin/Release --require-cuda`
also verifies that default decoding actually uses CUDA. Linux uses `openjpeg/build/bin`.
Hosted Windows/Linux CI verifies CPU fallback without requiring GPU hardware and
includes the compiled CUDA kernels in both package formats.
