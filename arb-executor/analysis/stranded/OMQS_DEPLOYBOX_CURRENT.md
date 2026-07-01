# OMQS — CURRENT DEPLOY-BOX TRADE REVIEW (player-by-player)

**Deploy box:** Jun 30 15:46 ET bisect-flip → Jul 1 18:40 ET (config unchanged across the disk-crash gap + restart — one box). Read-only, assumptions vs tape.

**Scope:** 88 legs the bot touched (posted ≥1), across 48 events.


## KXATPCHALLENGERMATCH-26JUL01GIUTOP  [ATP_CHALL]

### GIU  (KXATPCHALLENGERMATCH-26JUL01GIUTOP-GIU)
- **timeline:** 01:40 post 47c x5 (resting) | 02:05 **FILL 47c x5 v4_resting_maker** | 02:05 exit_post 57c
- **entry grade:** assumption cell=47 target_bid=47c | tape premkt last_trade min/med/max = 46/48/49c (n=787) | book-at-post @01:40 bid47/ask48; @01:40 bid47/ask48
  → **FILL 47c**: vs target 47 (0c), tape-position **mid-3rd**
- **outcome:** OPEN

### TOP  (KXATPCHALLENGERMATCH-26JUL01GIUTOP-TOP)
- **timeline:** 00:00 post 53c x5 (resting)
- **entry grade:** assumption cell=53 target_bid=53c | tape premkt last_trade min/med/max = 54/54/55c (n=744) | book-at-post @00:00 bid53/ask54; @00:00 bid53/ask54
- **outcome:** settled LOSS pnl=$0.0

**PAIR:** posted 2 legs; filled 1.
  → ONE-SIDED. kept=GIU, missed=TOP class=**NO_OPP** | catchable sibling dedup opps: none

## KXATPCHALLENGERMATCH-26JUL01HEIBAR  [ATP_CHALL]

### BAR  (KXATPCHALLENGERMATCH-26JUL01HEIBAR-BAR)
- **timeline:** 00:00 post 19c x5 (resting) | 00:02 cancel [v4_move_repost] | 00:02 post 20c x5 (resting) | 03:40 cancel [v4_t20m_fallback] | 03:40 post 20c x5 (resting) | 03:53 **FILL 20c x5 v4_fallback_maker** | 03:53 exit_post 26c
- **entry grade:** assumption cell=20 target_bid=19c | tape premkt last_trade min/med/max = 19/22/22c (n=6859) | book-at-post @00:00 bid20/ask21; @03:40 bid20/ask21
  → **FILL 20c**: vs target 19 (+1c), tape-position **mid-3rd**
- **mechanical:** v4_t20m_fallback@03:40 ; would_skip_walled x1
- **outcome:** OPEN

### HEI  (KXATPCHALLENGERMATCH-26JUL01HEIBAR-HEI)
- **timeline:** 00:23 post 79c x5 (resting) | 02:26 cancel [v4_move_repost] | 02:26 post 80c x5 (resting) | 03:40 cancel [v4_t20m_fallback] | 03:40 post 81c x5 (resting) | 03:42 cancel [v4_move_repost] | 03:42 post 80c x5 (resting) | 03:44 cancel [v4_t20m_fallback] | 03:44 post 80c x5 (resting) | 03:55 cancel [v4_move_repost] | 03:55 post 81c x5 (resting) | 03:57 cancel [v4_t20m_fallback] | 03:57 post 81c x5 (resting)
- **entry grade:** assumption cell=79 target_bid=79c | tape premkt last_trade min/med/max = 80/81/81c (n=7097) | book-at-post @00:23 bid79/ask80; @03:57 bid81/ask82
- **mechanical:** v4_t20m_fallback@03:40 ; v4_t20m_fallback@03:44 ; v4_t20m_fallback@03:57 ; would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

**PAIR:** posted 2 legs; filled 1.
  → ONE-SIDED. kept=BAR, missed=HEI class=**NO_OPP** | catchable sibling dedup opps: none

## KXATPCHALLENGERMATCH-26JUL01KAOMOE  [ATP_CHALL]

### KAO  (KXATPCHALLENGERMATCH-26JUL01KAOMOE-KAO)
- **timeline:** 03:00 post 25c x5 (resting)
- **entry grade:** assumption cell=25 target_bid=25c | tape premkt last_trade min/med/max = 25/25/25c (n=11) | book-at-post @03:00 bid25/ask27; @03:00 bid25/ask27
- **mechanical:** would_skip_walled x1
- **outcome:** settled LOSS pnl=$0.0

### MOE  (KXATPCHALLENGERMATCH-26JUL01KAOMOE-MOE)
- **timeline:** 03:00 post 73c x5 (resting)
- **entry grade:** assumption cell=73 target_bid=73c | tape premkt last_trade min/med/max = 73/73/75c (n=1195) | book-at-post @03:00 bid73/ask75; @03:00 bid73/ask75
- **mechanical:** would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

**PAIR:** posted 2 legs; filled 0.
  → MISSED BOTH (posted, no fill)

## KXATPCHALLENGERMATCH-26JUL01KASSAN  [ATP_CHALL]

### KAS  (KXATPCHALLENGERMATCH-26JUL01KASSAN-KAS)
- **timeline:** 23:37 post 56c x5 (resting) | 02:11 cancel [v4_move_repost] | 02:11 post 59c x5 (resting) | 02:34 cancel [v4_move_repost] | 02:34 post 60c x5 (resting) | 03:11 cancel [v4_t20m_fallback] | 03:11 post 60c x5 (resting)
- **entry grade:** assumption cell=56 target_bid=56c | tape premkt last_trade min/med/max = 56/70/81c (n=10302) | book-at-post @23:37 bid56/ask57; @03:11 bid61/ask61
- **mechanical:** v4_t20m_fallback@03:11 ; would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

### SAN  (KXATPCHALLENGERMATCH-26JUL01KASSAN-SAN)
- **timeline:** 23:37 post 42c x5 (resting) | 01:05 **FILL 42c x5 v4_resting_maker** | 01:05 exit_post 51c
- **entry grade:** assumption cell=42 target_bid=42c | tape premkt last_trade min/med/max = 21/28/43c (n=10851) | book-at-post @23:37 bid42/ask43; @23:37 bid42/ask43
  → **FILL 42c**: vs target 42 (0c), tape-position **EXPENSIVE-3rd**
- **mechanical:** would_skip_walled x1
- **outcome:** OPEN

**PAIR:** posted 2 legs; filled 1.
  → ONE-SIDED. kept=SAN, missed=KAS class=**PULLED** | catchable sibling dedup opps: 20:34 ~56c x22; 03:42 ~62c x48; 03:45 ~62c x10

## KXATPCHALLENGERMATCH-26JUL01MIDGUE  [ATP_CHALL]

### GUE  (KXATPCHALLENGERMATCH-26JUL01MIDGUE-GUE)
- **timeline:** 23:30 post 42c x5 (resting) | 03:15 **FILL 42c x5 v4_resting_maker** | 03:15 exit_post 51c
- **entry grade:** assumption cell=42 target_bid=42c | tape premkt last_trade min/med/max = 39/45/50c (n=23207) | book-at-post @23:30 bid42/ask44; @23:30 bid42/ask44
  → **FILL 42c**: vs target 42 (0c), tape-position **CHEAP-3rd**
- **outcome:** OPEN

### MID  (KXATPCHALLENGERMATCH-26JUL01MIDGUE-MID)
- **timeline:** 02:00 post 57c x5 (resting) | 02:11 cancel [v4_move_repost] | 02:11 post 58c x5 (resting) | 02:42 cancel [v4_move_repost] | 02:42 post 59c x5 (resting) | 02:44 **FILL 59c x5 v4_resting_maker** | 02:44 exit_post 76c
- **entry grade:** assumption cell=58 target_bid=57c | tape premkt last_trade min/med/max = 50/56/62c (n=27504) | book-at-post @02:00 bid58/ask58; @02:42 bid59/ask60
  → **FILL 59c**: vs target 57 (+2c), tape-position **EXPENSIVE-3rd**
- **outcome:** OPEN

**PAIR:** posted 2 legs; filled 2.
  → BOTH FILLED, combined = 42+59 = **101c [>100]**

## KXATPCHALLENGERMATCH-26JUL01NEDRON  [ATP_CHALL]

### NED  (KXATPCHALLENGERMATCH-26JUL01NEDRON-NED)
- **timeline:** 00:30 post 66c x5 (resting) | 01:28 **FILL 66c x5 v4_resting_maker** | 01:28 exit_post 85c
- **entry grade:** assumption cell=67 target_bid=66c | tape premkt last_trade min/med/max = 65/73/81c (n=21248) | book-at-post @00:30 bid66/ask67; @00:30 bid66/ask67
  → **FILL 66c**: vs target 66 (0c), tape-position **CHEAP-3rd**
- **mechanical:** would_skip_walled x1
- **outcome:** OPEN

