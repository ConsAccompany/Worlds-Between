# Private Site v18: canon character labels (operational QA receipt)

Date: 2026-10-18. This is an operational record only. It accepts no art and changes no gate. The counters are unchanged: 40.8%, M2 10/12, scenes 3/12, sprites 0/52, playtests 0/2, formal acceptance false.

## Deployment (as reported by root)

- **Deployed source:** private Site source revision `1296f66b04a9a51aa71d7c4a29340e1f34310dfe`.
- **Deployment:** `appgdep_6ad4c068d41881919a4bf34ed075a21f`, status SUCCEEDED.
- **Live production UI check (root, about 08:50 local):**
  - the character filter shows the canon labels: **Culture (文化) lists 11** characters and **portal planet lists 7**;
  - reset shows all **51** identities;
  - searching the canon label "Culture" works;
  - inventory captions were checked: 33 Culture mappings and 21 portal-planet mappings.
- **Data unchanged:**
  - The change is label-only. The mapping from displayed label to stored raw value is unchanged (the raw character data still stores the pre-decision board labels; the UI maps them).
  - All underlying data is unchanged.
  - The private Site audience is unchanged.

## Public-safe proof

`outputs/rpg-2-star-ocean-the-second_cloud-tracker_canon-character-labels-complete-live-proof_v18_20261018-085430-d1a493f8.jpg`
- byte-exact copy of root's screenshot;
- sha256 `61e9c9c851b4e173df190ea86d6b1a9e6d7f8f1fe6625933d17c391f3e48e93e`, 187,874 bytes.

Note: the file content is a JPEG (2104×1244). Root delivered it with a wrong `.png` extension, and 43ba56f first committed it under that name. It has since been renamed to `.jpg` with the same bytes; the image itself was not edited.

Claude inspected the image. It shows the production 角色 (Characters) tab:
- the sync bar reads "GitHub 已同步 · 160b823 · 8:54:11 AM";
- the badge reads "51 份档案";
- the sphere filter is set to **文化** and lists exactly 11 entries, each captioned "文化 · …": 09 娜丽娅, 10 伊赛, 11 赛恩, 12 达伽, 22 阿维拉, 23 克恩, 24 莱芮, 39 席妲, 40 顾鳞, 41 瑞玛, 42 陶粒;
- the selected card is labelled "主线伙伴 · 文化".

The portal-planet count (7), the reset count (51 listed), the search check and the inventory caption counts are root's live observations; this image does not show them. The image contains no account, credential, budget or session data.

## Not included

- No private Site source, controller, credential, deployment log, account or budget data.
- No Site URL.
- The private Site checkout was not touched.
