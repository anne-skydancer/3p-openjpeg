# 3p-openjpeg

Autobuild packaging for VulkanStorm's [OpenJPEG fork](https://github.com/anne-skydancer/openjpeg), based on Second Life's package recipe.

The source submodule pins the merged decoder and encoder acceleration work. Windows x64 ships `openjp2.dll` and its import library; Linux x64 ships `libopenjp2.a`. The package remains named `openjpeg`.

OpenCL acceleration is enabled automatically on capable GPU devices, irrespective of vendor. The driver is loaded dynamically; absent or unsuitable OpenCL devices fall back to native CPU OpenJPEG. No OpenCL SDK or activation environment variable is needed on the user's machine. GPU execution is validated locally on AMD Windows; hosted CI verifies both platforms' CPU fallback, not GPU hardware compatibility.

Release builds retain precise floating-point behavior. Windows also uses link-time optimization. Development experiments and reference capture are excluded from the shipping library. Codec command-line tools are built for the CI roundtrip checks but are not packaged.

Each archive contains `SOURCE_REVISION.txt`, public headers, and the OpenJPEG BSD and bundled Khronos headers Apache-2.0 licenses. The Build workflow produces downloadable autobuild archives for Windows and Linux, checking automatic selection and missing-device fallback against native CPU lossless output.

## Build

Clone with submodules, install autobuild 3.9.3, and point `AUTOBUILD_VARIABLES_FILE` at a Second Life build-variables checkout. Then run:

```sh
autobuild build -A 64 -c Release --no-configure --id BUILD_ID
autobuild package -A 64 --archive-format tzst --archive-name ARCHIVE_NAME
```

Consumers install normally through `autobuild.xml`; no local package override is required.
