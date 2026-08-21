"use strict";

function lawfulCent(value) {
  return Number.isInteger(value) && value >= 1 && value <= 99;
}

function latestStrictlyBefore(rows, timestampEpoch) {
  let lo = 0;
  let hi = rows.length - 1;
  let hit = -1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (rows[mid].timestamp_epoch < timestampEpoch) {
      hit = mid;
      lo = mid + 1;
    } else {
      hi = mid - 1;
    }
  }
  return hit >= 0 ? rows[hit] : null;
}

function orderAfterDecision(row) {
  if (!row) return null;
  if (["PLACE_REST", "REPRICE_REST"].includes(row.final_action)) {
    return lawfulCent(row.final_target_cents) ? row.final_target_cents : null;
  }
  if (["CANCEL_REST", "TAKE"].includes(row.final_action)) return null;
  return lawfulCent(row.order_before_cents) ? row.order_before_cents : null;
}

function restAt(rows, timestampEpoch, siblingCredit) {
  const decision = latestStrictlyBefore(rows, timestampEpoch);
  let target = orderAfterDecision(decision);
  let cap = null;
  if (siblingCredit && Number.isFinite(siblingCredit.fill_timestamp_epoch)
      && siblingCredit.fill_timestamp_epoch < timestampEpoch) {
    cap = 99 - siblingCredit.entry_cents;
    if (lawfulCent(target) && target > cap) target = lawfulCent(cap) ? cap : null;
  }
  return {
    target_cents: target,
    source_receipt: decision?.receipt ?? null,
    source_timestamp_epoch: decision?.timestamp_epoch ?? null,
    source_action: decision?.final_action ?? null,
    source_reason: decision?.reason ?? null,
    pair_cap_cents: cap,
    joint_license_complete: decision?.joint_license?.complete === true,
    machine_state: decision?.read?.state ?? null,
    quote_path_state: decision?.read?.quote_path_state ?? null,
    pressure_state: decision?.read?.pressure_state ?? null,
  };
}

function firstLaterTradeAtOrBelow(prints, timestampEpoch, targetCents, receipt) {
  return prints.find((row) =>
    row.timestamp_epoch > timestampEpoch
      && row.receipt !== receipt
      && lawfulCent(row.price_cents)
      && row.price_cents <= targetCents) ?? null;
}