### RON  (KXATPCHALLENGERMATCH-26JUL01NEDRON-RON)
- **timeline:** 23:30 post 34c x5 (resting) | 01:15 **FILL 34c x5 v4_engagement_join** | 01:16 exit_post 42c
- **entry grade:** assumption cell=34 target_bid=34c | tape premkt last_trade min/med/max = 20/29/36c (n=23713) | book-at-post @23:30 bid34/ask36; @23:30 bid34/ask36
  → **FILL 34c**: vs target 34 (0c), tape-position **EXPENSIVE-3rd**
- **outcome:** OPEN

**PAIR:** posted 2 legs; filled 2.
  → BOTH FILLED, combined = 66+34 = **100c [98-100]**

## KXATPCHALLENGERMATCH-26JUL01PASDAL  [ATP_CHALL]

### DAL  (KXATPCHALLENGERMATCH-26JUL01PASDAL-DAL)
- **timeline:** 01:32 post 43c x5 (resting) | 03:01 cancel [v4_move_repost] | 03:01 post 46c x5 (resting) | 03:03 cancel [v4_move_repost] | 03:03 post 47c x5 (resting)
- **entry grade:** assumption cell=43 target_bid=43c | tape premkt last_trade min/med/max = 44/46/48c (n=574) | book-at-post @01:32 bid43/ask44; @03:03 bid47/ask48
- **mechanical:** would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

### PAS  (KXATPCHALLENGERMATCH-26JUL01PASDAL-PAS)
- **timeline:** 01:48 post 55c x5 (resting)
- **entry grade:** assumption cell=55 target_bid=55c | tape premkt last_trade min/med/max = 55/56/56c (n=936) | book-at-post @01:48 bid55/ask56; @01:48 bid55/ask56
- **mechanical:** would_skip_walled x1
- **outcome:** settled LOSS pnl=$0.0

**PAIR:** posted 2 legs; filled 0.
  → MISSED BOTH (posted, no fill)

## KXATPCHALLENGERMATCH-26JUL01RINERH  [ATP_CHALL]

### ERH  (KXATPCHALLENGERMATCH-26JUL01RINERH-ERH)
- **timeline:** 03:00 post 42c x5 (resting)
- **entry grade:** assumption cell=44 target_bid=42c | tape premkt last_trade min/med/max = 46/46/46c (n=123) | book-at-post @03:00 bid44/ask45; @03:00 bid44/ask45
- **outcome:** settled LOSS pnl=$0.0

### RIN  (KXATPCHALLENGERMATCH-26JUL01RINERH-RIN)
- **timeline:** 03:00 post 59c x5 (resting)
- **entry grade:** assumption cell=59 target_bid=59c | tape premkt last_trade min/med/max = 56/57/60c (n=555) | book-at-post @03:00 bid59/ask60; @03:00 bid59/ask60
- **outcome:** settled WIN pnl=$0.0

**PAIR:** posted 2 legs; filled 0.
  → MISSED BOTH (posted, no fill)

## KXATPCHALLENGERMATCH-26JUL01SMISQU  [ATP_CHALL]

### SMI  (KXATPCHALLENGERMATCH-26JUL01SMISQU-SMI)
- **timeline:** 01:28 post 28c x5 (resting) | 02:24 cancel [v4_move_repost] | 02:24 post 29c x5 (resting) | 03:03 cancel [v4_move_repost] | 03:03 post 31c x5 (resting)
- **entry grade:** assumption cell=28 target_bid=28c | tape premkt last_trade min/med/max = 28/30/32c (n=1218) | book-at-post @01:28 bid28/ask29; @03:03 bid31/ask32
- **mechanical:** would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

### SQU  (KXATPCHALLENGERMATCH-26JUL01SMISQU-SQU)
- **timeline:** 01:17 post 71c x5 (resting) | 03:03 **FILL 71c x5 v4_resting_maker** | 03:03 exit_post 90c
- **entry grade:** assumption cell=71 target_bid=71c | tape premkt last_trade min/med/max = 69/70/73c (n=686) | book-at-post @01:17 bid71/ask72; @01:17 bid71/ask72
  → **FILL 71c**: vs target 71 (0c), tape-position **mid-3rd**
- **mechanical:** would_skip_walled x1
- **outcome:** OPEN

**PAIR:** posted 2 legs; filled 1.
  → ONE-SIDED. kept=SQU, missed=SMI class=**PULLED** | catchable sibling dedup opps: 17:52 ~28c x39

## KXATPCHALLENGERMATCH-26JUL01STAMAR  [ATP_CHALL]

### MAR  (KXATPCHALLENGERMATCH-26JUL01STAMAR-MAR)
- **timeline:** 02:10 post 62c x5 (resting)
- **entry grade:** assumption cell=62 target_bid=62c | tape premkt last_trade min/med/max = 62/63/63c (n=1489) | book-at-post @02:10 bid62/ask63; @02:10 bid62/ask63
- **mechanical:** would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

### STA  (KXATPCHALLENGERMATCH-26JUL01STAMAR-STA)
- **timeline:** 02:10 post 36c x5 (resting)
- **entry grade:** assumption cell=36 target_bid=36c | tape premkt last_trade min/med/max = 37/39/40c (n=677) | book-at-post @02:10 bid36/ask37; @02:10 bid36/ask37
- **mechanical:** would_skip_walled x1
- **outcome:** settled LOSS pnl=$0.0

**PAIR:** posted 2 legs; filled 0.
  → MISSED BOTH (posted, no fill)

## KXATPCHALLENGERMATCH-26JUN30BARFIC  [ATP_CHALL]

### BAR  (KXATPCHALLENGERMATCH-26JUN30BARFIC-BAR)
- **timeline:** 15:47 post 58c x5 (resting) | 21:17 cancel [match_live_cancel]
- **entry grade:** assumption cell=58 target_bid=58c | tape premkt last_trade min/med/max = 59/63/66c (n=7996) | book-at-post @15:47 bid58/ask59; @15:47 bid58/ask59
- **mechanical:** would_skip_walled x1
- **outcome:** determined (ws)

### FIC  (KXATPCHALLENGERMATCH-26JUN30BARFIC-FIC)
- **timeline:** 15:47 post 40c x5 (resting) | 18:09 **FILL 42c x3 v4_reconciled** | 18:09 exit_post 51c | 21:26 exit_fill 51c pnl$0.27 | 21:26 exit_post 51c
- **entry grade:** assumption cell=40 target_bid=40c | tape premkt last_trade min/med/max = 33/39/44c (n=6862) | book-at-post @15:47 bid40/ask41; @15:47 bid40/ask41
  → **FILL 42c**: vs target 40 (+2c), tape-position **EXPENSIVE-3rd**
- **outcome:** determined (ws), exit_fill pnl=$0.27

**PAIR:** posted 2 legs; filled 1.
  → ONE-SIDED. kept=FIC, missed=BAR class=**TOO_DEEP** | catchable sibling dedup opps: 20:07 ~60c x500; 21:13 ~59c x23

## KXATPCHALLENGERMATCH-26JUN30ELLSEK  [ATP_CHALL]

### ELL  (KXATPCHALLENGERMATCH-26JUN30ELLSEK-ELL)
- **timeline:** 15:47 post 42c x5 (resting) | 18:18 **FILL 42c x5 v4_resting_maker** | 18:18 exit_post 51c | 20:07 exit_fill 51c pnl$0.45
- **entry grade:** assumption cell=43 target_bid=42c | tape premkt last_trade min/med/max = 28/44/99c (n=38629) | book-at-post @15:47 bid43/ask44; @15:47 bid43/ask44
  → **FILL 42c**: vs target 42 (0c), tape-position **CHEAP-3rd**
- **outcome:** determined (ws), exit_fill pnl=$0.45

### SEK  (KXATPCHALLENGERMATCH-26JUN30ELLSEK-SEK)
- **timeline:** 15:47 post 57c x5 (resting) | 17:49 **FILL 57c x5 v4_resting_maker** | 17:49 exit_post 73c | 19:50 exit_fill 73c pnl$0.8
- **entry grade:** assumption cell=58 target_bid=57c | tape premkt last_trade min/med/max = 1/42/73c (n=34835) | book-at-post @15:47 bid57/ask58; @15:47 bid57/ask58
  → **FILL 57c**: vs target 57 (0c), tape-position **EXPENSIVE-3rd**
- **outcome:** determined (ws), exit_fill pnl=$0.8

**PAIR:** posted 2 legs; filled 2.
  → BOTH FILLED, combined = 42+57 = **99c [98-100]**

## KXATPCHALLENGERMATCH-26JUN30GOILIN  [ATP_CHALL]

### GOI  (KXATPCHALLENGERMATCH-26JUN30GOILIN-GOI)
- **timeline:** 15:47 post 53c x5 (resting) | 18:14 **FILL 53c x5 v4_resting_maker** | 18:14 exit_post 67c | 18:17 exit_fill 67c pnl$0.7
- **entry grade:** assumption cell=53 target_bid=53c | tape premkt last_trade min/med/max = 47/74/99c (n=15472) | book-at-post @15:47 bid53/ask56; @15:47 bid53/ask56
  → **FILL 53c**: vs target 53 (0c), tape-position **CHEAP-3rd**
- **mechanical:** would_skip_walled x1
- **outcome:** determined (ws), exit_fill pnl=$0.7

