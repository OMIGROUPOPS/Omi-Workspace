# Bucket-A v1 — schedule_date_mismatch population, ground-truthed

Re-derivation 2026-06-10 ([C-T51-COHORTS]; recipe = the Jun-9 validation re-run
on the FULL June jsonl population with three more days of finalization).
Ground truth per event: trade-tape volume onset (T51-style 10-prints/60s latch,
live tape, historical_pull fallback), cross-checked vs Kalshi close_time for
finalized markets.

## CHECKSUM DELTA (reported, not forced)
Jun-9 expectation: ~38 finalized, feed-right 32 / ticker-right 6.
Re-derivation: population **94**, finalized **93** -> **ticker-right 41 /
feed-right 35 / BOTH-wrong 17 / unfinalized 1** (Lulu Sun vs Mary Stoiana).
The Jun-9 sample was an early-finalization snapshot; with the full population
ground-truthed, feed-wrong (ticker-right) is the MAJORITY class, and 17 events
had BOTH sources wrong (rain/backlog reschedules) — the class only tape liveness
can protect. Note: Qinwen Zheng vs Jaqueline Cristian re-classifies as
feed-right; Agustin Libre vs Tomas Martinez holds as ticker-right.

## The ticker-right cohort (41) — feed was WRONG; date-gate demotion exposes these

