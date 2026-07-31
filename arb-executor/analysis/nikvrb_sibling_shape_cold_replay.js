#!/usr/bin/env node
"use strict";

// One-event, score-free cold replay overlay. This module never imports or
// mutates live_v4. It consumes the frozen chronological NIK-VRB market clock
// and the frozen organ consultations, then exercises the candidate decision
// tree in receipt order. The mechanism is generic across a two-leg event; the
// named specimen is supplied by the builder/test fixture.

const CELL_WIDTH_CENTS = 5; // live_v4 significant-move cell width.
const T2_OPEN_MINUTES = 120; // existing aim-time-axis T2 boundary.
const ASK_REACH_DWELL_SECONDS = 10; // frozen quote-touch comparator threshold.

function numberOrNull(value) {
  if (value === "" || value === null || value === undefined) return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function parseTs(value) {
  const ms = Date.parse(value);
  if (!Number.isFinite(ms)) throw new Error(`invalid timestamp ${value}`);
  return ms / 1000;
}

function strictAfter(row, order) {
  return row.epoch > order.action_epoch;
}

function validBook(book) {
  return book && Number.isInteger(book.bid) && Number.isInteger(book.ask)
    && book.bid > 0 && book.ask <= 99 && book.bid <= book.ask;
}

function makerSafe(price, book) {
  return Number.isInteger(price) && price >= 1 && price <= 99
    && validBook(book) && price < book.ask;
}

const SHARP_BOOKS = ["pinnacle", "betfair_ex_eu", "matchbook"];

function resolveQuietBookAnchor({ book, externalSharp = null }) {
  if (externalSharp !== null) {
    const names = Array.isArray(externalSharp.sources)
      ? [...externalSharp.sources].sort() : [];
    const expected = [...SHARP_BOOKS].sort();
    if (names.length === expected.length
        && names.every((name, index) => name === expected[index])
        && Number.isFinite(externalSharp.fv_cents)
        && externalSharp.age_seconds >= 0
        && externalSharp.age_seconds <= 3600) {
      return {
        anchor_cents: Math.round(externalSharp.fv_cents),
        raw_anchor_cents: externalSharp.fv_cents,
        source: "EXTERNAL_SHARP_BLEND__PINNACLE_BETFAIR_MATCHBOOK",
        source_receipts: externalSharp.receipts || [],
      };
    }
  }
  if (!validBook(book) || book.ask - book.bid > 1) return null;
  const mid = (book.bid + book.ask) / 2;
  return {
    anchor_cents: Math.round(mid),
    raw_anchor_cents: mid,
    source: "OWN_LAWFUL_BBO_MID",
    source_receipts: [],
  };
}

function newPulseTracker() {
  return {
    NIK: { bid: null, ask: null, bid_down: false, ask_down: false, bid_trough: null, ask_trough: null, recurrences: 0, recurrences_by_side: { bid: 0, ask: 0 } },
    VRB: { bid: null, ask: null, bid_down: false, ask_down: false, bid_trough: null, ask_trough: null, recurrences: 0, recurrences_by_side: { bid: 0, ask: 0 } },
  };
}

function updatePulseTracker(trackers, row) {
  for (const leg of ["NIK", "VRB"]) {
    const tracker = trackers[leg];
    const book = row.books[leg];
    for (const side of ["bid", "ask"]) {
      const value = book[side];
      if (!Number.isInteger(value)) continue;
      const prior = tracker[side];
      const downKey = `${side}_down`;
      const troughKey = `${side}_trough`;
      if (Number.isInteger(prior) && value < prior) {
        tracker[downKey] = true;
        tracker[troughKey] = value;
      } else if (tracker[downKey] && value > tracker[troughKey]) {
        tracker.recurrences += 1;
        tracker.recurrences_by_side[side] += 1;
        tracker[downKey] = false;
        tracker[troughKey] = null;
      } else if (tracker[downKey] && value < tracker[troughKey]) {
        tracker[troughKey] = value;
      }
      tracker[side] = value;
    }
  }
}

function enrichRows(rawRows, capacityBySequence = {}) {
  const dwell = {
    NIK: { key: null, since: null },
    VRB: { key: null, since: null },
  };
  const lastReceipt = { NIK: null, VRB: null };
  const sideDwell = {
    NIK: { bid: { value: null, since: null }, ask: { value: null, since: null } },
    VRB: { bid: { value: null, since: null }, ask: { value: null, since: null } },
  };
  const pulses = newPulseTracker();
  return rawRows.map((raw) => {
    const epoch = parseTs(raw.timestamp_et);
    const books = {};
    for (const leg of ["NIK", "VRB"]) {
      const capacity = capacityBySequence[`${raw.sequence}|${leg}`] || null;
      books[leg] = {
        bid: numberOrNull(raw[`${leg}_bid`]),
        ask: numberOrNull(raw[`${leg}_ask`]),
        last: numberOrNull(raw[`${leg}_last`]),
      };
      if (capacity) {
        books[leg].ask_size = numberOrNull(capacity.ask_size);
        books[leg].ask_capacity_at_top = numberOrNull(capacity.ask_capacity_at_top);
        books[leg].ask_capacity_receipt = capacity.receipt;
      }
      books[leg].spread = Number.isInteger(books[leg].bid) && Number.isInteger(books[leg].ask)
        ? books[leg].ask - books[leg].bid : null;
      const key = `${books[leg].bid}|${books[leg].ask}`;
      if (key !== dwell[leg].key) {
        dwell[leg].key = key;
        dwell[leg].since = epoch;
      }
      books[leg].dwell_seconds = dwell[leg].since === null
        ? null : Number((epoch - dwell[leg].since).toFixed(6));
      for (const side of ["bid", "ask"]) {
        const tracker = sideDwell[leg][side];
        if (books[leg][side] !== tracker.value) {
          tracker.value = books[leg][side];
          tracker.since = epoch;
        }
        books[leg][`${side}_dwell_seconds`] = tracker.since === null
          ? null : Number((epoch - tracker.since).toFixed(6));
      }
      if (raw.event_kind === `PRINT_${leg}` && raw[`${leg}_print_trade_id`]) {
        lastReceipt[leg] = {
          receipt: raw[`${leg}_print_trade_id`],
          timestamp_et: raw.timestamp_et,
          price: numberOrNull(raw[`${leg}_print_price`]),
        };
      }
      books[leg].last_trade_provenance = raw.event_kind === `PRINT_${leg}`
        ? { state: "VERIFIED_NEW_EXECUTION", ...(lastReceipt[leg] || {}) }
        : lastReceipt[leg]
          ? { state: "CARRIED_VERIFIED_EXECUTION", ...lastReceipt[leg] }
          : { state: "UNAVAILABLE", receipt: null };
    }
    const row = {
      sequence: Number(raw.sequence),
      event_kind: raw.event_kind,
      timestamp_et: raw.timestamp_et,
      epoch,
      tminus_scheduled: raw.tminus_scheduled,
      tminus_scheduled_min: numberOrNull(raw.tminus_scheduled_min),
      tminus_bell: raw.tminus_actual_bell,
      books,
      print: null,
    };
    for (const leg of ["NIK", "VRB"]) {
      if (raw.event_kind === `PRINT_${leg}`) {
        row.print = {
          leg,
          price: numberOrNull(raw[`${leg}_print_price`]),
          size: numberOrNull(raw[`${leg}_print_size`]),
          receipt: raw[`${leg}_print_trade_id`] || `clock-sequence-${raw.sequence}`,
        };
      }
    }
    updatePulseTracker(pulses, row);
    row.pulse_recurrences = {
      NIK: pulses.NIK.recurrences,
      VRB: pulses.VRB.recurrences,
    };
    row.pulse_recurrences_by_side = {
      NIK: { ...pulses.NIK.recurrences_by_side },
      VRB: { ...pulses.VRB.recurrences_by_side },
    };
    return row;
  });
}

function consultationKey(epoch, leg) {
  return `${epoch}|${leg}`;
}

function buildConsultations(trace) {
  const out = new Map();
  for (const call of trace.consultations) {
    const p75 = call.atlas.depth_p25_p50_p75[2];
    const isRiser = call.orientation.riser === call.leg;
    const target = isRiser ? call.book.bid : Math.max(1, call.anchor.price - p75);
    out.set(consultationKey(parseTs(call.time_et), call.leg), {
      ...call,
      is_riser: isRiser,
      selected_target: target,
      signer: isRiser ? "ORIENTATION_RISER_NEAR_NOW" : "ORIENTATION_FALLER_DEEP",
    });
  }
  return out;
}

class ColdReplay {
  constructor({ trace, scenario, externalAnchors = {} }) {
    if (!new Set(["current", "tuned", "breathing", "ask_dwell"]).has(scenario)) throw new Error(`bad scenario ${scenario}`);
    this.trace = trace;
    this.scenario = scenario;
    this.tuned = scenario === "tuned" || scenario === "breathing" || scenario === "ask_dwell";
    this.breathing = scenario === "breathing" || scenario === "ask_dwell";
    this.askDwell = scenario === "ask_dwell";
    this.externalAnchors = externalAnchors;
    // Both scenarios inherit the already-validated orientation-conditioned
    // branch. The tuned scenario adds only sibling-conditioned faller patience.
    this.consultations = buildConsultations(trace);
    this.consumedConsultations = new Set();
    this.orders = { NIK: null, VRB: null };
    this.orderIntervals = [];
    this.fills = { NIK: null, VRB: null };
    this.material = [];
    this.ledger = [];
    this.shape = "UNRESOLVED";
    this.patience = null;
    this.firstDualBook = false;
    this.targetCeilings = { NIK: null, VRB: null };
    this.quietAnchors = { NIK: null, VRB: null };
    this.ratchetDown = { NIK: false, VRB: false };
    this.exactTouchArms = { NIK: null, VRB: null };
    this.capacityEvidenceAbsent = [];
    this.capacityAbsenceSeen = new Set();
  }

  _joint(row) {
    const visibleBook = (book) => this.askDwell ? book : Object.fromEntries(
      Object.entries(book).filter(([key]) => !["bid_dwell_seconds", "ask_dwell_seconds"].includes(key))
    );
    return {
      NIK: visibleBook(row.books.NIK),
      VRB: visibleBook(row.books.VRB),
      pair_bid_sum: Number.isInteger(row.books.NIK.bid) && Number.isInteger(row.books.VRB.bid)
        ? row.books.NIK.bid + row.books.VRB.bid : null,
      pair_ask_sum: Number.isInteger(row.books.NIK.ask) && Number.isInteger(row.books.VRB.ask)
        ? row.books.NIK.ask + row.books.VRB.ask : null,
    };
  }

  _shapeCalls() {
    if (this.shape === "UNRESOLVED") {
      return { VRB: "UNRESOLVED", NIK: "UNRESOLVED" };
    }
    if (this.shape === "ORIENTED") {
      return {
        VRB: "RISER__CLIMB_WITH_PULSES_EXPECTED_BEFORE_T2",
        NIK: "FALLER__INVERSE_SLIDE_EXPECTED_IN_T2",
      };
    }
    if (this.shape === "PATIENCE_ARMED") {
      return {
        VRB: "RISER__CLIMB_WITH_PULSES_RESOLVED",
        NIK: "FALLER__WAIT_FOR_ONE_LIVE_PRICE_CELL",
      };
    }
    if (this.shape === "FALLER_IMPULSE") {
      return {
        VRB: "RISER__RESOLVED_NO_CONTRADICTION",
        NIK: "FALLER__LATE_IMPULSE_CONFIRMED",
      };
    }
    return { VRB: "ENTRY_COMPLETE", NIK: "ENTRY_COMPLETE" };
  }

  _closeOrder(leg, row, reason) {
    const order = this.orders[leg];
    if (!order) return null;
    order.end_epoch = row.epoch;
    order.end_et = row.timestamp_et;
    order.end_sequence = row.sequence;
    order.end_reason = reason;
    this.orders[leg] = null;
    return order;
  }

  _place(leg, price, row, authority, reason) {
    if (!makerSafe(price, row.books[leg])) {
      throw new Error(`maker-unsafe ${leg} ${price} at ${row.timestamp_et} ${JSON.stringify(row.books[leg])}`);
    }
    const replaced = this._closeOrder(leg, row, `REPLACED_BY_${authority}`);
    const order = {
      scenario: this.scenario,
      leg,
      price,
      quantity: 5,
      action_epoch: row.epoch,
      action_et: row.timestamp_et,
      action_sequence: row.sequence,
      authority,
      reason,
      replaced_price: replaced ? replaced.price : null,
      end_epoch: null,
      end_et: null,
      end_sequence: null,
      end_reason: null,
    };
    this.orders[leg] = order;
    this.orderIntervals.push(order);
    return order;
  }

  _restingPrice(leg, row) {
    const ceiling = this.targetCeilings[leg];
    const book = row.books[leg];
    if (!Number.isInteger(ceiling) || !validBook(book)) return null;
    if (this.ratchetDown[leg] && !this.askDwell) {
      this.targetCeilings[leg] = Math.min(ceiling, book.bid);
    }
    if (this.askDwell) {
      return Math.max(1, Math.min(this.targetCeilings[leg], book.ask - 1));
    }
    return Math.max(1, Math.min(this.targetCeilings[leg], book.bid, book.ask - 1));
  }

  _quietAnchor(row, leg) {
    if (!this.breathing || this.orders[leg] || this.fills[leg]
        || this.quietAnchors[leg] || row.event_kind !== `BBO_${leg}`
        || row.books[leg].last_trade_provenance.state !== "UNAVAILABLE") return false;
    const externalSharp = this.externalAnchors[`${row.sequence}|${leg}`] || null;
    const anchor = resolveQuietBookAnchor({ book: row.books[leg], externalSharp });
    if (!anchor) return false;
    this.quietAnchors[leg] = {
      ...anchor,
      sequence: row.sequence,
      timestamp_et: row.timestamp_et,
      book: { bid: row.books[leg].bid, ask: row.books[leg].ask },
    };
    this.targetCeilings[leg] = anchor.anchor_cents;
    const price = this._restingPrice(leg, row);
    const order = this._place(leg, price, row, "QUIET_BOOK_ANCHOR", anchor.source);
    this._record(row, {
      material: true,
      leg,
      organ: "QUIET_BOOK_ANCHOR",
      organ_returns: {
        external_sharp_blend: externalSharp ? externalSharp.fv_cents : "NO_CALL",
        own_bbo_mid: (row.books[leg].bid + row.books[leg].ask) / 2,
        selected_anchor: anchor.anchor_cents,
        selected_source: anchor.source,
      },
      door_opened: "BOOK_PRICED_ENTRY_WITHOUT_TRUE_PRINT",
      signer: anchor.source,
      action: `PLACE_${leg}_${order.price}`,
      arithmetic: this.askDwell
        ? `round((${row.books[leg].bid}+${row.books[leg].ask})/2)=${anchor.anchor_cents}; min(anchor ${anchor.anchor_cents}, ask-1 ${row.books[leg].ask - 1})=${order.price}`
        : `round((${row.books[leg].bid}+${row.books[leg].ask})/2)=${anchor.anchor_cents}; min(${anchor.anchor_cents},${row.books[leg].bid})=${order.price}`,
      declined: "NO_CALL solely because last trade is unavailable",
      code_path: "resolveQuietBookAnchor -> ColdReplay._quietAnchor -> ColdReplay._place",
      english: `${leg} had no verified trade, but its lawful ${row.books[leg].bid}/${row.books[leg].ask} book supplied a ${anchor.raw_anchor_cents}-cent anchor. The maximum payable price became ${anchor.anchor_cents}; the maker order rested at ${order.price}.`,
    });
    return true;
  }

  _breathingTick(row, leg) {
    if (!this.breathing || row.event_kind !== `BBO_${leg}`
        || !this.orders[leg] || this.fills[leg] || !validBook(row.books[leg])) return false;
    const order = this.orders[leg];
    const book = row.books[leg];

    if (this.askDwell && book.ask <= order.price) {
      this._record(row, {
        material: false,
        leg,
        organ: "ASK_DWELL_GATE",
        door_opened: "WAIT_FOR_CAUSAL_ASK_RESIDENCY",
        signer: "OPPOSITE_ASK_ONLY",
        action: `HOLD_${leg}_${order.price}__ASK_DWELL_${book.ask_dwell_seconds}`,
        arithmetic: `ask ${book.ask} <= resting ${order.price}; dwell ${book.ask_dwell_seconds}<${ASK_REACH_DWELL_SECONDS}; output ${order.price}`,
        declined: "bid movement and zero-dwell fill credit",
        code_path: "ColdReplay._breathingTick:askDwellGate",
        english: `${leg}'s external ask was at or below the resting bid, but the ask had not yet met the frozen ${ASK_REACH_DWELL_SECONDS}-second residency threshold. The order stayed unchanged; bid churn had no authority.`,
      });
      return true;
    }

    if (!this.askDwell && book.ask === order.price) {
      const armed = this.exactTouchArms[leg];
      if (armed && row.epoch > armed.epoch) {
        this._fill(leg, row, {
          type: "ACTIVE_ASK_LIFT_CONFIRMATION",
          receipt: `clock-sequence-${row.sequence}`,
          evidence_price: book.ask,
          evidence_size: null,
          prior_arm_receipt: armed.receipt,
        });
        return true;
      }
      if (!armed) {
        this.exactTouchArms[leg] = {
          epoch: row.epoch,
          sequence: row.sequence,
          receipt: `clock-sequence-${row.sequence}`,
        };
        this._record(row, {
          material: true,
          leg,
          organ: "LIVE_TOUCH_EXECUTION_ARM",
          door_opened: "STRICTLY_LATER_ASK_LIFT_CONFIRMATION",
          signer: "OWN_ACTIVE_LIMIT_EQUALS_EXTERNAL_ASK",
          action: `ARM_${leg}_ASK_LIFT_${order.price}`,
          arithmetic: `resting ${order.price} = external ask ${book.ask}; price unchanged ${order.price}`,
          declined: "same-receipt fill credit",
          code_path: "ColdReplay._breathingTick:exactTouchArm",
          english: `${leg}'s previously resting ${order.price} bid met the external ask at ${book.ask}. The receipt armed an active ask lift but could not also fill the action; a strictly later receipt was required.`,
        });
        return true;
      }
    } else if (!this.askDwell) {
      this.exactTouchArms[leg] = null;
    }

    const desired = this._restingPrice(leg, row);
    if (!Number.isInteger(desired) || desired === order.price) return false;
    const before = order.price;
    const replacement = this._place(
      leg, desired, row, this.askDwell ? "LIVE_ASK_TOUCH" : "LIVE_BOOK_TOUCH",
      this.askDwell ? "target ceiling recomputed against the current external ask only" : "target ceiling recomputed against current external best bid"
    );
    this._record(row, {
      material: true,
      leg,
      organ: this.askDwell ? "LIVE_ASK_TOUCH" : "LIVE_BOOK_TOUCH",
      door_opened: "TOUCH_TRACKED_RESTING_EXPOSURE",
      signer: this.askDwell ? "CURRENT_EXTERNAL_BEST_ASK" : "CURRENT_EXTERNAL_BEST_BID",
      action: `REPRICE_${leg}_${before}_TO_${replacement.price}`,
      arithmetic: this.askDwell
        ? `min(ceiling ${this.targetCeilings[leg]}, ask-1 ${book.ask - 1})=${replacement.price}`
        : `min(ceiling ${this.targetCeilings[leg]}, bid ${book.bid}, ask-1 ${book.ask - 1})=${replacement.price}`,
      declined: `identity hold at stale ${before}`,
      code_path: "ColdReplay._breathingTick -> ColdReplay._restingPrice -> ColdReplay._place",
      english: `${leg}'s maximum payable price was ${this.targetCeilings[leg]}. The live book was ${book.bid}/${book.ask}, so the resting price recomputed to ${replacement.price}; the stale ${before} order was replaced on this tick.`,
    });
    return true;
  }

  _fillEvidence(row, leg) {
    const order = this.orders[leg];
    if (!order || !strictAfter(row, order)) return null;
    if (this.askDwell) {
      const book = row.books[leg];
      if (row.event_kind === `BBO_${leg}` && validBook(book)
          && book.ask <= order.price
          && book.ask_dwell_seconds >= ASK_REACH_DWELL_SECONDS) {
        const displayed = book.ask_capacity_at_top;
        return {
          type: "ASK_DWELL_REACHABLE",
          receipt: `clock-sequence-${row.sequence}`,
          evidence_price: book.ask,
          evidence_size: displayed,
          capacity_receipt: book.ask_capacity_receipt,
          capacity_status: Number.isFinite(displayed) && displayed >= order.quantity
            ? "PROVEN_FIVE_CONTRACT_CAPACITY" : "EVIDENCE_ABSENT",
          creditable: Number.isFinite(displayed) && displayed >= order.quantity,
          dwell_seconds: book.ask_dwell_seconds,
          dwell_threshold_seconds: ASK_REACH_DWELL_SECONDS,
        };
      }
      return null;
    }
    if (row.print && row.print.leg === leg && row.print.size > 0 && row.print.price <= order.price) {
      return { type: "PRICE_REACHED", receipt: row.print.receipt, evidence_price: row.print.price, evidence_size: row.print.size };
    }
    if (row.event_kind === `BBO_${leg}` && validBook(row.books[leg]) && row.books[leg].ask < order.price) {
      return { type: "STRICT_ASK_CERTAIN_FILL", receipt: `clock-sequence-${row.sequence}`, evidence_price: row.books[leg].ask, evidence_size: null };
    }
    return null;
  }

  _record(row, fields) {
    const record = {
      scenario: this.scenario,
      sequence: row.sequence,
      timestamp_et: row.timestamp_et,
      tminus_scheduled: row.tminus_scheduled,
      tminus_bell: row.tminus_bell,
      trigger: row.event_kind,
      joint_observation: this._joint(row),
      shapes: this._shapeCalls(),
      ...(this.breathing ? { active_orders_after: {
        NIK: this.orders.NIK ? this.orders.NIK.price : null,
        VRB: this.orders.VRB ? this.orders.VRB.price : null,
      }, target_ceilings_after: {
        NIK: this.targetCeilings.NIK,
        VRB: this.targetCeilings.VRB,
      } } : {}),
      ...fields,
    };
    this.ledger.push(record);
    if (fields.material) this.material.push(record);
    return record;
  }

  _fill(leg, row, evidence) {
    const order = this.orders[leg];
    const fill = {
      leg,
      price: order.price,
      quantity: 5,
      action_et: order.action_et,
      action_sequence: order.action_sequence,
      evidence_et: row.timestamp_et,
      evidence_sequence: row.sequence,
      evidence,
      strictly_later: strictAfter(row, order),
    };
    this.fills[leg] = fill;
    this._closeOrder(leg, row, `FILLED_${evidence.type}`);
    if (this.fills.NIK && this.fills.VRB) this.shape = "COMPLETE";
    return this._record(row, {
      material: true,
      organ: "FILL_ACCOUNTING",
      door_opened: this.fills.NIK && this.fills.VRB ? "PAIR_ENTRY_COMPLETE" : "SIBLING_REMAINS_OPEN",
      signer: evidence.type,
      action: `CREDIT_${leg}_FILL_${fill.price}`,
      ...(this.askDwell ? { arithmetic:
        `ask ${evidence.evidence_price} <= resting ${fill.price}; dwell ${evidence.dwell_seconds}>=${evidence.dwell_threshold_seconds}; displayed capacity ${evidence.evidence_size}>=${fill.quantity}; credit ${fill.quantity}@${fill.price}` } : {}),
      declined: "no cancel/reprice before fill credit",
      code_path: "ColdReplay._fillEvidence -> ColdReplay._fill",
      english: this.askDwell
        ? `${leg} had a five-contract bid resting at ${fill.price}. A strictly later external ask at ${evidence.evidence_price} with displayed capacity ${evidence.evidence_size} proved five-contract capacity, so the replay credited five at ${fill.price} before allowing any other action.`
        : `${leg} had a five-contract bid resting at ${fill.price}. A strictly later ${evidence.type === "PRICE_REACHED" ? `public print at ${evidence.evidence_price}` : `external ask at ${evidence.evidence_price}`} proved that price fillable, so the replay credited ${fill.price} before allowing any other action.`,
    });
  }

  _recordCapacityAbsent(leg, row, evidence) {
    const key = `${leg}|${row.sequence}|${this.orders[leg].price}`;
    if (this.capacityAbsenceSeen.has(key)) return;
    this.capacityAbsenceSeen.add(key);
    const receipt = {
      leg,
      sequence: row.sequence,
      timestamp_et: row.timestamp_et,
      resting_price: this.orders[leg].price,
      ask_price: evidence.evidence_price,
      displayed_ask_capacity: evidence.evidence_size,
      required_quantity: this.orders[leg].quantity,
      status: "EVIDENCE_ABSENT",
      capacity_receipt: evidence.capacity_receipt,
    };
    this.capacityEvidenceAbsent.push(receipt);
    this._record(row, {
      material: true,
      leg,
      organ: "FILL_CAPACITY_GATE",
      door_opened: "PRICE_REACH_RECORDED_WITHOUT_FILL_CREDIT",
      signer: "EVIDENCE_ABSENT",
      action: `NO_CREDIT_${leg}_${this.orders[leg].price}__EVIDENCE_ABSENT`,
      arithmetic: `ask ${evidence.evidence_price} <= resting ${this.orders[leg].price}; dwell ${evidence.dwell_seconds}>=${evidence.dwell_threshold_seconds}; displayed capacity ${evidence.evidence_size === null ? "UNKNOWN" : evidence.evidence_size}<required ${this.orders[leg].quantity}; credit 0`,
      declined: "five-contract fill assignment without displayed ask capacity",
      code_path: "ColdReplay._fillEvidence -> ColdReplay._recordCapacityAbsent",
      english: `${leg}'s price was ask-reachable, but the contemporaneous displayed ask capacity was ${evidence.evidence_size === null ? "unavailable" : evidence.evidence_size}. The replay recorded EVIDENCE_ABSENT and assigned no contracts.`,
    });
  }

  process(row) {
    for (const leg of ["NIK", "VRB"]) {
      const evidence = this._fillEvidence(row, leg);
      if (evidence) {
        if (evidence.creditable === false) {
          this._recordCapacityAbsent(leg, row, evidence);
        } else {
          this._fill(leg, row, evidence);
        }
        return;
      }
    }

    if (row.event_kind === "GATE_OPEN") {
      this._record(row, {
        material: true,
        organ: "WINDOW_GATE",
        door_opened: "OBSERVATION_ONLY",
        signer: "NO_CALL",
        action: "NO_ORDER__BOOKS_UNAVAILABLE",
        declined: "all entry pricing",
        code_path: "ColdReplay.process:GATE_OPEN",
        english: "Window 1 opened with neither book nor a verified trade. The OS could observe the clock only, so it made no price call and placed nothing.",
      });
      return;
    }

    if (!this.firstDualBook && validBook(row.books.NIK) && validBook(row.books.VRB)) {
      this.firstDualBook = true;
      this._record(row, {
        material: true,
        organ: "DISCOVERY_GATE",
        door_opened: "WAIT_FOR_TRUE_PRINT_ANCHOR",
        signer: "NO_CALL",
        action: "NO_ORDER__NO_VERIFIED_LAST_TRADE",
        declined: "BBO-only conception",
        code_path: "ColdReplay.process:firstDualBook",
        english: "Both books were visible, but neither leg had a receipt-identified true-print anchor. The discovery gate kept pricing unreachable instead of treating a quote as a trade.",
      });
      return;
    }

    for (const quietLeg of ["NIK", "VRB"]) {
      if (this._quietAnchor(row, quietLeg)) return;
    }

    let leg = row.event_kind.endsWith("_NIK") ? "NIK"
      : row.event_kind.endsWith("_VRB") ? "VRB" : null;
    const pendingCall = [...this.consultations.entries()].find(([candidateKey, candidate]) => {
      if (this.consumedConsultations.has(candidateKey)) return false;
      if (!candidateKey.startsWith(`${row.epoch}|`)) return false;
      const book = row.books[candidate.leg];
      return book.bid === candidate.book.bid && book.ask === candidate.book.ask
        && book.last === candidate.book.last_trade;
    });
    const key = pendingCall ? pendingCall[0] : null;
    const call = pendingCall ? pendingCall[1] : null;
    if (call && !this.consumedConsultations.has(key)) {
      this.consumedConsultations.add(key);
      leg = call.leg;
      if (this.fills[leg]) {
        this._record(row, {
          material: false,
          organ: "FILLED_PHASE_GATE",
          door_opened: "NONE",
          signer: "FILLED_PHASE_LOCK",
          action: `NO_CALL_${leg}_ALREADY_FILLED`,
          declined: `consultation target ${call.selected_target}`,
          code_path: "ColdReplay.process:consultationFilledGate",
          english: `${leg} was already filled, so the later consultation was observed but could not reopen an entry path.`,
        });
        return;
      }
      this.shape = "ORIENTED";
      let selectedTarget = call.selected_target;
      let finalSigner = call.signer;
      let priorOrder = null;
      let order;
      if (this.breathing) {
        const existingCeiling = this.targetCeilings[leg];
        this.targetCeilings[leg] = Number.isInteger(existingCeiling)
          ? Math.min(existingCeiling, call.selected_target) : call.selected_target;
        selectedTarget = this._restingPrice(leg, row);
        finalSigner = selectedTarget === call.selected_target
          ? call.signer : "LIVE_BOOK_ANCHOR_CEILING";
        priorOrder = this.orders[leg];
        order = priorOrder && priorOrder.price === selectedTarget
          ? priorOrder
          : this._place(leg, selectedTarget, row, finalSigner, "frozen organ consultation plus live-book ceiling");
      } else {
        order = this._place(leg, call.selected_target, row, call.signer, "frozen organ consultation");
      }
      const organs = {
        fresh_print_anchor: `${call.anchor.source}:${call.anchor.price}`,
        orientation: `${call.orientation.riser}_RISER conviction=${call.orientation.conviction}`,
        atlas: `${call.atlas.aim} (p50); p75=${call.atlas.depth_p25_p50_p75[2]}`,
        cohort: `dip_p50=${call.cohort.dip_p50}`,
        contention: `${call.contention.verdict}:${call.contention.best_pct}%`,
        pair: `${call.pair.verdict}:${call.pair.combined_at_path}`,
        flow: `${call.flow.bucket}; prints30m=${call.flow.prints_30m}`,
      };
      this._record(row, {
        material: true,
        organ: "INITIAL_ENTRY_TREE",
        organ_returns: organs,
        door_opened: call.is_riser ? "RISER_NEAR_NOW" : "FALLER_DEEP_CAST",
        signer: finalSigner,
        action: this.breathing && priorOrder && priorOrder.price === selectedTarget
          ? `HOLD_${leg}_${selectedTarget}`
          : `${order.replaced_price === null ? "PLACE" : "REPRICE"}_${leg}_${order.price}`,
        ...(this.breathing ? { arithmetic: this.askDwell
          ? `min(organ ${call.selected_target}, ceiling ${this.targetCeilings[leg]}, ask-1 ${row.books[leg].ask - 1})=${selectedTarget}`
          : `min(organ ${call.selected_target}, ceiling ${this.targetCeilings[leg]}, bid ${row.books[leg].bid}, ask-1 ${row.books[leg].ask - 1})=${selectedTarget}` } : {}),
        declined: call.is_riser ? `ATLAS ${call.atlas.aim}` : `ATLAS p50 ${call.atlas.aim}`,
        code_path: "buildConsultations -> ColdReplay._place",
        english: `${leg}'s verified anchor was ${call.anchor.price}. Orientation called VRB the riser, which made ${leg} the ${call.is_riser ? "near-now riser" : "deep-cast faller"}. ${finalSigner} signed ${order.price}; the replay ${this.breathing && priorOrder && priorOrder.price === selectedTarget ? `held ${selectedTarget}` : order.replaced_price === null ? `placed ${order.price}` : `moved from ${order.replaced_price} to ${order.price}`} and declined the competing ATLAS price.`,
      });
      return;
    }

    if (this.tuned && !this.patience && !this.fills.NIK && this.fills.VRB
        && row.tminus_scheduled_min !== null
        && row.tminus_scheduled_min <= T2_OPEN_MINUTES
        && row.tminus_scheduled_min > 60
        && (this.askDwell ? row.pulse_recurrences_by_side.VRB.ask : row.pulse_recurrences.VRB) > 0
        && row.books.VRB.bid > this.fills.VRB.price
        && validBook(row.books.NIK)) {
      const cancelled = this._closeOrder("NIK", row, "SIBLING_RISER_SHAPE_RESOLVED");
      this.patience = {
        armed_epoch: row.epoch,
        armed_et: row.timestamp_et,
        arm_sequence: row.sequence,
        arm_bid: row.books.NIK.bid,
        arm_ask: row.books.NIK.ask,
        sibling_bid: row.books.VRB.bid,
        sibling_ask: row.books.VRB.ask,
        sibling_recurrences: this.askDwell ? row.pulse_recurrences_by_side.VRB.ask : row.pulse_recurrences.VRB,
        cancelled_price: cancelled ? cancelled.price : null,
      };
      if (this.breathing) this.ratchetDown.NIK = true;
      this.shape = "PATIENCE_ARMED";
      this._record(row, {
        material: true,
        ...(this.askDwell ? { leg: "NIK" } : {}),
        organ: "SIBLING_REALIZED_SHAPE",
        organ_returns: {
          orientation: "VRB_RISER/NIK_FALLER",
          timing_axis: "T2_OPEN",
          sibling_live_book: `${row.books.VRB.bid}/${row.books.VRB.ask}`,
          sibling_completed_quote_recurrences: this.askDwell ? row.pulse_recurrences_by_side.VRB.ask : row.pulse_recurrences.VRB,
          sibling_above_fill: row.books.VRB.bid - this.fills.VRB.price,
        },
        door_opened: "FALLER_PATIENCE_WAIT_FOR_ONE_LIVE_PRICE_CELL",
        signer: "JOINT_SHAPE_AUTHORITY",
        action: `CANCEL_NIK_${cancelled ? cancelled.price : "NONE"}__WAIT`,
        ...(this.askDwell ? { arithmetic:
          `VRB ask recurrences ${row.pulse_recurrences_by_side.VRB.ask}>0; VRB bid ${row.books.VRB.bid}>fill ${this.fills.VRB.price}; cancel ${cancelled ? cancelled.price : "EMPTY"}->EMPTY` } : {}),
        declined: "accepting the still-lawful 21 before the late inverse slide",
        code_path: "ColdReplay.process:siblingShapePatienceArm",
        english: `At the first receipt inside the existing T2 clock bucket, VRB was ${row.books.VRB.bid}/${row.books.VRB.ask}, still above its 69 fill after ${this.askDwell ? row.pulse_recurrences_by_side.VRB.ask : row.pulse_recurrences.VRB} completed ${this.askDwell ? "ask-side " : ""}quote recurrences. The riser path was now realized, so the joint-shape organ inferred that inverse faller NIK still had room. It cancelled ${cancelled ? cancelled.price : "no order"} and waited instead of letting ATLAS depth finish the decision.`,
      });
      return;
    }

    if (this.askDwell && this.patience && !this.orders.NIK && !this.fills.NIK
        && row.event_kind === "BBO_NIK" && validBook(row.books.NIK)) {
      const askDrop = this.patience.arm_ask - row.books.NIK.ask;
      const dwell = row.books.NIK.ask_dwell_seconds;
      const siblingStillSupports = validBook(row.books.VRB)
        && row.books.VRB.ask > this.fills.VRB.price;
      if (askDrop >= CELL_WIDTH_CENTS
          && dwell >= ASK_REACH_DWELL_SECONDS
          && siblingStillSupports) {
        const target = row.books.NIK.ask - 1;
        this.targetCeilings.NIK = target;
        this.ratchetDown.NIK = true;
        const order = this._place(
          "NIK", target, row, "ASK_DWELL_PATIENCE_RELEASE",
          `opposite ask fell a full cell and persisted ${ASK_REACH_DWELL_SECONDS} seconds`
        );
        this.shape = "FALLER_IMPULSE";
        this._record(row, {
          material: true,
          organ: "ASK_DWELL_PATIENCE_RELEASE",
          organ_returns: {
            arm_ask: this.patience.arm_ask,
            current_ask: row.books.NIK.ask,
            ask_drop: askDrop,
            ask_dwell_seconds: dwell,
            minimum_dwell_seconds: ASK_REACH_DWELL_SECONDS,
            mechanical_cell_width: CELL_WIDTH_CENTS,
            sibling_book: `${row.books.VRB.bid}/${row.books.VRB.ask}`,
          },
          door_opened: "ASK_MINUS_ONE_MAKER_EXPOSURE",
          signer: "PERSISTENT_EXTERNAL_ASK",
          action: `PLACE_NIK_${order.price}`,
          arithmetic: `arm ask ${this.patience.arm_ask}-current ask ${row.books.NIK.ask}=${askDrop}>=${CELL_WIDTH_CENTS}; dwell ${dwell}>=${ASK_REACH_DWELL_SECONDS}; ask-1=${order.price}`,
          declined: "all bid-side episodes and the 7-second 24 / 2-second 23 asks",
          code_path: "ColdReplay.process:askDwellPatienceRelease -> ColdReplay._place",
          english: `NIK's opposite ask, not its bid, had fallen ${askDrop} cents and persisted ${dwell} seconds. The ask-side evidence cleared the pre-existing ten-second comparator, so the current ask minus one signed a maker bid at ${order.price}.`,
        });
        return;
      }
    }

    if (!this.askDwell && this.tuned && this.patience && !this.orders.NIK && !this.fills.NIK
        && row.event_kind === "BBO_NIK" && validBook(row.books.NIK)) {
      const bidDrop = this.patience.arm_bid - row.books.NIK.bid;
      const siblingStillSupports = validBook(row.books.VRB)
        && row.books.VRB.bid > this.fills.VRB.price;
      if (bidDrop >= CELL_WIDTH_CENTS && siblingStillSupports) {
        const target = row.books.NIK.bid;
        if (this.breathing) {
          this.targetCeilings.NIK = target;
          this.ratchetDown.NIK = true;
        }
        const order = this._place("NIK", target, row, "SIBLING_SHAPE_PATIENCE_RELEASE", "one live five-cent cell lower with sibling riser intact");
        this.shape = "FALLER_IMPULSE";
        this._record(row, {
          material: true,
          organ: "FALLER_PATIENCE_RELEASE",
          organ_returns: {
            arm_bid: this.patience.arm_bid,
            current_bid: row.books.NIK.bid,
            bid_drop: bidDrop,
            mechanical_cell_width: CELL_WIDTH_CENTS,
            sibling_book: `${row.books.VRB.bid}/${row.books.VRB.ask}`,
          },
          door_opened: "CURRENT_BID_MAKER_EXPOSURE",
          signer: "LIVE_NIK_BID",
          action: `PLACE_NIK_${order.price}`,
          declined: "ATLAS 21 and any future lower price not yet observed",
          code_path: "ColdReplay.process:fallerPatienceRelease -> ColdReplay._place",
          english: `NIK's live bid had fallen one complete five-cent price cell, from ${this.patience.arm_bid} to ${row.books.NIK.bid}, while VRB still held ${row.books.VRB.bid}/${row.books.VRB.ask} above its 69 fill. That receipt ended patience. The current NIK bid, not a depth table, signed a maker order at ${order.price}; unseen lower prices remained unreachable.`,
        });
        return;
      }
    }

    if (leg && this._breathingTick(row, leg)) return;

    let organ = "ROUTER";
    let action = "NO_CALL__NO_ENTRY_TRIGGER";
    let declined = "new entry placement";
    let codePath = "ColdReplay.process:defaultNoCall";
    let english = "The receipt updated market state but opened no new entry door, so the current state was preserved.";
    if (this.fills.NIK && this.fills.VRB) {
      organ = "FILLED_PHASE_GATE";
      action = "NO_CALL__PAIR_ENTRY_COMPLETE";
      declined = "all further Window-1 entry actions";
      codePath = "ColdReplay.process:pairCompleteLock";
      english = "Both five-contract entries were already credited. The entry tree stayed locked; this receipt could update market memory but could not create a re-buy.";
    } else if (leg && this.fills[leg]) {
      organ = "FILLED_PHASE_GATE";
      action = `NO_CALL__${leg}_ENTRY_COMPLETE`;
      declined = "re-entry on the filled leg";
      codePath = "ColdReplay.process:legFilledLock";
      english = `${leg} was already filled, so the entry router recorded the new book/tape state but did not reopen that leg.`;
    } else if (this.tuned && this.patience && !this.orders.NIK && !this.fills.NIK) {
      const drop = validBook(row.books.NIK) ? this.patience.arm_bid - row.books.NIK.bid : null;
      organ = "FALLER_PATIENCE";
      action = "HOLD_NO_ORDER__WAIT_FOR_FULL_CELL";
      declined = "premature NIK exposure";
      codePath = "ColdReplay.process:fallerPatienceHold";
      english = `NIK remained unexposed because the observed bid drop was ${drop === null ? "unavailable" : `${drop} cents`}, short of the existing five-cent cell release or without a valid confirming sibling book.`;
    } else if (leg && this.orders[leg]) {
      organ = this.scenario === "current" && leg === "VRB" ? "QUIET_STAIRCASE_HOLD" : "RESTING_ORDER_MANAGER";
      action = `HOLD_${leg}_${this.orders[leg].price}`;
      declined = "cancel/reprice without a named trigger";
      codePath = "ColdReplay.process:restingHold";
      english = `${leg}'s ${this.orders[leg].price} bid remained maker-safe and no named state transition fired, so the OS preserved the resting order and its queue position.`;
    }
    this._record(row, {
      material: false,
      organ,
      door_opened: "STATE_PRESERVED",
      signer: organ,
      action,
      declined,
      code_path: codePath,
      english,
    });
  }

  finish(lastRow) {
    for (const leg of ["NIK", "VRB"]) {
      if (this.orders[leg]) this._closeOrder(leg, lastRow, "WINDOW1_END");
    }
    const counts = {};
    for (const row of this.ledger) counts[row.action] = (counts[row.action] || 0) + 1;
    return {
      scenario: this.scenario,
      fills: this.fills,
      order_intervals: this.orderIntervals,
      material_decisions: this.material,
      decision_ledger: this.ledger,
      action_counts: counts,
      patience: this.patience,
      target_ceilings: this.targetCeilings,
      quiet_anchors: this.quietAnchors,
      ...(this.askDwell ? { capacity_evidence_absent: this.capacityEvidenceAbsent } : {}),
    };
  }
}

function runColdReplay({ rawRows, trace, scenario, externalAnchors = {}, capacityBySequence = {} }) {
  const rows = enrichRows(rawRows, capacityBySequence);
  const replay = new ColdReplay({ trace, scenario, externalAnchors });
  for (const row of rows) replay.process(row);
  return replay.finish(rows[rows.length - 1]);
}

module.exports = {
  ASK_REACH_DWELL_SECONDS,
  CELL_WIDTH_CENTS,
  T2_OPEN_MINUTES,
  ColdReplay,
  enrichRows,
  makerSafe,
  parseTs,
  resolveQuietBookAnchor,
  runColdReplay,
  SHARP_BOOKS,
  validBook,
};