### LIN  (KXATPCHALLENGERMATCH-26JUN30GOILIN-LIN)
- **timeline:** 15:47 post 45c x5 (resting) | 18:15 **FILL 45c x5 v4_resting_maker** | 18:15 exit_post 54c | 19:18 cancel [settlement_cleanup]
- **entry grade:** assumption cell=45 target_bid=45c | tape premkt last_trade min/med/max = 1/25/53c (n=23236) | book-at-post @15:47 bid45/ask47; @15:47 bid45/ask47
  → **FILL 45c**: vs target 45 (0c), tape-position **EXPENSIVE-3rd**
- **outcome:** settled LOSS pnl=$-2.25

**PAIR:** posted 2 legs; filled 2.
  → BOTH FILLED, combined = 53+45 = **98c [98-100]**

## KXATPCHALLENGERMATCH-26JUN30LEGBIC  [ATP_CHALL]

### LEG  (KXATPCHALLENGERMATCH-26JUN30LEGBIC-LEG)
- **timeline:** 15:47 post 46c x5 (resting) | 17:29 **FILL 46c x5 v4_resting_maker** | 17:29 exit_post 55c | 19:55 exit_fill 55c pnl$0.45
- **entry grade:** assumption cell=46 target_bid=46c | tape premkt last_trade min/med/max = 41/57/99c (n=29073) | book-at-post @15:47 bid46/ask47; @15:47 bid46/ask47
  → **FILL 46c**: vs target 46 (0c), tape-position **CHEAP-3rd**
- **outcome:** determined (ws), exit_fill pnl=$0.45

**PAIR:** posted 1 legs; filled 1.

## KXATPCHALLENGERMATCH-26JUN30MARRIB  [ATP_CHALL]

### MAR  (KXATPCHALLENGERMATCH-26JUN30MARRIB-MAR)
- **timeline:** 15:47 post 14c x5 (resting) | 16:41 cancel [v4_t20m_fallback] | 16:41 post 14c x5 (resting) | 16:47 **FILL 14c x5 v4_reconciled** | 16:47 exit_post 19c | 16:55 exit_fill 19c pnl$0.25
- **entry grade:** assumption cell=14 target_bid=14c | tape premkt last_trade min/med/max = 1/11/30c (n=26765) | book-at-post @15:47 bid14/ask15; @16:41 bid14/ask15
  → **FILL 14c**: vs target 14 (0c), tape-position **mid-3rd**
- **mechanical:** v4_t20m_fallback@16:41 ; would_skip_walled x1
- **outcome:** determined (ws), exit_fill pnl=$0.25

### RIB  (KXATPCHALLENGERMATCH-26JUN30MARRIB-RIB)
- **timeline:** 15:47 post 85c x5 (resting) | 16:41 cancel [v4_t20m_fallback] | 16:41 post 85c x5 (resting) | 16:42 cancel [v4_move_repost] | 16:42 post 86c x5 (resting) | 16:44 cancel [v4_t20m_fallback] | 16:44 post 86c x5 (resting) | 16:47 **FILL 86c x5 v4_fallback_maker** | 16:47 exit_post 98c | 17:35 exit_fill 98c pnl$0.6
- **entry grade:** assumption cell=85 target_bid=85c | tape premkt last_trade min/med/max = 71/82/99c (n=37080) | book-at-post @15:47 bid85/ask86; @16:44 bid86/ask87
  → **FILL 86c**: vs target 85 (+1c), tape-position **mid-3rd**
- **mechanical:** v4_t20m_fallback@16:41 ; v4_t20m_fallback@16:44 ; would_skip_walled x1
- **outcome:** determined (ws), exit_fill pnl=$0.6

**PAIR:** posted 2 legs; filled 2.
  → BOTH FILLED, combined = 14+86 = **100c [98-100]**

## KXATPCHALLENGERMATCH-26JUN30SAKLER  [ATP_CHALL]

### SAK  (KXATPCHALLENGERMATCH-26JUN30SAKLER-SAK)
- **timeline:** 15:47 post 91c x5 (resting) | 16:41 cancel [v4_t20m_fallback] | 16:41 post 91c x5 (resting) | 19:15 **FILL 91c x5 v4_fallback_maker** | 19:15 exit_post 98c | 20:37 exit_fill 98c pnl$0.28 | 20:38 exit_fill 98c pnl$0.35
- **entry grade:** assumption cell=91 target_bid=91c | tape premkt last_trade min/med/max = 77/93/99c (n=32434) | book-at-post @15:47 bid91/ask92; @16:41 bid91/ask92
  → **FILL 91c**: vs target 91 (0c), tape-position **mid-3rd**
- **mechanical:** v4_t20m_fallback@16:41 ; would_skip_walled x1
- **outcome:** determined (ws), exit_fill pnl=$0.28

**PAIR:** posted 1 legs; filled 1.

## KXATPCHALLENGERMATCH-26JUN30SUNSHI  [ATP_CHALL]

### SHI  (KXATPCHALLENGERMATCH-26JUN30SUNSHI-SHI)
- **timeline:** 15:47 post 52c x5 (resting) | 20:02 **FILL 52c x5 v4_resting_maker** | 20:02 exit_post 66c | 22:56 exit_fill 66c pnl$0.7
- **entry grade:** assumption cell=52 target_bid=52c | tape premkt last_trade min/med/max = 49/72/99c (n=20591) | book-at-post @15:47 bid52/ask54; @15:47 bid52/ask54
  → **FILL 52c**: vs target 52 (0c), tape-position **CHEAP-3rd**
- **outcome:** determined (ws), exit_fill pnl=$0.7

### SUN  (KXATPCHALLENGERMATCH-26JUN30SUNSHI-SUN)
- **timeline:** 15:47 post 47c x5 (resting) | 18:27 cancel [v4_move_repost] | 18:27 post 49c x5 (resting) | 18:27 cancel [v4_t20m_fallback] | 18:27 post 49c x5 (resting) | 22:50 **FILL 49c x5 v4_fallback_maker** | 22:50 exit_post 61c | 23:54 cancel [settlement_cleanup]
- **entry grade:** assumption cell=47 target_bid=47c | tape premkt last_trade min/med/max = 1/28/54c (n=28311) | book-at-post @15:47 bid47/ask50; @18:27 bid49/ask50
  → **FILL 49c**: vs target 47 (+2c), tape-position **EXPENSIVE-3rd**
- **mechanical:** v4_t20m_fallback@18:27 ; would_skip_walled x1
- **outcome:** settled LOSS pnl=$-2.45

**PAIR:** posted 2 legs; filled 2.
  → BOTH FILLED, combined = 52+49 = **101c [>100]**

## KXATPCHALLENGERMATCH-26JUN30SURDRA  [ATP_CHALL]

### DRA  (KXATPCHALLENGERMATCH-26JUN30SURDRA-DRA)
- **timeline:** 15:47 post 57c x5 (resting) | 22:02 **FILL 57c x5 v4_resting_maker** | 22:02 exit_post 73c | 22:41 exit_fill 73c pnl$0.8
- **entry grade:** assumption cell=57 target_bid=57c | tape premkt last_trade min/med/max = 1/53/75c (n=37964) | book-at-post @15:47 bid57/ask58; @15:47 bid57/ask58
  → **FILL 57c**: vs target 57 (0c), tape-position **EXPENSIVE-3rd**
- **mechanical:** would_skip_walled x1
- **outcome:** determined (ws), exit_fill pnl=$0.8

### SUR  (KXATPCHALLENGERMATCH-26JUN30SURDRA-SUR)
- **timeline:** 15:47 post 41c x5 (resting) | 17:30 cancel [v4_move_repost] | 17:30 post 42c x5 (resting) | 18:11 cancel [v4_t20m_fallback] | 18:11 post 42c x5 (resting) | 19:34 **FILL 42c x5 v4_fallback_maker** | 19:34 exit_post 51c | 23:37 exit_fill 51c pnl$0.45
- **entry grade:** assumption cell=41 target_bid=41c | tape premkt last_trade min/med/max = 25/45/99c (n=49844) | book-at-post @15:47 bid41/ask42; @18:11 bid42/ask43
  → **FILL 42c**: vs target 41 (+1c), tape-position **CHEAP-3rd**
- **mechanical:** v4_t20m_fallback@18:11 ; would_skip_walled x1
- **outcome:** determined (ws), exit_fill pnl=$0.45

**PAIR:** posted 2 legs; filled 2.
  → BOTH FILLED, combined = 57+42 = **99c [98-100]**

## KXATPMATCH-26JUL01BROBUS  [ATP_MAIN]

### BRO  (KXATPMATCH-26JUL01BROBUS-BRO)
- **timeline:** 02:10 post 57c x5 (resting) | 02:59 cancel [v4_move_repost] | 02:59 post 58c x5 (resting)
- **entry grade:** assumption cell=57 target_bid=57c | tape premkt last_trade min/med/max = 54/57/60c (n=9149) | book-at-post @02:10 bid57/ask58; @02:59 bid58/ask59
- **mechanical:** would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

### BUS  (KXATPMATCH-26JUL01BROBUS-BUS)
- **timeline:** 02:58 post 41c x5 (resting)
- **entry grade:** assumption cell=41 target_bid=41c | tape premkt last_trade min/med/max = 41/44/46c (n=9731) | book-at-post @02:58 bid41/ask42; @02:58 bid41/ask42
- **mechanical:** would_skip_walled x1
- **outcome:** settled LOSS pnl=$0.0