| match | ticker date | feed datetime | true date (onset) | T51 protection of the hypothetical feed-window |
|---|---|---|---|---|
| Landon Ardila vs Tyler Zink | 2026-06-01 | 2026-06-02T15:00 | 2026-06-01 (Jun01 04:18PM) | FULL (latch 14.7h before window open) |
| Robin Bertrand vs Patrick Zahraj | 2026-06-01 | 2026-06-02T14:10 | 2026-06-01 (Jun01 01:52PM) | FULL (latch 16.3h before window open) |
| Blaise Bicknell vs Johannus Monday | 2026-06-01 | 2026-06-03T15:55 | 2026-06-01 (Jun01 04:16PM) | FULL (latch 39.6h before window open) |
| Frederico Ferreira Silva vs Pedro Martinez | 2026-06-01 | 2026-05-20T14:00 | 2026-06-01 (Jun01 10:06AM) | PARTIAL (latch 292.1h after window open) |
| Daniel Milavsky vs Christian Langmo | 2026-06-01 | 2026-06-02T14:05 | 2026-06-01 (Jun01 02:38PM) | FULL (latch 15.4h before window open) |
| Yunchaokete Bu vs Lloyd Harris | 2026-06-01 | 2026-06-02T12:30 | 2026-06-01 (Jun01 09:44AM) | FULL (latch 18.8h before window open) |
| Ugo Blanchet vs Felix Gill | 2026-06-02 | 2026-06-03T12:45 | 2026-06-02 (Jun02 02:55PM) | FULL (latch 13.8h before window open) |
| Olaf Pieczkowski vs Karl Poling | 2026-06-02 | 2026-06-03T14:10 | 2026-06-02 (Jun02 08:52AM) | FULL (latch 21.3h before window open) |
| Sho Shimabukuro vs Shintaro Mochizuki | 2026-06-02 | 2026-06-03T15:00 | 2026-06-02 (Jun02 02:52PM) | FULL (latch 16.1h before window open) |
| Zhizhen Zhang vs Otto Virtanen | 2026-06-02 | 2026-06-03T14:00 | 2026-06-02 (Jun02 03:06PM) | FULL (latch 14.9h before window open) |
| Alexander Shevchenko vs Nikolas Sanchez Izquierdo | 2026-06-03 | 2026-06-03T00:30 | 2026-06-03 (Jun03 01:56AM) | PARTIAL (latch 9.4h after window open) |
| Braden Shick vs Aidan Mayo | 2026-06-03 | 2026-06-03T00:30 | 2026-06-03 (Jun03 05:53PM) | PARTIAL (latch 25.4h after window open) |
| Agustin Libre vs Tomas Martinez | 2026-06-07 | 2026-06-08T08:30 | 2026-06-07 (Jun07 05:15PM) | FULL (latch 7.2h before window open) |
| Benjamin Chelia vs Tomas Martinez | 2026-06-08 | 2026-06-09T13:10 | 2026-06-08 (Jun08 10:33PM) | FULL (latch 6.6h before window open) |
| Mateo Del Pino vs Arklon Huertas Del Pino Cordova | 2026-06-08 | 2026-06-09T13:10 | 2026-06-08 (Jun08 04:12PM) | FULL (latch 13.0h before window open) |
| Santiago Giamichelle vs Thiago Cigarran | 2026-06-08 | 2026-06-09T15:00 | 2026-06-08 (Jun08 03:32PM) | FULL (latch 15.5h before window open) |
| Samuel Heredia vs Julian Cundom | 2026-06-08 | 2026-06-09T13:10 | 2026-06-08 (Jun08 03:22PM) | FULL (latch 13.8h before window open) |
| Johan Alexander Rodriguez Rodriguez vs Wilson Leite | 2026-06-08 | 2026-06-09T13:10 | 2026-06-08 (Jun08 04:05PM) | FULL (latch 13.1h before window open) |
| Segundo Goity Zapico vs Federico Coria | 2026-06-09 | 2026-06-10T15:15 | 2026-06-09 (Jun09 04:42PM) | FULL (latch 14.5h before window open) |
| Henrique Rocha vs Charles Broom | 2026-06-09 | 2026-06-10T17:00 | 2026-06-09 (Jun09 08:03AM) | FULL (latch 24.9h before window open) |
| Sho Shimabukuro vs Stefanos Sakellaridis | 2026-06-06 | 2026-05-18T09:40 | 2026-06-06 (Jun06 06:41AM) | PARTIAL (latch 461.0h after window open) |
| Daniel Altmaier vs Frances Tiafoe | 2026-06-08 | 2026-06-09T14:40 | 2026-06-08 (Jun08 10:43AM) | FULL (latch 19.9h before window open) |
| Roberto Bautista Agut vs Marcos Giron | 2026-06-08 | 2026-06-09T09:15 | 2026-06-08 (Jun08 11:49PM) | FULL (latch 1.4h before window open) |
| Thijs Boogaard vs Yibing Wu | 2026-06-08 | 2026-06-10T09:05 | 2026-06-08 (Jun08 10:40AM) | FULL (latch 38.4h before window open) |
| Jaume Munar vs Martin Damm Jr | 2026-06-08 | 2026-06-09T09:50 | 2026-06-08 (Jun08 11:35PM) | FULL (latch 2.2h before window open) |
| Roman Safiullin vs Giovanni Mpetshi Perricard | 2026-06-08 | 2026-06-09T11:20 | 2026-06-08 (Jun08 10:25AM) | FULL (latch 16.9h before window open) |
| Mika Stojsavljevic vs Emerson Jones | 2026-06-01 | 2026-06-02T10:55 | 2026-06-01 (Jun01 09:39AM) | FULL (latch 17.3h before window open) |
| Mary Stoiana vs Lulu Sun | 2026-06-01 | 2026-06-02T12:45 | 2026-06-01 (Jun01 09:34AM) | FULL (latch 19.2h before window open) |
| Laura Mair vs Yiming Dang | 2026-06-02 | 2026-06-03T12:15 | 2026-06-02 (Jun02 12:49PM) | FULL (latch 15.4h before window open) |
| Taylah Preston vs Alicia Dudeney | 2026-06-02 | 2026-06-04T04:00 | 2026-06-02 (Jun02 03:06PM) | FULL (latch 28.9h before window open) |
| Ajla Tomljanovic vs Katie Swan | 2026-06-02 | 2026-06-04T04:00 | 2026-06-02 (Jun02 02:20PM) | FULL (latch 29.7h before window open) |
| Vendula Valdmannova vs Sayaka Ishii | 2026-06-07 | 2026-05-30T10:35 | 2026-06-07 (Jun07 11:25AM) | PARTIAL (latch 200.8h after window open) |
| Elvina Kalieva vs Ashlyn Krueger | 2026-06-08 | 2026-06-09T11:30 | 2026-06-08 (Jun08 12:45AM) | FULL (latch 26.7h before window open) |
| Mingge Xu vs Elizabeth Mandlik | 2026-06-08 | 2026-06-09T14:30 | 2026-06-08 (Jun08 05:30PM) | FULL (latch 13.0h before window open) |
| Darja Vidmanova vs Linda Fruhvirtova | 2026-06-08 | 2026-06-09T11:30 | 2026-06-08 (Jun08 02:04PM) | FULL (latch 13.4h before window open) |
| Katie Boulter vs Leylah Fernandez | 2026-06-07 | 2026-06-09T13:00 | 2026-06-07 (Jun07 10:34PM) | FULL (latch 30.4h before window open) |
| Harriet Dart vs Liudmila Samsonova | 2026-06-07 | 2026-06-08T09:00 | 2026-06-07 (Jun07 08:46PM) | FULL (latch 4.2h before window open) |
| Karolina Pliskova vs McCartney Kessler | 2026-06-07 | 2026-06-08T09:00 | 2026-06-07 (Jun07 07:56PM) | FULL (latch 5.1h before window open) |
| Mika Stojsavljevic vs Marta Kostyuk | 2026-06-07 | 2026-06-09T14:00 | 2026-06-07 (Jun07 10:19AM) | FULL (latch 43.7h before window open) |
| Barbora Krejcikova vs Renata Zarazua | 2026-06-08 | 2026-06-09T11:25 | 2026-06-08 (Jun08 10:16PM) | FULL (latch 5.1h before window open) |
| Greet Minnen vs Janice Tjen | 2026-06-08 | 2026-06-09T10:00 | 2026-06-08 (Jun08 09:35PM) | FULL (latch 4.4h before window open) |

