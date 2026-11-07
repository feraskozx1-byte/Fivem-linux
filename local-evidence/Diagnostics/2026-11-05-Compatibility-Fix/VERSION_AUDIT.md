# VERSION AUDIT — 2026-11-05

253 root-level PE files inspected across the three runtime directories and the official reference. Resources/debug directories read without execution; SHA256 only for principal files. Full per-file data, timestamps, CodeView IDs and FXCOMPONENT JSON are in versions.json.

## Identity and provenance

| File | Set | PE FileVersion | COFF UTC if timestamp | SHA256 | Provenance evidence |
| --- | --- | --- | --- | --- | --- |
| CitizenGame.dll | Run-Adhesive-Test | 1.0.0.1 | 2026-11-04T12:46:27+00:00 | `5d448df8690a2321a042b7ca69f7b792a8e4a726233818f53be11ee11fb69431` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| CoreRT.dll | Run-Adhesive-Test | 1.0.0.1 | 2026-11-04T12:32:43+00:00 | `b38ab16c25c9bf72b537e9e1acfef5411a0939d6289c953f28b4ac2358fc8013` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| FiveM.exe | Run-Adhesive-Test | 2.0.0.1 | 2026-11-04T13:02:12+00:00 | `0f70ea0ee9ccdcf83bdebacf588722770bc0a28c95ce19ee1dc5575344c9819f` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| adhesive.dll | Run-Adhesive-Test | 1.0.0.24769 | 2026-01-22T11:08:54+00:00 | `3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b` | Matches provided official-reference SHA256; prior signature/digest check; original download/build manifest unavailable |
| citizen-resources-core.dll | Run-Adhesive-Test | 1.0.0.1 | 2026-11-04T12:51:58+00:00 | `6ee7a4130769883056c61f6ea43212377eb2397a35850ad3501424c240d58935` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| http-client.dll | Run-Adhesive-Test | 1.0.0.1 | 2026-11-04T12:50:34+00:00 | `8ea79cb41d8713893a08750309ca8f9061a762b5d023fe21afdc798a315d323d` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| legitimacy.dll | Run-Adhesive-Test | 1.0.0.1 | 2026-02-05T12:31:53+00:00 | `b15f1101d89aeb84e308fbe4dd7d8888d8c2c6c36474954dc184ad4c766fa0e5` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| net-base.dll | Run-Adhesive-Test | 1.0.0.1 | 2026-11-04T12:38:30+00:00 | `ac33fefb3c403f8c2a249ad492f92aa0e507ea7842515285580515af32aa1b64` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| net-tcp-server.dll | Run-Adhesive-Test | 1.0.0.1 | 2026-11-04T12:43:27+00:00 | `92a835bff2261da1e2e7c268faa3a1d7f3c8fd270405b8736e72a24a5868a5a8` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| node.dll | Run-Adhesive-Test | 1.0.0.1 | 2026-11-04T12:56:28+00:00 | `8c284e1412659dcdd6133ce9ce7cc0d5301b4e5a899d119ff8fb349b954126b6` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| sticky.dll | Run-Adhesive-Test | 1.0.0.1 | 2026-11-04T12:39:07+00:00 | `9dc92655c0accec04718abd63ce6e0c5764a552e95d5cc8d3a2c9200daa4fc2b` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| v8-9.3.345.16.dll | Run-Adhesive-Test | not present | 2021-07-13T23:34:00+00:00 | `ae1ebbfc9d6e351803ed0b5b43cbdbc30ab7e78f7a9f93615958514563b5b0d5` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| vfs-core.dll | Run-Adhesive-Test | 1.0.0.1 | 2026-11-04T12:47:50+00:00 | `a81cafa7390fd730cfb943d22afd431dff3a844a691c527bcb3ccb2f7e55519b` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| CitizenGame.dll | Run-CoreRT-Test | 1.0.0.1 | 2026-11-04T12:46:27+00:00 | `5d448df8690a2321a042b7ca69f7b792a8e4a726233818f53be11ee11fb69431` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| CoreRT.dll | Run-CoreRT-Test | 1.0.0.1 | 2026-11-05T11:40:03+00:00 | `cd9f91d57fc15d8c2180eeb7e85040bd035a13861e7641c81d484abe84eb4d64` | CI42019993897 validation.json SHA256 and CodeView match; base commit ba07d9d plus recorded local patches |
| FiveM.exe | Run-CoreRT-Test | 2.0.0.1 | 2026-11-04T13:02:12+00:00 | `0f70ea0ee9ccdcf83bdebacf588722770bc0a28c95ce19ee1dc5575344c9819f` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| citizen-resources-core.dll | Run-CoreRT-Test | 1.0.0.1 | 2026-11-04T12:51:58+00:00 | `6ee7a4130769883056c61f6ea43212377eb2397a35850ad3501424c240d58935` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| http-client.dll | Run-CoreRT-Test | 1.0.0.1 | 2026-11-04T12:50:34+00:00 | `8ea79cb41d8713893a08750309ca8f9061a762b5d023fe21afdc798a315d323d` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| legitimacy.dll | Run-CoreRT-Test | 1.0.0.1 | 2026-02-05T12:31:53+00:00 | `b15f1101d89aeb84e308fbe4dd7d8888d8c2c6c36474954dc184ad4c766fa0e5` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| net-base.dll | Run-CoreRT-Test | 1.0.0.1 | 2026-11-04T12:38:30+00:00 | `ac33fefb3c403f8c2a249ad492f92aa0e507ea7842515285580515af32aa1b64` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| net-tcp-server.dll | Run-CoreRT-Test | 1.0.0.1 | 2026-11-04T12:43:27+00:00 | `92a835bff2261da1e2e7c268faa3a1d7f3c8fd270405b8736e72a24a5868a5a8` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| node.dll | Run-CoreRT-Test | 1.0.0.1 | 2026-11-04T12:56:28+00:00 | `8c284e1412659dcdd6133ce9ce7cc0d5301b4e5a899d119ff8fb349b954126b6` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| sticky.dll | Run-CoreRT-Test | 1.0.0.1 | 2026-11-04T12:39:07+00:00 | `9dc92655c0accec04718abd63ce6e0c5764a552e95d5cc8d3a2c9200daa4fc2b` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| v8-9.3.345.16.dll | Run-CoreRT-Test | not present | 2021-07-13T23:34:00+00:00 | `ae1ebbfc9d6e351803ed0b5b43cbdbc30ab7e78f7a9f93615958514563b5b0d5` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| vfs-core.dll | Run-CoreRT-Test | 1.0.0.1 | 2026-11-04T12:47:50+00:00 | `a81cafa7390fd730cfb943d22afd431dff3a844a691c527bcb3ccb2f7e55519b` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| CitizenGame.dll | Compiled-Release | 1.0.0.1 | 2026-11-04T12:46:27+00:00 | `5d448df8690a2321a042b7ca69f7b792a8e4a726233818f53be11ee11fb69431` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| CoreRT.dll | Compiled-Release | 1.0.0.1 | 2026-11-04T12:32:43+00:00 | `b38ab16c25c9bf72b537e9e1acfef5411a0939d6289c953f28b4ac2358fc8013` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| FiveM.exe | Compiled-Release | 2.0.0.1 | 2026-11-04T13:02:12+00:00 | `0f70ea0ee9ccdcf83bdebacf588722770bc0a28c95ce19ee1dc5575344c9819f` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| citizen-resources-core.dll | Compiled-Release | 1.0.0.1 | 2026-11-04T12:51:58+00:00 | `6ee7a4130769883056c61f6ea43212377eb2397a35850ad3501424c240d58935` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| http-client.dll | Compiled-Release | 1.0.0.1 | 2026-11-04T12:50:34+00:00 | `8ea79cb41d8713893a08750309ca8f9061a762b5d023fe21afdc798a315d323d` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| legitimacy.dll | Compiled-Release | 1.0.0.1 | 2026-02-05T12:31:53+00:00 | `b15f1101d89aeb84e308fbe4dd7d8888d8c2c6c36474954dc184ad4c766fa0e5` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| net-base.dll | Compiled-Release | 1.0.0.1 | 2026-11-04T12:38:30+00:00 | `ac33fefb3c403f8c2a249ad492f92aa0e507ea7842515285580515af32aa1b64` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| net-tcp-server.dll | Compiled-Release | 1.0.0.1 | 2026-11-04T12:43:27+00:00 | `92a835bff2261da1e2e7c268faa3a1d7f3c8fd270405b8736e72a24a5868a5a8` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| node.dll | Compiled-Release | 1.0.0.1 | 2026-11-04T12:56:28+00:00 | `8c284e1412659dcdd6133ce9ce7cc0d5301b4e5a899d119ff8fb349b954126b6` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| sticky.dll | Compiled-Release | 1.0.0.1 | 2026-11-04T12:39:07+00:00 | `9dc92655c0accec04718abd63ce6e0c5764a552e95d5cc8d3a2c9200daa4fc2b` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| v8-9.3.345.16.dll | Compiled-Release | not present | 2021-07-13T23:34:00+00:00 | `ae1ebbfc9d6e351803ed0b5b43cbdbc30ab7e78f7a9f93615958514563b5b0d5` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| vfs-core.dll | Compiled-Release | 1.0.0.1 | 2026-11-04T12:47:50+00:00 | `a81cafa7390fd730cfb943d22afd431dff3a844a691c527bcb3ccb2f7e55519b` | Byte identity with Compiled-Release baseline; exact source/toolchain provenance unavailable |
| adhesive-24769.dll | Official-Reference | 1.0.0.24769 | 2026-01-22T11:08:54+00:00 | `3ba9e52b06a2af3d5f748d83129899afa2d38b644b5a79feb129ba3af958556b` | Matches provided official-reference SHA256; prior signature/digest check; original download/build manifest unavailable |

