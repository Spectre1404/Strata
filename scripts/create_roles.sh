#!/usr/bin/env bash
# Create Strata custom roles in Atlas.
# Usage: bash scripts/create_roles.sh <PROJECT_ID>
set -euo pipefail
PID="$1"

# P ACTION coll1 coll2 ... -> ACTION@strata.coll1,ACTION@strata_test.coll1,...
P() { a=$1; shift; out=""; for c in "$@"; do for d in strata strata_test; do out="$out,$a@$d.$c"; done; done; echo "${out#,}"; }

R_FIND="research_bars universe sessions preregistrations trials trial_returns trial_groups audits policies"
R_INS="sessions preregistrations trials trial_returns blocked"

atlas customDbRoles create researcher --projectId "$PID" --privilege "$(P FIND $R_FIND),$(P INSERT $R_INS)"
atlas customDbRoles create auditor    --projectId "$PID" --privilege "FIND@strata,FIND@strata_test,$(P INSERT audits vault_openings blocked)"
atlas customDbRoles create strategist --projectId "$PID" --privilege "$(P FIND research_bars universe sessions trials trial_returns trial_groups audits policies),$(P INSERT policies)"
atlas customDbRoles create grouper    --projectId "$PID" --privilege "$(P FIND trials trial_returns trial_groups),$(P INSERT trial_groups),$(P UPDATE trial_groups)"
atlas customDbRoles create worker     --projectId "$PID" --privilege "$(P FIND $R_FIND requests),$(P INSERT $R_INS),$(P UPDATE requests),$(P CHANGE_STREAM requests)"
atlas customDbRoles create app        --projectId "$PID" --privilege "$(P FIND sessions preregistrations trials trial_groups audits vault_openings blocked policies requests),$(P INSERT requests),$(P CHANGE_STREAM trials audits blocked requests)"
