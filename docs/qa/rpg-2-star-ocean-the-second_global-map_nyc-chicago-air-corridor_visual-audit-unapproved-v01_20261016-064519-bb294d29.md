# NYC–Chicago air corridor — Codex visual audit

**Status:** visual finding only; map art remains unapproved. I inspected the actual 1280×720 Godot captures `outputs/rpg-2-star-ocean-the-second_global-earth-map_us-great-lakes-chicago-air-route-card-en-runtime-capture_m2-v02_20261015-184808-49d78162.png`, `outputs/rpg-2-star-ocean-the-second_global-earth-map_us-northeast-en-runtime-capture_m2-v02_20261015-184808-49d78162.png`, and `outputs/rpg-2-star-ocean-the-second_global-earth-map_globe-en-runtime-capture_m2-v02_20261015-184808-49d78162.png`.

## One visual issue to resolve

When Chicago is selected, the Great Lakes view shows only the Chicago marker. The route card states “From: New York City” and “Air · Flight 1177.1 km · 6 h 5 min,” but the New York marker is outside the visible map and no connection appears on the map surface. The player can read the transport data yet cannot see the trip's direction or spatial span. The Northeast capture confirms the origin marker exists on another regional view; the globe capture contains both regional pins but still draws no connection between them.

**Next art pass:** while this route card is open, give the NYC→Chicago itinerary one clearly marked geographic connection. A restrained dashed air arc on the globe or a small two-endpoint route inset would preserve the current regional camera and route facts. Distinguish the air line from later road connections with a separate stroke/icon language. Keep underlying place coordinates, click targets, estimated time, and bilingual labels intact. Compare the same route-card view at 1280×720 and 640×360 before proposing it as a map-art candidate.

**Counter impact:** none. This note makes no runtime or acceptance change; M2 map art remains open and the MVP meter is unchanged.