## Conclusions with evidence

- Principal binaries compared across the three sets are byte-identical except the rebuilt CoreRT and the additional official Adhesive in Run-Adhesive-Test. This is identity evidence, not proof of compatibility with a particular private ABI.
- Run-CoreRT-Test and Compiled-Release have no adhesive.dll. Their components.json still requests adhesive; the existing source manifest fallback can therefore choose Sticky. No files were supplied/replaced by this audit.
- The embedded FXCOMPONENT for official Adhesive declares name=adhesive, semantic version=0.1.0 and dependencies including fx[2], rage:device, gta:core, net, vfs:core and other FiveM components. Sticky also declares0.1.0, which does not make it an equivalent security implementation.
- All nonoptional declared dependencies resolve against the inspected manifests plus built-in fx[2]/platform:windows. See FxGameComponent.cpp:36-44, ComponentLoader.cpp:247-285, ComponentId.cpp:46-61. vendor/legitimacy categories are exempted by the existing source resolver; they must not be reported as missing DLLs merely from those manifest labels.
- This static coverage does not verify PE import semantics, C++ object layouts, vtables, allocator ownership, initialization ordering or private Adhesive ABI. The prior direct-import audit is separate.
- PE versions1.0.0.1 for local components use CI_PIPELINE_ID default1 (code/tools/gen_rc.py:9,18-19). Adhesive1.0.0.24769 alone is NOT evidence of an ABI mismatch. Semantic manifest versions are different data.
- COFF timestamps above are header values interpreted as UTC only if not IMAGE_DEBUG_TYPE_REPRO. They are not authenticated build dates. Version, embedded PDB path, or equal timestamp cannot establish exact source provenance.
- Source is shallow wine-proton-fix at ba07d9d3d5bd8459b69a81c69eb6065d4e11273c with preexisting local edits. Existing CI validation names four source hashes; these can validate that targeted CoreRT build, not the origin of the whole Compiled-Release set.
- Confirmed stale debugging file: Run-CoreRT-Test/dbg/CoreRT.pdb GUID8B792D8E… does not match new DLL GUIDD93B51AE… age1. Correct artifact PDB exists in Diagnostics/2026-11-05-Compatibility/ci-citicore/downloaded-build/citicore-x64-42019993897. Phase2/CoreRT-PDB-validation.txt records both; no PDB was replaced here.
- No complete release/BOM or approved private ABI matrix is available. Overall compatibility of this mixed local-build/reference set cannot be certified. Cfx.re must identify the approved host/component build set for Adhesive SHA2563ba9e52b…58556b.

## Reproduce

```bash
python3 Diagnostics/2026-11-05-Compatibility-Fix/audit-versions.py
```

The audit reads only source/runtime files and writes versions.json and its own diagnostic Git snapshot. It does not mutate product files.
