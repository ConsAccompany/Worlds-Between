# Private Bible v25: offline bootstrap and live verification

Published privately from Site source6d45f4eb4fb9c4b8aeb5fc4c6ac29e44abe8cba2, deploymentappgdep_6ad53fd75e908191b381af0edf9f20fb. Native deployment status succeeded. Audience/authentication unchanged.

The homepage previously blanked while project APIs failed; a separate read showed Cloudflare1102 resource limits. New build renders the exact bundled03e0572 public-project snapshot immediately with a non-live label. Network refreshes are8s bounded/coalesced, failure retries back off60/120/240/300s; no redundant10s polling or private-record dependency. Failed reads retain usable data, successful reads restore live provenance and preserve view/search/focus. Playing media defers re-rendering. No server resource-limit cause or permanent server fix is claimed.

All8 targeted checks passed, including actual Bible VM offline/hanging/recovery and normal-playing-media regressions. Root independently reran snapshot/current-candidate checks and reviewed the code before publishing. Exact frozen data blob pins are checked; Chicago v06 replacesv05 at rank6 andv05 remains pinned in history; other10current cards unchanged.

Root reloaded the actual private homepage, selected Production and visibly verified liveGitHub986b27b76d2c5521452f93fc9dad713b1c6d6445: production51.0%, coding100%, content18.3%, inspection13.2%, creatorapproval7%, formalacceptancefalse. The separate compact-panel connector opened successfully and its refreshed metadata returned the same liveSHA/productionLive=true. Thus reads recovered during this observation; the underlying earlier1102 is not diagnosed as permanently resolved.

Actual screenshot: `outputs/rpg-2-star-ocean-the-second_cloud-tracker_workflow-live-production_v25_20261018-175405-94e389d3.jpg`.

No acceptance counters changed: environments3/12, fullsprites0/52, humanplays0/2. No cloud credits, Claude calls, account changes or new schedules.
