#!/usr/bin/env bash
# Conservative *local* evidence staging only. Nothing is pushed automatically.
set -euo pipefail

PROJECT="${FIVEM_PROJECT:-$HOME/Projects/FiveM-PR4050-Test}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$HERE/local-evidence"

if ! git -C "$HERE" rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "ERROR: run inside a clone of the archival GitHub repository" >&2; exit 1
fi
if [[ ! -d "$PROJECT/Diagnostics" ]]; then
  echo "ERROR: expected diagnostics not found: $PROJECT/Diagnostics" >&2; exit 1
fi
if [[ -e "$OUT" ]]; then
  echo "ERROR: $OUT already exists; review existing staged files instead of overwriting" >&2; exit 1
fi

mkdir -p "$OUT/Diagnostics"
count=0
while IFS= read -r -d '' f; do
  rel="${f#"$PROJECT"/}"
  # Reject symlinks, sensitive subtrees, too-large sources, and all non-allowlisted types.
  [[ ! -L "$f" ]] || continue
  case "/$rel/" in
    *"/private/"*|*"/prefix/"*|*"/drive_c/"*|*"/secrets/"*) continue;;
  esac
  case "$rel" in
    *.md|*.patch|*.diff|*.py|*.c|*.cpp|*.h|*.sh) ;;
    *) continue;;
  esac
  # Limit each text file to 512 KiB; avoid memory dumps disguised as text.
  (( $(stat -c '%s' -- "$f") <= 524288 )) || continue
  # Reject NUL-containing binary files.
  if LC_ALL=C grep -qU $'\x00' -- "$f" 2>/dev/null; then
    # grep with NUL pattern is not portable; the file/type checks below are authoritative.
    :
  fi
  case "$(file --mime-type -b "$f")" in
    text/*|application/x-shellscript|application/x-python-code|application/json) ;;
    *) continue;;
  esac
  mkdir -p "$OUT/$(dirname "$rel")"
  cp -- "$f" "$OUT/$rel"
  count=$((count+1))
done < <(find "$PROJECT/Diagnostics" -type f -print0)

if [[ -f "$PROJECT/PR-4050.patch" ]]; then
  cp -- "$PROJECT/PR-4050.patch" "$OUT/PR-4050.patch"
fi
SOURCE="$PROJECT/Original-PR4050-Source"
if [[ -d "$SOURCE/.git" ]]; then
  git -C "$SOURCE" diff --no-ext-diff --no-textconv -- . ':!*.dll' ':!*.exe' > "$OUT/local-source-working-tree.patch"
  git -C "$SOURCE" diff --cached --no-ext-diff --no-textconv -- . ':!*.dll' ':!*.exe' > "$OUT/local-source-index.patch"
fi

git -C "$HERE" add -- local-evidence/
echo "Staged $count diagnostic source/text files (plus available source patches)."
git -C "$HERE" diff --cached --check
git -C "$HERE" diff --cached --stat

# Heuristic warnings, not a guarantee that data is safe.
if git -C "$HERE" diff --cached -U0 | grep -Eina   '(ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|authorization:[[:space:]]*bearer|password[[:space:]]*[:=]|access_token[[:space:]]*[:=]|client_secret[[:space:]]*[:=])'; then
  echo "WARNING: Possible secrets found in staged material. Review/redact; DO NOT PUSH yet." >&2
  exit 2
fi

echo
echo "READY FOR MANUAL REVIEW. NO COMMIT AND NO PUSH PERFORMED."
echo "Inspect: git diff --cached"
echo "If safe: git commit -m 'archive: import reviewed patches and notes' && git push origin main"