**PAIR:** posted 2 legs; filled 0.
  → MISSED BOTH (posted, no fill)

## KXATPMATCH-26JUL01DAVMAR  [ATP_MAIN]

### DAV  (KXATPMATCH-26JUL01DAVMAR-DAV)
- **timeline:** 04:00 post 66c x5 (resting)
- **entry grade:** assumption cell=67 target_bid=66c | tape premkt last_trade min/med/max = 66/68/73c (n=11645) | book-at-post @04:00 bid66/ask67; @04:00 bid66/ask67
- **mechanical:** would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

### MAR  (KXATPMATCH-26JUL01DAVMAR-MAR)
- **timeline:** 04:00 post 33c x5 (resting)
- **entry grade:** assumption cell=34 target_bid=33c | tape premkt last_trade min/med/max = 29/33/34c (n=10243) | book-at-post @04:00 bid33/ask34; @04:00 bid33/ask34
- **mechanical:** would_skip_walled x1
- **outcome:** settled LOSS pnl=$0.0

**PAIR:** posted 2 legs; filled 0.
  → MISSED BOTH (posted, no fill)

## KXATPMATCH-26JUL01FUCTIE  [ATP_MAIN]

### FUC  (KXATPMATCH-26JUL01FUCTIE-FUC)
- **timeline:** 02:00 post 27c x5 (resting)
- **entry grade:** assumption cell=28 target_bid=27c | tape premkt last_trade min/med/max = 27/28/30c (n=5852) | book-at-post @02:00 bid27/ask28; @02:00 bid27/ask28
- **mechanical:** would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

### TIE  (KXATPMATCH-26JUL01FUCTIE-TIE)
- **timeline:** 02:00 post 73c x5 (resting) | 02:30 cancel [v4_move_repost] | 02:30 post 74c x5 (resting) | 03:09 **FILL 74c x5 v4_resting_maker** | 03:09 exit_post 93c
- **entry grade:** assumption cell=74 target_bid=73c | tape premkt last_trade min/med/max = 72/74/75c (n=6285) | book-at-post @02:00 bid73/ask74; @02:30 bid74/ask75
  → **FILL 74c**: vs target 73 (+1c), tape-position **EXPENSIVE-3rd**
- **mechanical:** would_skip_walled x1
- **outcome:** OPEN

**PAIR:** posted 2 legs; filled 1.
  → ONE-SIDED. kept=TIE, missed=FUC class=**TOO_DEEP** | catchable sibling dedup opps: 13:14 ~28c x3; 18:57 ~27c x17; 20:32 ~27c x57; 23:10 ~27c x16; 23:53 ~27c x30

## KXATPMATCH-26JUL01HUROFN  [ATP_MAIN]

### HUR  (KXATPMATCH-26JUL01HUROFN-HUR)
- **timeline:** 02:00 post 73c x5 (resting)
- **entry grade:** assumption cell=74 target_bid=73c | tape premkt last_trade min/med/max = 73/75/75c (n=4878) | book-at-post @02:00 bid74/ask74; @02:00 bid74/ask74
- **mechanical:** would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

### OFN  (KXATPMATCH-26JUL01HUROFN-OFN)
- **timeline:** 02:00 post 25c x5 (resting) | 03:56 **FILL 25c x5 v4_resting_maker** | 03:56 exit_post 32c
- **entry grade:** assumption cell=26 target_bid=25c | tape premkt last_trade min/med/max = 25/27/27c (n=3073) | book-at-post @02:00 bid26/ask26; @02:00 bid26/ask26
  → **FILL 25c**: vs target 25 (0c), tape-position **CHEAP-3rd**
- **mechanical:** would_skip_walled x1
- **outcome:** OPEN

**PAIR:** posted 2 legs; filled 1.
  → ONE-SIDED. kept=OFN, missed=HUR class=**PULLED** | catchable sibling dedup opps: 12:30 ~73c x6; 12:54 ~73c x6; 18:40 ~73c x66; 23:54 ~74c x2

## KXATPMATCH-26JUL01KWONPAU  [ATP_MAIN]

### KWON  (KXATPMATCH-26JUL01KWONPAU-KWON)
- **timeline:** 02:00 post 12c x5 (resting) | 03:36 **FILL 12c x5 v4_resting_maker** | 03:36 exit_post 17c
- **entry grade:** assumption cell=13 target_bid=12c | tape premkt last_trade min/med/max = 12/14/14c (n=7042) | book-at-post @02:00 bid13/ask13; @02:00 bid13/ask13
  → **FILL 12c**: vs target 12 (0c), tape-position **CHEAP-3rd**
- **mechanical:** would_skip_walled x1
- **outcome:** OPEN

### PAU  (KXATPMATCH-26JUL01KWONPAU-PAU)
- **timeline:** 02:10 post 88c x5 (resting)
- **entry grade:** assumption cell=88 target_bid=88c | tape premkt last_trade min/med/max = 86/88/89c (n=8227) | book-at-post @02:10 bid88/ask89; @02:10 bid88/ask89
- **mechanical:** would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

**PAIR:** posted 2 legs; filled 1.
  → ONE-SIDED. kept=KWON, missed=PAU class=**PULLED** | catchable sibling dedup opps: 10:10 ~87c x380; 15:21 ~86c x39; 15:59 ~86c x13; 16:13 ~86c x25; 16:15 ~86c x18

## KXATPMATCH-26JUL01MEJZHE  [ATP_MAIN]

### MEJ  (KXATPMATCH-26JUL01MEJZHE-MEJ)
- **timeline:** 03:30 post 20c x5 (resting)
- **entry grade:** assumption cell=21 target_bid=20c | tape premkt last_trade min/med/max = 20/23/28c (n=5248) | book-at-post @03:30 bid20/ask21; @03:30 bid20/ask21
- **mechanical:** would_skip_walled x1
- **outcome:** settled LOSS pnl=$0.0

### ZHE  (KXATPMATCH-26JUL01MEJZHE-ZHE)
- **timeline:** 03:45 post 79c x5 (resting)
- **entry grade:** assumption cell=79 target_bid=79c | tape premkt last_trade min/med/max = 74/79/80c (n=3928) | book-at-post @03:45 bid79/ask80; @03:45 bid79/ask80
- **mechanical:** would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

**PAIR:** posted 2 legs; filled 0.
  → MISSED BOTH (posted, no fill)

## KXATPMATCH-26JUL01SAFVAN  [ATP_MAIN]

### SAF  (KXATPMATCH-26JUL01SAFVAN-SAF)
- **timeline:** 03:45 post 55c x5 (resting)
- **entry grade:** assumption cell=55 target_bid=55c | tape premkt last_trade min/med/max = 55/56/57c (n=8855) | book-at-post @03:45 bid55/ask56; @03:45 bid55/ask56
- **outcome:** settled WIN pnl=$0.0

### VAN  (KXATPMATCH-26JUL01SAFVAN-VAN)
- **timeline:** 03:45 post 45c x5 (resting) | 03:56 **FILL 45c x5 v4_engagement_join** | 03:56 exit_post 54c
- **entry grade:** assumption cell=45 target_bid=45c | tape premkt last_trade min/med/max = 43/45/46c (n=8861) | book-at-post @03:45 bid45/ask46; @03:45 bid45/ask46
  → **FILL 45c**: vs target 45 (0c), tape-position **EXPENSIVE-3rd**
- **mechanical:** would_skip_walled x1
- **outcome:** OPEN

**PAIR:** posted 2 legs; filled 1.
  → ONE-SIDED. kept=VAN, missed=SAF class=**PULLED** | catchable sibling dedup opps: 18:12 ~55c x19; 18:17 ~55c x5; 00:22 ~55c x10632; 00:45 ~55c x1058; 01:04 ~55c x17

## KXITFMATCH-26JUL01BARSAK  [ITF_M]

### BAR  (KXITFMATCH-26JUL01BARSAK-BAR)
- **timeline:** 01:30 post 52c x5 (resting) | 02:40 cancel [v4_t20m_fallback] | 02:40 post 52c x5 (resting) | 03:07 **FILL 52c x5 v4_fallback_maker** | 03:07 exit_post 66c
- **entry grade:** assumption cell=57 target_bid=52c | tape premkt last_trade min/med/max = 22/45/57c (n=3988) | book-at-post @01:30 bid52/ask55; @02:40 bid52/ask53
  → **FILL 52c**: vs target 52 (0c), tape-position **EXPENSIVE-3rd**
- **mechanical:** v4_t20m_fallback@02:40 (41min before onset) ; itf_recent_volume_floor x159
- **outcome:** OPEN

### SAK  (KXITFMATCH-26JUL01BARSAK-SAK)
- **timeline:** 01:56 post 45c x5 (resting) | 01:56 cancel [v4_move_repost] | 01:56 post 46c x5 (resting) | 02:40 cancel [v4_t20m_fallback] | 02:40 post 46c x5 (resting) | 03:22 cancel [match_live_cancel]
- **entry grade:** assumption cell=46 target_bid=45c | tape premkt last_trade min/med/max = 48/56/79c (n=2191) | book-at-post @01:56 bid46/ask48; @02:40 bid46/ask48
- **mechanical:** v4_t20m_fallback@02:40 (41min before onset) ; itf_recent_volume_floor x187 ; would_skip_walled x1
- **outcome:** OPEN