function enumerateTrueDivots({
  prints,
  ownBooks,
  siblingBooks,
  decisionRows,
  siblingCredit,
  observationalArmAt = () => null,
}) {
  const sortedPrints = [...prints].sort((a, b) =>
    a.timestamp_epoch - b.timestamp_epoch || String(a.receipt).localeCompare(String(b.receipt)));
  let runningHigh = null;
  let pending = null;
  const divots = [];
  for (const row of sortedPrints) {
    const decision = latestStrictlyBefore(decisionRows, row.timestamp_epoch);
    const ownBook = latestStrictlyBefore(ownBooks, row.timestamp_epoch);
    const siblingBook = latestStrictlyBefore(siblingBooks, row.timestamp_epoch);
    if (pending && row.timestamp_epoch > pending.trough.timestamp_epoch
        && row.price_cents > pending.trough.price_cents) {
      const resumeOwnBook = ownBook;
      const resumeSiblingBook = siblingBook;
      const rest = restAt(decisionRows, row.timestamp_epoch, siblingCredit);
      const pairArmed = Boolean(siblingCredit
        && siblingCredit.fill_timestamp_epoch < row.timestamp_epoch);
      const slideTarget = resumeOwnBook?.bid_cents ?? null;
      const capLawful = lawfulCent(slideTarget)
        && (!lawfulCent(rest.pair_cap_cents) || slideTarget <= rest.pair_cap_cents);
      const sanityLawful = lawfulCent(slideTarget)
        && lawfulCent(resumeOwnBook?.ask_cents)
        && slideTarget < resumeOwnBook.ask_cents;
      const jointStateLive = Boolean(resumeOwnBook && resumeSiblingBook
        && lawfulCent(resumeOwnBook.bid_cents) && lawfulCent(resumeOwnBook.ask_cents)
        && lawfulCent(resumeSiblingBook.bid_cents) && lawfulCent(resumeSiblingBook.ask_cents));
      const laterTrade = capLawful && sanityLawful && jointStateLive && pairArmed
        ? firstLaterTradeAtOrBelow(sortedPrints, row.timestamp_epoch, slideTarget, row.receipt)
        : null;
      divots.push({
        definition: "F_V53_028_TRUE_DIVOT_CAUSALLY_RECOGNIZED_ON_LATER_RESUME",
        trough: pending.trough,
        recognition: {
          timestamp_epoch: row.timestamp_epoch,
          receipt: row.receipt,
          trade_id: row.trade_id,
          price_cents: row.price_cents,
          size: row.size,
          taker_side: row.taker_side,
          taker_book_side: row.taker_book_side,
        },
        joint_observation_at_recognition: {
          own: resumeOwnBook,
          sibling: resumeSiblingBook,
          last_traded_cents: row.price_cents,
        },
        machine_read_at_recognition: {
          state: decision?.read?.state ?? null,
          quote_path_state: decision?.read?.quote_path_state ?? null,
          pressure_state: decision?.read?.pressure_state ?? null,
          source_receipt: decision?.receipt ?? null,
        },
        rest_at_recognition: rest,
        arm_state: {
          pair_armed_by_sibling_credit: pairArmed,
          sibling_credit: siblingCredit ?? null,
          observational_riser_arm: observationalArmAt(row.timestamp_epoch),
        },
        slide_counterfactual: {
          target_best_bid_cents: slideTarget,
          rest_was_elsewhere: rest.target_cents !== slideTarget,
          cap_lawful: capLawful,
          sanity_lawful: sanityLawful,
          joint_state_live: jointStateLive,
          strictly_later_trade_required: true,
          would_slide_to_best_bid_trade: Boolean(laterTrade),
          first_strictly_later_trade_at_or_below_target: laterTrade,
          failure_reason: laterTrade ? null
            : !pairArmed ? "PAIR_NOT_ARMED_AT_DIVOT_RECOGNITION"
              : !jointStateLive ? "JOINT_BOOK_NOT_LIVE_AT_RECOGNITION"
                : !capLawful ? "BEST_BID_ABOVE_PAIR_CAP_OR_INVALID"
                  : !sanityLawful ? "BEST_BID_FAILED_POST_ONLY_SANITY"
                    : "NO_STRICTLY_LATER_TRUE_TRADE_AT_OR_BELOW_BEST_BID",
        },
      });
      pending = null;
    }
    const strengthening = decision?.read?.state === "RISING"
      && lawfulCent(runningHigh) && lawfulCent(row.price_cents)
      && row.price_cents < runningHigh;
    const jointLive = ownBook && siblingBook
      && lawfulCent(ownBook.bid_cents) && lawfulCent(ownBook.ask_cents)
      && lawfulCent(siblingBook.bid_cents) && lawfulCent(siblingBook.ask_cents);
    const tradeBacked = ownBook && lawfulCent(row.price_cents)
      && row.price_cents <= ownBook.bid_cents;
    if (strengthening && jointLive && tradeBacked) {
      const candidate = {
        timestamp_epoch: row.timestamp_epoch,
        receipt: row.receipt,
        trade_id: row.trade_id,
        price_cents: row.price_cents,
        size: row.size,
        taker_side: row.taker_side,
        taker_book_side: row.taker_book_side,
        running_prior_trade_high_cents: runningHigh,
        machine_state: decision.read.state,
        machine_state_receipt: decision.receipt,
        joint_observation: { own: ownBook, sibling: siblingBook, last_traded_cents: row.price_cents },
        trade_backed_at_or_below_best_bid: true,
        tradability_live: true,
      };
      if (!pending || candidate.price_cents < pending.trough.price_cents) pending = { trough: candidate };
    }
    runningHigh = runningHigh === null ? row.price_cents : Math.max(runningHigh, row.price_cents);
  }
  return divots;
}

function classifyDeadSibling(divots) {
  if (!divots.length) return "ZERO_TRUE_DIVOTS";
  if (divots.some((row) => row.slide_counterfactual.rest_was_elsewhere
      && row.slide_counterfactual.would_slide_to_best_bid_trade)) {
    return "DIVOTS_EXISTED_REST_ELSEWHERE";
  }
  return "DIVOTS_EXISTED_SLIDE_WOULD_NOT_TRADE";
}

module.exports = {
  lawfulCent,
  latestStrictlyBefore,
  orderAfterDecision,
  restAt,
  enumerateTrueDivots,
  classifyDeadSibling,
};
