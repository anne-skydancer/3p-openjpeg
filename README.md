# CPU-only AVX2 OpenJPEG packages

Windows x64 and Linux x86_64 packages use AVX2 CPU decoding and encoding. CUDA and OpenCL backends are explicitly disabled; no GPU SDK is required. These packages require AVX2-capable processors. The macOS viewer package pin remains separate.

Windows ships openjp2.dll and its import library; Linux ships libopenjp2.a. Existing Autobuild layouts and the openjpeg package name are retained. Release builds preserve precise floating-point behavior and Windows LTO. Codec tools verify the shipping library before packaging. BUILD_POLICY.txt records the intended backend and ISA; SOURCE_REVISION.txt identifies the source.

The measured AVX2 improvement over SSE2 was small and workload-dependent; this package does not claim a viewer FPS improvement. GPU backends cannot be re-enabled at runtime through environment variables.