**T51 hypothetical-window protection over the 41: {'FULL': 36, 'PARTIAL': 5}** (FULL = latch precedes the
feed-derived T-240 window open, so every hypothetical placement is blocked;
PARTIAL = latch lands inside the window — placements before the latch are exposed).

## Feed-right (35) — ticker was wrong; the current date-gate DISCARDS these correct-feed matches

- Tuncay Duran vs Stefano Napolitano — ticker 2026-06-01, feed 2026-06-02, true 2026-06-02
- Mark Lajal vs Leandro Riedi — ticker 2026-06-01, feed 2026-06-02, true 2026-06-02
- Andres Martin vs Blake Ellis — ticker 2026-06-01, feed 2026-06-03, true 2026-06-03
- Jack Pinnington Jones vs Aleksandar Vukic — ticker 2026-06-01, feed 2026-06-02, true 2026-06-02
- Braden Shick vs Ronald Hohmann — ticker 2026-06-01, feed 2026-06-02, true 2026-06-02
- Yuta Shimizu vs Dane Sweeny — ticker 2026-06-01, feed 2026-06-03, true 2026-06-03
- Coleman Wong vs Oliver Tarvet — ticker 2026-06-01, feed 2026-06-02, true 2026-06-02
- James McCabe vs Kamil Majchrzak — ticker 2026-06-02, feed 2026-06-03, true 2026-06-03
- Elias Ymer vs Christopher O'Connell — ticker 2026-06-02, feed 2026-06-03, true 2026-06-03
- Harry Wendelken vs Mark Lajal — ticker 2026-06-03, feed 2026-06-04, true 2026-06-04
- Karim Bennani vs Santiago Rodriguez Taverna — ticker 2026-06-08, feed 2026-06-09, true 2026-06-09
- Juan Sebastian Gomez vs Luciano Emanuel Ambrogi — ticker 2026-06-08, feed 2026-06-09, true 2026-06-09
- Pol Martin Tiffon vs Dali Blanch — ticker 2026-06-08, feed 2026-06-07, true 2026-06-07
- Facundo Mena vs Lorenzo Joaquin Rodriguez — ticker 2026-06-08, feed 2026-06-09, true 2026-06-09
- Nicolas Villalon Valdes vs Ezequiel Monferrer — ticker 2026-06-08, feed 2026-06-09, true 2026-06-09
- Ronald Hohmann vs Adria Soriano Barrera — ticker 2026-05-31, feed 2026-06-01, true 2026-06-01
- Garrett Johns vs Olaf Pieczkowski — ticker 2026-05-31, feed 2026-06-01, true 2026-06-01
- Braden Shick vs Dan Martin — ticker 2026-05-31, feed 2026-06-01, true 2026-06-01
- Tom Gentzsch vs Rinky Hijikata — ticker 2026-06-07, feed 2026-06-09, true 2026-06-09
- Niels Visker vs Elias Ymer — ticker 2026-06-07, feed 2026-06-06, true 2026-06-06
- Gabriel Diallo vs Adrian Mannarino — ticker 2026-06-08, feed 2026-06-09, true 2026-06-09
- Yannick Hanfmann vs Aleksandar Kovacevic — ticker 2026-06-08, feed 2026-06-09, true 2026-06-09
- Zhizhen Zhang vs Jenson Brooksby — ticker 2026-06-08, feed 2026-06-09, true 2026-06-09
- Gabriela Knutson vs Joanna Garland — ticker 2026-06-01, feed 2026-06-02, true 2026-06-02
- Celine Naef vs Maddison Inglis — ticker 2026-06-01, feed 2026-06-03, true 2026-06-03
- Ashlyn Krueger vs Himeno Sakatsume — ticker 2026-06-02, feed 2026-06-03, true 2026-06-03
- Tatjana Maria vs Linda Fruhvirtova — ticker 2026-06-02, feed 2026-06-03, true 2026-06-03
- Kayla Day vs Mary Stoiana — ticker 2026-06-08, feed 2026-06-09, true 2026-06-09
- Tereza Martincova vs Katie Swan — ticker 2026-06-09, feed 2026-06-10, true 2026-06-10
- Qinwen Zheng vs Jaqueline Cristian — ticker 2026-06-07, feed 2026-06-08, true 2026-06-08
- Alina Charaeva vs Polina Kudermetova — ticker 2026-06-08, feed 2026-06-07, true 2026-06-07
- Tamara Korpatsch vs Elena-Gabriela Ruse — ticker 2026-06-08, feed 2026-06-09, true 2026-06-09
- Donna Vekic vs Anna Blinkova — ticker 2026-06-08, feed 2026-06-07, true 2026-06-07
- Katie Volynets vs Zeynep Sonmez — ticker 2026-06-08, feed 2026-06-09, true 2026-06-09
- Dayana Yastremska vs Sara Bejlek — ticker 2026-06-08, feed 2026-06-09, true 2026-06-09

