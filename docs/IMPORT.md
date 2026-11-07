# Evidence import — completed 2026-11-07

**Historical import succeeded.** The initial documentation was based on Codex session exports. The PS5 owner then ran the import script locally and pushed **179 text/source files** to GitHub in commit `58cd24c` (18,011 added lines). See [local-evidence/](../local-evidence/README.md). The connected GitHub app still cannot read the PS5 disk directly.

For possible **future additional imports only**, [`scripts/import-local-evidence.sh`](../scripts/import-local-evidence.sh) on the original PS5 Ubuntu host:

1. Checks the original project and a Git clone of this repo;
2. Copies only `*.md`, `*.patch`, `*.diff`, `*.py`, `*.c`, `*.cpp`, `*.h`, `*.sh` from `Diagnostics/` while rejecting `private/`, symlinks, logs, binary objects and huge files;
3. Exports the working Git source changes as a **text patch** (not a second entire upstream source tree);
4. Displays staged file names and runs a simple sensitivity scanner;
5. **Does not upload or push automatically**; the operator reviews the staged changes before publishing.

### Historical procedure (already completed)

```bash
git clone https://github.com/feraskozx1-byte/Fivem-linux.git "$HOME/Fivem-linux-archive"
cd "$HOME/Fivem-linux-archive"
bash scripts/import-local-evidence.sh
```

**Do not rerun this blindly:** the script refuses to overwrite an existing `local-evidence/` directory. Re-running requires deliberate new file review, not an automatic re-import. A private GitHub repository requires authorization.

For any **new**, reviewed import in a clean clone, the publishing step would be:

```bash
git diff --cached --stat
git diff --cached
git commit -m "archive: import reviewed local source patches and notes"
git push origin main
```

**Never commit** official FiveM security DLLs, game files, passwords, raw client tickets, full Wine prefixes or large crash dumps. Do not disable the scanner merely to get a clean result. If the script flags a source file, inspect/redact it before pushing.
