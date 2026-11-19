# CPU-only AVX2 OpenJPEG packages

Windows x64 and Linux x86_64 packages use AVX2 CPU decoding and encoding. CUDA and OpenCL backends are explicitly disabled; no GPU SDK is required. These packages require AVX2-capable processors. The macOS viewer package pin remains separate.

Windows ships openjp2.dll and its import library; Linux ships libopenjp2.a. Existing Autobuild layouts and the openjpeg package name are retained. Release builds preserve precise floating-point behavior and Windows LTO. Codec tools verify the shipping library before packaging. BUILD_POLICY.txt records the intended backend and ISA; SOURCE_REVISION.txt identifies the source.

The measured AVX2 improvement over SSE2 was small and workload-dependent; this package does not claim a viewer FPS improvement. GPU backends cannot be re-enabled at runtime through environment variables.

The source is the fork's `vkstorm-2.5.4-hotfix` line: OpenJPEG 2.5.4 (fork `3b1a6a96`) with six decoder fixes. Complete codestreams decode bit for bit as before. Cut codestreams keep every complete codeword segment, also with EPH markers and with a last tile-part of Psot = 0. The decoder no longer visits packets after a tile's data ends, rejects an invalid reduce factor without changing its state, allocates tile parameters only for tiles that appear, and decodes 9/7 tiles that vanish at the decoded resolution. A new additive API, `opj_decoder_limits_init()` with `opj_decoder_set_limits()` (`OPJ_HAVE_DECODER_LIMITS`), bounds what a header can make the decoder allocate; `OPJ_DECODER_LIMITS_SL_TEXTURE` is the Second Life texture profile. Without limits, a decoder behaves as before.