**PAIR:** posted 2 legs; filled 1.
  → ONE-SIDED. kept=BAR, missed=SAK class=**NO_OPP** | catchable sibling dedup opps: none

## KXITFMATCH-26JUL01HOMDAG  [ITF_M]

### DAG  (KXITFMATCH-26JUL01HOMDAG-DAG)
- **timeline:** 01:46 post 52c x5 (resting) | 02:40 cancel [v4_t20m_fallback] | 02:40 post 52c x5 (resting) | 03:05 **FILL 52c x5 v4_fallback_maker** | 03:05 exit_post 66c
- **entry grade:** assumption cell=55 target_bid=52c | tape premkt last_trade min/med/max = 52/55/58c (n=521) | book-at-post @01:46 bid52/ask55; @02:40 bid52/ask54
  → **FILL 52c**: vs target 52 (0c), tape-position **CHEAP-3rd**
- **mechanical:** v4_t20m_fallback@02:40 ; itf_recent_volume_floor x40 ; would_skip_walled x1
- **outcome:** OPEN

### HOM  (KXITFMATCH-26JUL01HOMDAG-HOM)
- **timeline:** 01:46 post 45c x5 (resting) | 02:40 cancel [v4_t20m_fallback] | 02:40 post 45c x5 (resting)
- **entry grade:** assumption cell=45 target_bid=45c | tape premkt last_trade min/med/max = 48/49/52c (n=239) | book-at-post @01:46 bid45/ask48; @02:40 bid45/ask47
- **mechanical:** v4_t20m_fallback@02:40 ; itf_recent_volume_floor x144 ; would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

**PAIR:** posted 2 legs; filled 1.
  → ONE-SIDED. kept=DAG, missed=HOM class=**NO_OPP** | catchable sibling dedup opps: none

## KXITFMATCH-26JUL01JASSUZ  [ITF_M]

### JAS  (KXITFMATCH-26JUL01JASSUZ-JAS)
- **timeline:** 22:27 post 90c x5 (resting) | 23:43 cancel [v4_move_repost] | 23:43 post 91c x5 (resting) | 00:05 **FILL 91c x5 v4_engagement_join** | 00:05 exit_post 98c
- **entry grade:** assumption cell=90 target_bid=90c | tape premkt last_trade min/med/max = 86/91/94c (n=3172) | book-at-post @22:27 bid90/ask93; @23:43 bid91/ask93
  → **FILL 91c**: vs target 90 (+1c), tape-position **mid-3rd**
- **mechanical:** itf_recent_volume_floor x75 ; would_skip_walled x1
- **outcome:** OPEN

### SUZ  (KXITFMATCH-26JUL01JASSUZ-SUZ)
- **timeline:** 21:57 post 7c x5 (resting) | 21:58 cancel [v4_move_repost] | 21:58 post 8c x5 (resting) | 23:03 **FILL 8c x5 v4_engagement_join** | 23:03 exit_post 12c | 23:05 exit_fill 12c pnl$0.2
- **entry grade:** assumption cell=8 target_bid=7c | tape premkt last_trade min/med/max = 5/13/15c (n=4197) | book-at-post @21:57 bid8/ask9; @21:58 bid8/ask9
  → **FILL 8c**: vs target 7 (+1c), tape-position **CHEAP-3rd**
- **mechanical:** itf_recent_volume_floor x75
- **outcome:** determined (ws), exit_fill pnl=$0.2

**PAIR:** posted 2 legs; filled 2.
  → BOTH FILLED, combined = 91+8 = **99c [98-100]**

## KXITFMATCH-26JUL01JONOCH  [ITF_M]

### JON  (KXITFMATCH-26JUL01JONOCH-JON)
- **timeline:** 22:33 post 81c x5 (resting) | 00:10 cancel [v4_t20m_fallback] | 00:10 post 83c x5 (resting) | 00:30 **FILL 83c x2 v4_fallback_maker** | 00:30 exit_post 98c | 00:33 **FILL 83c x3 v4_fallback_maker** | 00:33 cancel [v4_exit_reset] | 00:33 exit_post 98c | 01:07 **FILL 83c x5 v4_fallback_maker** | 01:07 cancel [v4_exit_reset] | 01:07 cancel [v4_exit_reset_stray] | 01:07 exit_post 98c | 03:19 exit_fill 98c pnl$0.75
- **entry grade:** assumption cell=81 target_bid=81c | tape premkt last_trade min/med/max = 32/68/99c (n=27833) | book-at-post @22:33 bid81/ask84; @00:10 bid83/ask84
  → **FILL 83c**: vs target 81 (+2c), tape-position **EXPENSIVE-3rd**
- **mechanical:** v4_t20m_fallback@00:10 ; itf_recent_volume_floor x46 ; would_skip_walled x1
- **outcome:** determined (ws), exit_fill pnl=$0.75

### OCH  (KXITFMATCH-26JUL01JONOCH-OCH)
- **timeline:** 22:09 post 16c x5 (resting) | 00:10 cancel [v4_t20m_fallback] | 00:10 post 16c x5 (resting) | 01:23 **FILL 16c x5 v4_fallback_maker** | 01:23 exit_post 21c | 01:32 exit_fill 21c pnl$0.25
- **entry grade:** assumption cell=16 target_bid=16c | tape premkt last_trade min/med/max = 1/32/72c (n=22253) | book-at-post @22:09 bid16/ask19; @00:10 bid16/ask19
  → **FILL 16c**: vs target 16 (0c), tape-position **CHEAP-3rd**
- **mechanical:** v4_t20m_fallback@00:10 ; itf_recent_volume_floor x46 ; would_skip_walled x1
- **outcome:** determined (ws), exit_fill pnl=$0.25

**PAIR:** posted 2 legs; filled 2.
  → BOTH FILLED, combined = 83+16 = **99c [98-100]**

## KXITFMATCH-26JUL01LUONOR  [ITF_M]

### NOR  (KXITFMATCH-26JUL01LUONOR-NOR)
- **timeline:** 22:11 post 71c x5 (resting) | 22:11 cancel [v4_move_repost] | 22:11 cancel [v4_move_repost] | 22:11 post 72c x5 (resting) | 23:40 cancel [v4_t20m_fallback] | 23:40 post 72c x5 (resting)
- **entry grade:** assumption cell=72 target_bid=71c | tape premkt last_trade min/med/max = 73/74/80c (n=1860) | book-at-post @22:11 bid74/ask73; @23:40 bid73/ask73
- **mechanical:** v4_t20m_fallback@23:40 ; itf_recent_volume_floor x32 ; would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

**PAIR:** posted 1 legs; filled 0.
  → MISSED BOTH (posted, no fill)

## KXITFMATCH-26JUL01TOMCHE  [ITF_M]

### TOM  (KXITFMATCH-26JUL01TOMCHE-TOM)
- **timeline:** 21:39 post 67c x5 (resting) | 22:07 **FILL 67c x5 v4_resting_maker** | 22:07 exit_post 86c
- **entry grade:** assumption cell=67 target_bid=67c | tape premkt last_trade min/med/max = 35/66/74c (n=2443) | book-at-post @21:39 bid67/ask69; @21:39 bid67/ask69
  → **FILL 67c**: vs target 67 (0c), tape-position **EXPENSIVE-3rd**
- **mechanical:** itf_recent_volume_floor x154
- **outcome:** OPEN

**PAIR:** posted 1 legs; filled 1.

## KXITFMATCH-26JUL01VOLWIS  [ITF_M]

### VOL  (KXITFMATCH-26JUL01VOLWIS-VOL)
- **timeline:** 02:05 post 7c x5 (resting) | 02:06 cancel [v4_move_repost] | 02:06 post 8c x5 (resting) | 02:54 **FILL 8c x1 v4_resting_maker** | 02:54 exit_post 12c | 03:09 cancel [orphan_buy_reconcile_cleanup]
- **entry grade:** assumption cell=9 target_bid=7c | tape premkt last_trade min/med/max = 8/10/13c (n=1085) | book-at-post @02:05 bid9/ask9; @02:06 bid9/ask9
  → **FILL 8c**: vs target 7 (+1c), tape-position **CHEAP-3rd**
- **mechanical:** itf_recent_volume_floor x124
- **outcome:** OPEN

### WIS  (KXITFMATCH-26JUL01VOLWIS-WIS)
- **timeline:** 02:05 post 90c x5 (resting) | 03:40 cancel [v4_t20m_fallback] | 03:40 post 91c x5 (resting)
- **entry grade:** assumption cell=90 target_bid=90c | tape premkt last_trade min/med/max = 91/94/95c (n=1052) | book-at-post @02:05 bid90/ask92; @03:40 bid91/ask92
- **mechanical:** v4_t20m_fallback@03:40 ; itf_recent_volume_floor x124 ; would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