## Both-wrong (17) — only tape liveness can protect

- Edas Butvilas vs Trevor Svajda — ticker 2026-06-01, feed 2026-06-03, TRUE 2026-06-02
- Timo Legout vs Andres Andrade — ticker 2026-06-01, feed 2026-06-03, TRUE 2026-06-02
- Henry Searle vs Mitchell Krueger — ticker 2026-06-01, feed 2026-06-03, TRUE 2026-06-02
- Fajing Sun vs Andre Ilagan — ticker 2026-06-01, feed 2026-06-03, TRUE 2026-06-02
- Billy Harris vs Yunchaokete Bu — ticker 2026-06-03, feed 2026-06-02, TRUE 2026-06-04
- Nick Kyrgios vs Corentin Moutet — ticker 2026-06-07, feed 2026-06-09, TRUE 2026-06-06
- Diego Dedura-Palomero vs James Duckworth — ticker 2026-06-08, feed 2026-06-09, TRUE 2026-06-07
- Tallon Griekspoor vs Botic Van de Zandschulp — ticker 2026-06-08, feed 2026-06-10, TRUE 2026-06-09
- Hubert Hurkacz vs Marton Fucsovics — ticker 2026-06-08, feed 2026-06-10, TRUE 2026-06-09
- James McCabe vs Zizou Bergs — ticker 2026-06-08, feed 2026-06-10, TRUE 2026-06-09
- Otto Virtanen vs Kamil Majchrzak — ticker 2026-06-08, feed 2026-06-10, TRUE 2026-06-07
- Emerson Jones vs Dalma Galfi — ticker 2026-06-08, feed 2026-06-09, TRUE 2026-06-10
- Laura Siegemund vs Francesca Jones — ticker 2026-06-07, feed 2026-06-09, TRUE 2026-06-08
- Nikola Bartunkova vs Hanne Vandewinkel — ticker 2026-06-08, feed 2026-06-10, TRUE 2026-06-09
- Lois Boisson vs Solana Sierra — ticker 2026-06-08, feed 2026-06-10, TRUE 2026-06-09
- Jessica Bouzas Maneiro vs Ajla Tomljanovic — ticker 2026-06-08, feed 2026-06-10, TRUE 2026-06-09
- Anastasia Potapova vs Suzan Lamens — ticker 2026-06-08, feed 2026-06-10, TRUE 2026-06-07
