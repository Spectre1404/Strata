"""Tools the Researcher can call. Owner: Shiv (S5). Reviewer: Talal.

All tools connect with the researcher role.

query_research_bars(pipeline):
  - Prepend $match on ts within the research window.
  - Allowed stages: $match, $project, $addFields, $set, $setWindowFields, $group, $sort, $limit.
  - $setWindowFields windows must not reach forward (upper bound <= 0 or "current").
  - Forbidden: $out, $merge, $lookup, $unionWith, $graphLookup, $facet, $function, $accumulator.
  - Set maxTimeMS. On a rejected stage or a permission error, write to `blocked` and send blocked_query.
memory_stats(family=None): attempts so far (session, total, effective), best Sharpe, current bars.
similar_attempts(text, k=5): Vector Search on trial_groups.
preregister(text, family): insert into preregistrations before any data query.
backtest(pipeline, construction): causality check, then core.researcher.backtest.run.
"""