**PAIR:** posted 2 legs; filled 1.
  → ONE-SIDED. kept=VOL, missed=WIS class=**PULLED** | catchable sibling dedup opps: 21:45 ~91c x26

## KXITFMATCH-26JUN30SHINIS  [ITF_M]

### NIS  (KXITFMATCH-26JUN30SHINIS-NIS)
- **timeline:** 22:20 post 15c x5 (resting) | 22:40 cancel [v4_t20m_fallback] | 22:40 post 12c x5 (resting) | 22:42 cancel [v4_move_repost] | 22:42 post 12c x5 (resting) | 22:44 cancel [v4_t20m_fallback] | 22:44 post 12c x5 (resting) | 23:16 cancel [match_live_cancel]
- **entry grade:** assumption cell=16 target_bid=15c | tape premkt last_trade min/med/max = 13/18/21c (n=2311) | book-at-post @22:20 bid15/ask16; @22:44 bid12/ask15
- **mechanical:** v4_t20m_fallback@22:40 (35min before onset) ; v4_t20m_fallback@22:44 (31min before onset) ; itf_recent_volume_floor x196 ; would_skip_walled x1
- **outcome:** determined (ws)

### SHI  (KXITFMATCH-26JUN30SHINIS-SHI)
- **timeline:** 22:20 post 83c x5 (resting) | 22:40 cancel [v4_t20m_fallback] | 22:40 post 83c x5 (resting) | 22:42 cancel [v4_move_repost] | 22:42 post 84c x5 (resting) | 22:42 cancel [v4_t20m_fallback] | 22:42 post 84c x5 (resting) | 22:50 cancel [v4_move_repost] | 22:50 post 85c x5 (resting) | 22:52 cancel [v4_t20m_fallback] | 22:52 post 85c x5 (resting) | 23:10 **FILL 85c x5 v4_fallback_maker** | 23:10 exit_post 98c | 00:51 exit_fill 98c pnl$0.65
- **entry grade:** assumption cell=86 target_bid=83c | tape premkt last_trade min/med/max = 84/85/87c (n=2357) | book-at-post @22:20 bid83/ask86; @22:52 bid85/ask86
  → **FILL 85c**: vs target 83 (+2c), tape-position **mid-3rd**
- **mechanical:** v4_t20m_fallback@22:40 (35min before onset) ; v4_t20m_fallback@22:42 (33min before onset) ; v4_t20m_fallback@22:52 (23min before onset) ; itf_recent_volume_floor x196 ; would_skip_walled x1
- **outcome:** determined (ws), exit_fill pnl=$0.65

**PAIR:** posted 2 legs; filled 1.
  → ONE-SIDED. kept=SHI, missed=NIS class=**TOO_DEEP** | catchable sibling dedup opps: 23:13 ~17c x40

## KXITFWMATCH-26JUL01COLCHA  [ITF_W]

### COL  (KXITFWMATCH-26JUL01COLCHA-COL)
- **timeline:** 00:30 post 1c x5 (resting) | 00:30 cancel [v4_move_repost] | 00:30 post 2c x5 (resting) | 00:34 cancel [v4_move_repost] | 00:34 post 3c x5 (resting) | 00:36 cancel [v4_move_repost] | 00:36 post 4c x5 (resting) | 00:49 cancel [v4_move_repost] | 00:49 post 5c x5 (resting) | 00:51 cancel [v4_move_repost] | 00:51 post 6c x5 (resting) | 00:53 cancel [v4_move_repost] | 00:53 post 8c x5 (resting) | 00:54 cancel [v4_move_repost] | 00:54 post 9c x5 (resting) | 00:55 cancel [v4_move_repost] | 00:55 post 10c x5 (resting) | 00:56 cancel [v4_move_repost] | 00:56 post 11c x5 (resting) | 00:57 cancel [v4_move_repost] | 00:57 post 12c x5 (resting) | 00:58 cancel [v4_move_repost] | 00:58 post 13c x5 (resting) | 00:59 cancel [v4_move_repost]
- **entry grade:** assumption cell=2 target_bid=1c | tape premkt last_trade min/med/max = 45/45/45c (n=117) | book-at-post @00:30 bid2/ask94; @01:03 bid45/ask49
  → **FILL 45c**: vs target 1 (+44c), tape-position **flat**
- **outcome:** OPEN

**PAIR:** posted 1 legs; filled 1.

## KXITFWMATCH-26JUL01GARLOP  [ITF_W]

### LOP  (KXITFWMATCH-26JUL01GARLOP-LOP)
- **timeline:** 00:00 post 2c x5 (resting) | 00:00 cancel [v4_move_repost] | 00:00 cancel [v4_move_repost] | 00:00 cancel [v4_move_repost] | 00:00 cancel [v4_move_repost] | 00:00 post 2c x5 (resting) | 00:02 cancel [v4_move_repost] | 00:02 post 2c x5 (resting) | 00:04 cancel [v4_move_repost] | 00:04 post 2c x5 (resting) | 00:05 cancel [v4_move_repost] | 00:05 post 2c x5 (resting) | 00:08 cancel [v4_move_repost] | 00:08 post 2c x5 (resting) | 00:10 cancel [v4_move_repost] | 00:10 post 2c x5 (resting) | 00:12 cancel [v4_move_repost] | 00:12 post 2c x5 (resting) | 00:14 cancel [v4_move_repost] | 00:14 post 2c x5 (resting) | 00:16 cancel [v4_move_repost] | 00:16 post 2c x5 (resting) | 00:19 cancel [v4_move_repost] | 00:19 post 2c x5 (resting)
- **entry grade:** assumption cell=28 target_bid=2c | tape premkt last_trade min/med/max = 42/42/45c (n=5969) | book-at-post @00:00 bid28/ask58; @01:00 bid42/ask73
  → **FILL 42c**: vs target 2 (+40c), tape-position **CHEAP-3rd**
- **outcome:** OPEN

**PAIR:** posted 1 legs; filled 1.

## KXITFWMATCH-26JUL01HUIAHN  [ITF_W]

### AHN  (KXITFWMATCH-26JUL01HUIAHN-AHN)
- **timeline:** 15:30 post 72c x5 (resting) | 15:31 cancel [v4_move_repost] | 15:31 post 73c x5 (resting) | 16:09 **FILL 73c x5 v4_resting_maker** | 16:09 exit_post 91c
- **entry grade:** assumption cell=75 target_bid=72c | tape premkt last_trade min/med/max = 36/57/80c (n=26475) | book-at-post @15:30 bid72/ask76; @15:31 bid73/ask76
  → **FILL 73c**: vs target 72 (+1c), tape-position **EXPENSIVE-3rd**
- **mechanical:** itf_recent_volume_floor x58
- **outcome:** OPEN

### HUI  (KXITFWMATCH-26JUL01HUIAHN-HUI)
- **timeline:** 15:20 post 24c x5 (resting) | 15:24 cancel [v4_move_repost] | 15:24 post 25c x5 (resting) | 15:42 cancel [v4_move_repost] | 15:42 post 26c x5 (resting) | 16:07 cancel [v4_move_repost] | 16:07 post 27c x5 (resting) | 16:10 cancel [v4_t20m_fallback] | 16:10 post 31c x5 (resting) | 16:10 cancel [v4_move_repost] | 16:10 post 25c x5 (resting) | 16:10 cancel [no_fallback_fat_spread]
- **entry grade:** assumption cell=24 target_bid=24c | tape premkt last_trade min/med/max = 27/35/61c (n=18500) | book-at-post @15:20 bid24/ask27; @16:10 bid25/ask32
- **mechanical:** v4_t20m_fallback@16:10 ; no_fallback_fat_spread@16:10 ; itf_recent_volume_floor x58 ; maker_only_no_late_entry x14
- **outcome:** OPEN

**PAIR:** posted 2 legs; filled 1.
  → ONE-SIDED. kept=AHN, missed=HUI class=**TOO_DEEP** | catchable sibling dedup opps: 17:44 ~32c x1; 17:50 ~31c x15; 17:53 ~32c x672; 18:40 ~33c x191

## KXITFWMATCH-26JUL01KALMUN  [ITF_W]

### KAL  (KXITFWMATCH-26JUL01KALMUN-KAL)
- **timeline:** 23:00 post 7c x5 (resting) | 00:12 cancel [v4_move_repost] | 00:12 post 8c x5 (resting) | 00:36 **FILL 8c x3 v4_resting_maker** | 00:36 exit_post 11c | 01:00 **FILL 8c x5 v4_resting_maker** | 01:00 cancel [v4_exit_reset] | 01:00 cancel [v4_exit_reset_stray] | 01:00 exit_post 11c | 01:02 exit_fill 11c pnl$0.15
- **entry grade:** assumption cell=8 target_bid=7c | tape premkt last_trade min/med/max = 3/11/18c (n=9097) | book-at-post @23:00 bid7/ask8; @00:12 bid8/ask9
  → **FILL 8c**: vs target 7 (+1c), tape-position **mid-3rd**
- **mechanical:** would_skip_walled x1
- **outcome:** determined (ws), exit_fill pnl=$0.15

