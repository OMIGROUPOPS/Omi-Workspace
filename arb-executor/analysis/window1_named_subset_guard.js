"use strict";

function ensure(condition, message) { if (!condition) throw new Error(message); }

function parseExactNamedSubset(raw, expectedRaw) {
  ensure(typeof raw === "string" && raw.trim().length > 0, "NAMED_SUBSET_GUARD subset-games is required");
  const eventIds = raw.split(",").map((value) => value.trim()).filter(Boolean);
  const expectedGames = Number(expectedRaw);
  ensure(Number.isInteger(expectedGames) && expectedGames > 0, "NAMED_SUBSET_GUARD expected-game-count must be a positive integer");
  ensure(eventIds.length === expectedGames, `NAMED_SUBSET_GUARD named count ${eventIds.length} != expected ${expectedGames}`);
  ensure(new Set(eventIds).size === eventIds.length, "NAMED_SUBSET_GUARD duplicate named game");
  ensure(eventIds.every((eventId) => /^KX[A-Z0-9]+(?:-[A-Z0-9]+)+$/.test(eventId)), "NAMED_SUBSET_GUARD malformed event id");
  return Object.freeze({ mode: "EXACT_N_NAMED_GAMES", expected_games: expectedGames, event_ids: Object.freeze([...eventIds]) });
}

function createExecutionGuard(spec) {
  const allowed = new Set(spec.event_ids), executed = [];
  return Object.freeze({
    record(eventId) {
      ensure(allowed.has(eventId), `NAMED_SUBSET_GUARD unrequested execution ${eventId}`);
      ensure(!executed.includes(eventId), `NAMED_SUBSET_GUARD duplicate execution ${eventId}`);
      executed.push(eventId);
    },
    finalize() {
      const missing = spec.event_ids.filter((eventId) => !executed.includes(eventId));
      const unexpected = executed.filter((eventId) => !allowed.has(eventId));
      ensure(executed.length === spec.expected_games, `NAMED_SUBSET_GUARD executed count ${executed.length} != expected ${spec.expected_games}`);
      ensure(missing.length === 0 && unexpected.length === 0, `NAMED_SUBSET_GUARD conservation failed missing=${missing.join(",")} unexpected=${unexpected.join(",")}`);
      return Object.freeze({
        mode: spec.mode,
        expected_games: spec.expected_games,
        named_event_ids: [...spec.event_ids],
        executed_event_ids: [...executed],
        total_games_executed: executed.length,
        other_games_executed: unexpected.length,
        missing_named_games: missing,
        exact_identity_and_count: true,
      });
    },
  });
}

module.exports = Object.freeze({ parseExactNamedSubset, createExecutionGuard });
