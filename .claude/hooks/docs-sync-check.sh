#!/usr/bin/env bash
# Golden-rule guard (see CLAUDE.md): when code changes, the planning docs must change in the
# same session. This Stop hook nudges when backend/ or frontend/src/ changed but none of
# prd.md / spec.md / implementation.md did. It only nudges — you can still finish by updating
# the docs or confirming none is needed.
#
# Fires at most once per stop-chain (guarded by stop_hook_active) so it never loops.

input=$(cat)

# Avoid nag-loops: if this Stop was already re-triggered by a prior hook block, let it pass.
if printf '%s' "$input" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

# New-side path of every pending change (strip the 2 status chars + space; take rename target).
changed=$(git status --porcelain 2>/dev/null | sed 's/^...//; s/.* -> //')

code=$(printf '%s\n' "$changed" | grep -E '^(backend/|frontend/src/)' || true)
docs=$(printf '%s\n' "$changed" | grep -E '^(prd|spec|implementation)\.md$' || true)

if [ -n "$code" ] && [ -z "$docs" ]; then
  echo "Golden rule (CLAUDE.md): code under backend/ or frontend/src/ changed this session, but" >&2
  echo "prd.md / spec.md / implementation.md were not updated. Update the relevant doc(s) to match" >&2
  echo "the code change (or state explicitly that none is needed) before finishing." >&2
  exit 2
fi

exit 0