### MUN  (KXITFWMATCH-26JUL01KALMUN-MUN)
- **timeline:** 23:25 post 89c x5 (resting) | 23:27 cancel [v4_move_repost] | 23:27 post 91c x5 (resting) | 01:22 cancel [v4_move_repost] | 01:22 post 92c x5 (resting) | 02:40 cancel [v4_t20m_fallback] | 02:40 post 92c x5 (resting) | 02:54 **FILL 92c x5 v4_fallback_maker** | 02:54 exit_post 98c
- **entry grade:** assumption cell=91 target_bid=89c | tape premkt last_trade min/med/max = 83/90/94c (n=8866) | book-at-post @23:25 bid91/ask93; @02:40 bid92/ask93
  → **FILL 92c**: vs target 89 (+3c), tape-position **EXPENSIVE-3rd**
- **mechanical:** v4_t20m_fallback@02:40
- **outcome:** OPEN

**PAIR:** posted 2 legs; filled 2.
  → BOTH FILLED, combined = 8+92 = **100c [98-100]**

## KXITFWMATCH-26JUL01VANVER  [ITF_W]

### VAN  (KXITFWMATCH-26JUL01VANVER-VAN)
- **timeline:** 23:37 post 45c x5 (resting) | 23:38 cancel [v4_move_repost] | 23:38 post 46c x5 (resting) | 02:40 cancel [v4_t20m_fallback] | 02:40 post 46c x5 (resting) | 03:22 **FILL 46c x5 v4_fallback_maker** | 03:22 exit_post 55c | 03:30 exit_fill 55c pnl$0.45
- **entry grade:** assumption cell=46 target_bid=45c | tape premkt last_trade min/med/max = 16/47/57c (n=11350) | book-at-post @23:37 bid46/ask47; @02:40 bid46/ask47
  → **FILL 46c**: vs target 45 (+1c), tape-position **EXPENSIVE-3rd**
- **mechanical:** v4_t20m_fallback@02:40 ; would_skip_walled x1
- **outcome:** determined (ws), exit_fill pnl=$0.45

### VER  (KXITFWMATCH-26JUL01VANVER-VER)
- **timeline:** 23:37 post 53c x5 (resting) | 00:12 cancel [v4_move_repost] | 00:12 post 54c x5 (resting) | 02:40 cancel [v4_t20m_fallback] | 02:40 post 53c x5 (resting) | 02:42 cancel [v4_move_repost] | 02:42 post 53c x5 (resting) | 02:44 cancel [v4_t20m_fallback] | 02:44 post 53c x5 (resting) | 03:26 **FILL 53c x5 v4_fallback_maker** | 03:26 exit_post 65c | 03:50 exit_fill 65c pnl$0.6
- **entry grade:** assumption cell=53 target_bid=53c | tape premkt last_trade min/med/max = 38/52/83c (n=12829) | book-at-post @23:37 bid53/ask54; @02:44 bid53/ask54
  → **FILL 53c**: vs target 53 (0c), tape-position **mid-3rd**
- **mechanical:** v4_t20m_fallback@02:40 ; v4_t20m_fallback@02:44
- **outcome:** determined (ws), exit_fill pnl=$0.6

**PAIR:** posted 2 legs; filled 2.
  → BOTH FILLED, combined = 46+53 = **99c [98-100]**

## KXITFWMATCH-26JUN30AHNYUA  [ITF_W]

### AHN  (KXITFWMATCH-26JUN30AHNYUA-AHN)
- **timeline:** 22:47 post 20c x5 (resting) | 23:11 cancel [v4_t20m_fallback] | 23:11 post 19c x5 (resting) | 23:13 cancel [v4_move_repost] | 23:13 post 19c x5 (resting) | 23:15 cancel [v4_t20m_fallback] | 23:15 post 19c x5 (resting) | 23:45 cancel [match_live_cancel]
- **entry grade:** assumption cell=20 target_bid=20c | tape premkt last_trade min/med/max = 19/26/30c (n=2613) | book-at-post @22:47 bid20/ask22; @23:15 bid19/ask22
- **mechanical:** v4_t20m_fallback@23:11 (34min before onset) ; v4_t20m_fallback@23:15 (30min before onset) ; itf_recent_volume_floor x211
- **outcome:** determined (ws)

### YUA  (KXITFWMATCH-26JUN30AHNYUA-YUA)
- **timeline:** 22:47 post 77c x5 (resting) | 22:48 cancel [v4_move_repost] | 22:48 post 78c x5 (resting) | 22:51 cancel [v4_move_repost] | 22:51 post 79c x5 (resting) | 23:11 cancel [v4_t20m_fallback] | 23:11 post 79c x5 (resting) | 23:25 **FILL 79c x3 v4_fallback_maker** | 23:25 exit_post 98c | 23:25 **FILL 79c x4 v4_fallback_maker** | 23:25 cancel [v4_exit_reset] | 23:25 exit_post 98c | 23:40 **FILL 79c x5 v4_fallback_maker** | 23:40 cancel [v4_exit_reset] | 23:40 exit_post 98c | 01:50 exit_fill 98c pnl$0.95
- **entry grade:** assumption cell=80 target_bid=77c | tape premkt last_trade min/med/max = 72/77/81c (n=3579) | book-at-post @22:47 bid78/ask80; @23:11 bid79/ask80
  → **FILL 79c**: vs target 77 (+2c), tape-position **EXPENSIVE-3rd**
- **mechanical:** v4_t20m_fallback@23:11 (34min before onset) ; itf_recent_volume_floor x211 ; would_skip_walled x1
- **outcome:** determined (ws), exit_fill pnl=$0.95

**PAIR:** posted 2 legs; filled 1.
  → ONE-SIDED. kept=YUA, missed=AHN class=**PULLED** | catchable sibling dedup opps: 23:42 ~19c x42

## KXITFWMATCH-26JUN30DESGUO  [ITF_W]

### DES  (KXITFWMATCH-26JUN30DESGUO-DES)
- **timeline:** 22:46 post 16c x5 (resting) | 23:11 cancel [v4_t20m_fallback] | 23:11 post 14c x5 (resting) | 23:11 cancel [v4_move_repost] | 23:11 post 15c x5 (resting) | 23:13 cancel [v4_t20m_fallback] | 23:13 post 14c x5 (resting) | 23:23 cancel [v4_move_repost] | 23:23 post 13c x5 (resting) | 23:23 cancel [v4_t20m_fallback] | 23:23 cancel [v4_t20m_fallback] | 23:23 post 13c x5 (resting) | 23:28 cancel [v4_move_repost] | 23:28 post 15c x5 (resting) | 23:29 cancel [v4_t20m_fallback] | 23:29 post 15c x5 (resting) | 00:54 cancel [match_live_cancel] | 00:54 post 16c x5 (filled) | 00:54 **FILL 15c x5 v4_fallback_maker**
- **entry grade:** assumption cell=16 target_bid=16c | tape premkt last_trade min/med/max = 15/20/25c (n=3195) | book-at-post @22:46 bid16/ask18; @00:54 bid16/ask17
  → **FILL 15c**: vs target 16 (-1c), tape-position **CHEAP-3rd**
- **mechanical:** v4_t20m_fallback@23:11 (103min before onset) ; v4_t20m_fallback@23:13 (101min before onset) ; v4_t20m_fallback@23:23 (91min before onset) ; v4_t20m_fallback@23:23 (91min before onset) ; v4_t20m_fallback@23:29 (85min before onset) ; itf_recent_volume_floor x225
- **outcome:** settled LOSS pnl=$-0.75

### GUO  (KXITFWMATCH-26JUN30DESGUO-GUO)
- **timeline:** 22:46 post 82c x5 (resting) | 22:59 cancel [v4_move_repost] | 22:59 post 83c x5 (resting) | 23:07 **FILL 83c x1 v4_resting_maker** | 23:07 exit_post 98c | 23:08 **FILL 83c x5 v4_resting_maker** | 23:08 cancel [v4_exit_reset] | 23:08 exit_post 98c | 01:26 exit_fill 98c pnl$0.75
- **entry grade:** assumption cell=84 target_bid=82c | tape premkt last_trade min/med/max = 76/82/86c (n=15996) | book-at-post @22:46 bid82/ask84; @22:59 bid83/ask84
  → **FILL 83c**: vs target 82 (+1c), tape-position **EXPENSIVE-3rd**
- **mechanical:** itf_recent_volume_floor x225
- **outcome:** determined (ws), exit_fill pnl=$0.75

**PAIR:** posted 2 legs; filled 2.
  → BOTH FILLED, combined = 15+83 = **98c [98-100]**

## KXITFWMATCH-26JUN30WANCHO  [ITF_W]

### CHO  (KXITFWMATCH-26JUN30WANCHO-CHO)
- **timeline:** 21:58 post 12c x5 (resting) | 22:00 cancel [v4_move_repost] | 22:00 post 13c x5 (resting) | 23:01 cancel [v4_t20m_fallback] | 23:01 post 13c x5 (resting) | 01:39 **FILL 13c x5 v4_fallback_maker** | 01:39 exit_post 17c | 01:39 exit_fill 17c pnl$0.2
- **entry grade:** assumption cell=14 target_bid=12c | tape premkt last_trade min/med/max = 1/14/28c (n=23790) | book-at-post @21:58 bid13/ask14; @23:01 bid13/ask14
  → **FILL 13c**: vs target 12 (+1c), tape-position **mid-3rd**
- **mechanical:** v4_t20m_fallback@23:01 ; itf_recent_volume_floor x158
- **outcome:** determined (ws), exit_fill pnl=$0.2

### WAN  (KXITFWMATCH-26JUN30WANCHO-WAN)
- **timeline:** 21:58 post 85c x5 (resting) | 21:58 cancel [v4_move_repost] | 21:58 post 86c x5 (resting) | 21:58 **FILL 86c x5 v4_resting_maker** | 21:58 exit_post 98c | 02:49 exit_fill 98c pnl$0.6
- **entry grade:** assumption cell=88 target_bid=85c | tape premkt last_trade min/med/max = 72/85/99c (n=21762) | book-at-post @21:58 bid85/ask88; @21:58 bid86/ask88
  → **FILL 86c**: vs target 85 (+1c), tape-position **mid-3rd**
- **mechanical:** itf_recent_volume_floor x158 ; would_skip_walled x1
- **outcome:** determined (ws), exit_fill pnl=$0.6

**PAIR:** posted 2 legs; filled 2.
  → BOTH FILLED, combined = 13+86 = **99c [98-100]**

## KXWTAMATCH-26JUL01GASOSA  [WTA_MAIN]

### GAS  (KXWTAMATCH-26JUL01GASOSA-GAS)
- **timeline:** 02:00 post 6c x5 (resting)
- **entry grade:** assumption cell=7 target_bid=6c | tape premkt last_trade min/med/max = 6/7/9c (n=5741) | book-at-post @02:00 bid7/ask7; @02:00 bid7/ask7
- **mechanical:** would_skip_walled x1
- **outcome:** settled LOSS pnl=$0.0

### OSA  (KXWTAMATCH-26JUL01GASOSA-OSA)
- **timeline:** 02:10 post 93c x5 (resting)
- **entry grade:** assumption cell=93 target_bid=93c | tape premkt last_trade min/med/max = 92/94/95c (n=3874) | book-at-post @02:10 bid93/ask94; @02:10 bid93/ask94
- **outcome:** settled WIN pnl=$0.0

**PAIR:** posted 2 legs; filled 0.
  → MISSED BOTH (posted, no fill)

## KXWTAMATCH-26JUL01MUCZHA  [WTA_MAIN]

### ZHA  (KXWTAMATCH-26JUL01MUCZHA-ZHA)
- **timeline:** 04:00 post 11c x5 (resting)
- **entry grade:** assumption cell=12 target_bid=11c | tape premkt last_trade min/med/max = 12/15/16c (n=4636) | book-at-post @04:00 bid12/ask12; @04:00 bid12/ask12
- **mechanical:** would_skip_walled x1
- **outcome:** settled LOSS pnl=$0.0

**PAIR:** posted 1 legs; filled 0.
  → MISSED BOTH (posted, no fill)

## KXWTAMATCH-26JUL01OSTRUZ  [WTA_MAIN]

### OST  (KXWTAMATCH-26JUL01OSTRUZ-OST)
- **timeline:** 02:10 post 76c x5 (resting) | 02:24 cancel [v4_move_repost] | 02:24 post 77c x5 (resting)
- **entry grade:** assumption cell=76 target_bid=76c | tape premkt last_trade min/med/max = 76/78/78c (n=4033) | book-at-post @02:10 bid76/ask78; @02:24 bid77/ask78
- **mechanical:** would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

### RUZ  (KXWTAMATCH-26JUL01OSTRUZ-RUZ)
- **timeline:** 02:10 post 23c x5 (resting)
- **entry grade:** assumption cell=23 target_bid=23c | tape premkt last_trade min/med/max = 23/24/24c (n=3489) | book-at-post @02:10 bid23/ask24; @02:10 bid23/ask24
- **mechanical:** would_skip_walled x1
- **outcome:** settled LOSS pnl=$0.0

**PAIR:** posted 2 legs; filled 0.
  → MISSED BOTH (posted, no fill)

## KXWTAMATCH-26JUL01PARSAW  [WTA_MAIN]

### PAR  (KXWTAMATCH-26JUL01PARSAW-PAR)
- **timeline:** 02:10 post 58c x5 (resting) | 03:10 **FILL 58c x5 v4_resting_maker** | 03:10 exit_post 74c
- **entry grade:** assumption cell=58 target_bid=58c | tape premkt last_trade min/med/max = 58/59/60c (n=5445) | book-at-post @02:10 bid58/ask59; @02:10 bid58/ask59
  → **FILL 58c**: vs target 58 (0c), tape-position **CHEAP-3rd**
- **outcome:** OPEN

### SAW  (KXWTAMATCH-26JUL01PARSAW-SAW)
- **timeline:** 02:10 post 42c x5 (resting)
- **entry grade:** assumption cell=42 target_bid=42c | tape premkt last_trade min/med/max = 41/42/43c (n=3263) | book-at-post @02:10 bid42/ask43; @02:10 bid42/ask43
- **mechanical:** would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

**PAIR:** posted 2 legs; filled 1.
  → ONE-SIDED. kept=PAR, missed=SAW class=**PULLED** | catchable sibling dedup opps: 21:59 ~41c x7; 18:21 ~41c x137; 01:07 ~42c x12; 01:33 ~42c x83; 01:52 ~42c x380

## KXWTAMATCH-26JUL01SABKES  [WTA_MAIN]

### KES  (KXWTAMATCH-26JUL01SABKES-KES)
- **timeline:** 04:00 post 11c x5 (resting)
- **entry grade:** assumption cell=12 target_bid=11c | tape premkt last_trade min/med/max = 9/13/14c (n=3316) | book-at-post @04:00 bid11/ask12; @04:00 bid11/ask12
- **mechanical:** would_skip_walled x1
- **outcome:** settled LOSS pnl=$0.0

**PAIR:** posted 1 legs; filled 0.
  → MISSED BOTH (posted, no fill)

## KXWTAMATCH-26JUL01SONLIU  [WTA_MAIN]

### LIU  (KXWTAMATCH-26JUL01SONLIU-LIU)
- **timeline:** 03:45 post 35c x5 (resting)
- **entry grade:** assumption cell=35 target_bid=35c | tape premkt last_trade min/med/max = 34/35/37c (n=3113) | book-at-post @03:45 bid35/ask36; @03:45 bid35/ask36
- **mechanical:** would_skip_walled x1
- **outcome:** settled WIN pnl=$0.0

### SON  (KXWTAMATCH-26JUL01SONLIU-SON)
- **timeline:** 03:45 post 65c x5 (resting)
- **entry grade:** assumption cell=65 target_bid=65c | tape premkt last_trade min/med/max = 64/66/67c (n=4195) | book-at-post @03:45 bid65/ask66; @03:45 bid65/ask66
- **mechanical:** would_skip_walled x1
- **outcome:** settled LOSS pnl=$0.0

**PAIR:** posted 2 legs; filled 0.
  → MISSED BOTH (posted, no fill)

## KXWTAMATCH-26JUL01TJEKAS  [WTA_MAIN]

### KAS  (KXWTAMATCH-26JUL01TJEKAS-KAS)
- **timeline:** 02:10 post 51c x5 (resting) | 02:42 cancel [v4_move_repost] | 02:42 post 52c x5 (resting) | 02:50 **FILL 52c x5 v4_engagement_join** | 02:50 exit_post 66c
- **entry grade:** assumption cell=51 target_bid=51c | tape premkt last_trade min/med/max = 51/53/55c (n=9587) | book-at-post @02:10 bid51/ask52; @02:42 bid52/ask53
  → **FILL 52c**: vs target 51 (+1c), tape-position **CHEAP-3rd**
- **outcome:** OPEN

### TJE  (KXWTAMATCH-26JUL01TJEKAS-TJE)
- **timeline:** 02:10 post 48c x5 (resting) | 02:14 **FILL 48c x5 v4_engagement_join** | 02:14 exit_post 59c
- **entry grade:** assumption cell=48 target_bid=48c | tape premkt last_trade min/med/max = 46/49/50c (n=7203) | book-at-post @02:10 bid48/ask49; @02:10 bid48/ask49
  → **FILL 48c**: vs target 48 (0c), tape-position **mid-3rd**
- **outcome:** OPEN

**PAIR:** posted 2 legs; filled 2.
  → BOTH FILLED, combined = 52+48 = **100c [98-100]**


## DEPLOY-BOX SUMMARY
- players (legs touched): 88 | events: 48
- pair outcome: BOTH-filled 14 | ONE-sided 21 | MISSED-both 13
- entry-grade tape position of FILLS: {'mid-3rd': 13, 'EXPENSIVE-3rd': 18, 'CHEAP-3rd': 17, 'flat': 1}
- combined distribution (both-filled pairs): {'>100': 2, '98-100': 12}
- one-sided miss class: {'NO_OPP': 4, 'PULLED': 8, 'TOO_DEEP': 4}
- mechanical gate — players hit: {'v4_t20m_fallback': 26, 'itf_recent_volume_floor': 22, 'no_fallback_fat_spread': 1, 'maker_only_no_late_entry': 1}