"""Eleven-block field definitions and pure receipt-local derived features.

This is not a bench launcher. Integrators must bind recovered source hashes,
unchanged-FIRST Q and exact prior receipt clocks before using these functions.
"""
from __future__ import annotations

import math
from bisect import bisect_left, bisect_right

from feature_panel_book_recovery import (imbalance, visible_depth, snapshot_residual,
                                        spike_reversion, usable_book, book_invalid_reason)


ADDED_BLOCKS = ('BOOK_IMBALANCE','QUEUE_ESTIMATE','SPREAD_BEHAVIOR','SPIKE_REVERSION','MAKER')
NEW_FIELDS = (
    ('book_imbalance_top','BOOK_IMBALANCE','(bid top size - ask top size) / total top size'),
    ('book_imbalance_five','BOOK_IMBALANCE','(five bid sizes - five ask sizes) / total five-level size'),
    ('book_imbalance_top_change','BOOK_IMBALANCE','Top imbalance minus its state at the previous original receipt'),
    ('book_imbalance_five_change','BOOK_IMBALANCE','Five-level imbalance minus its state at the previous original receipt'),
    ('displayed_depth_at_first_q','QUEUE_ESTIMATE','Displayed bid depth at unchanged FIRST Q; not known queue priority'),
    ('queue_decay_per_minute','QUEUE_ESTIMATE','Previous minus current displayed bid depth at the SAME current FIRST Q, divided by prior-receipt minutes'),
    ('behavior_spread_cents','SPREAD_BEHAVIOR','Current library ask minus bid, duplicated spread retained as ordered'),
    ('spread_rate_per_minute','SPREAD_BEHAVIOR','Current minus previous original-receipt library spread divided by elapsed minutes'),
    ('completed_minute_largest_move','SPIKE_REVERSION','Signed largest absolute consecutive positive-print move in the latest completed minute; earliest tie'),
    ('completed_minute_retraced_share','SPIKE_REVERSION','Retracement of that signed move by the completed minute close; no clipping of extension or overshoot'),
    ('maker_bid_net_adds','MAKER','Sum positive net maker residuals at bid levels observable at both consecutive snapshots'),
    ('maker_bid_net_pulls','MAKER','Absolute sum negative net maker residuals at those bid levels'),
    ('maker_ask_net_adds','MAKER','Sum positive net maker residuals at ask levels observable at both consecutive snapshots'),
    ('maker_ask_net_pulls','MAKER','Absolute sum negative net maker residuals at those ask levels'),
    ('maker_refill_below_bid','MAKER','Positive net additions / executed contracts below the previous bid, same visible levels and interval; zero denominator missing'),
    ('maker_refill_above_ask','MAKER','Positive net additions / executed contracts above the previous ask, same visible levels and interval; zero denominator missing'),
)


def previous_receipt(pair_native_epochs, atlas_epochs, epoch, first_epoch):
    """Prior original replay receipt, NOT the prior sampled atlas gate."""
    choices=[]
    for rows in (pair_native_epochs,atlas_epochs):
        index=bisect_left(rows,epoch)-1
        if index>=0 and rows[index]>=first_epoch:
            choices.append(rows[index])
    return max(choices) if choices else None


def asof_book(books,epochs,epoch):
    if epoch is None:
        return None
    index=bisect_right(epochs,epoch)-1
    return books[index] if index>=0 else None


def finite(value):
    return value is not None and math.isfinite(float(value))


def difference(a,b):
    return a-b if finite(a) and finite(b) else None


def rate(change,minutes):
    return change/minutes if finite(change) and finite(minutes) and minutes>0 else None


def spread(bid,ask):
    return ask-bid if finite(bid) and finite(ask) and bid<=ask else None


def maker_summary(previous,current,prints,*,full=False,reference_price=None,known_at_epoch=None):
    result={name:None for name,block,definition in NEW_FIELDS if block=='MAKER'}
    if previous is None or current is None:
        return result,dict(reason='NO_CONSECUTIVE_VISIBLE_SNAPSHOTS')
    interval_invalid=book_invalid_reason(previous) or book_invalid_reason(current)
    rows=snapshot_residual(previous,current,prints,full=full,known_at_epoch=known_at_epoch)
    for side in ('bid','ask'):
        values=[r for r in rows if r[0]==side]
        # Off-screen levels are omitted from the measurement's explicitly
        # shared visibility domain, not treated as empty queues.
        visible=[r for r in values if visible_depth(previous[1 if side=='bid' else 2],r[1],side,full=full) is not None
            and visible_depth(current[1 if side=='bid' else 2],r[1],side,full=full) is not None]
        if not interval_invalid and visible and all(r[2] is not None for r in visible):
            result['maker_'+side+'_net_adds']=sum(max(0,r[2]) for r in visible)
            result['maker_'+side+'_net_pulls']=sum(max(0,-r[2]) for r in visible)
        levels=previous[1 if side=='bid' else 2]
        occupied=[p for p,q in levels if finite(p) and finite(q) and q>0]
        if not occupied:
            continue
        top=max(occupied) if side=='bid' else min(occupied)
        region=[r for r in visible if (r[1]<top if side=='bid' else r[1]>top)]
        if not interval_invalid and region and all(r[2] is not None and r[3] is not None for r in region):
            denominator=sum(r[3] for r in region)
            if denominator>0:
                result['maker_refill_below_bid' if side=='bid' else 'maker_refill_above_ask']=sum(max(0,r[2]) for r in region)/denominator
    per_level=[]
    for side,price,net,executed in rows:
        index=1 if side=='bid' else 2
        before=visible_depth(previous[index],price,side,full=full)
        after=visible_depth(current[index],price,side,full=full)
        per_level.append(dict(side=side,yes_price_cents=price,
            start_displayed_contracts=None if before is None else float(before),
            end_displayed_contracts=None if after is None else float(after),
            on_book_executed_contracts=executed,net_displayed_residual=net,
            distance_from_price_cents=difference(price,reference_price),
            distance_reference_price_cents=reference_price if finite(reference_price) else None,
            status='AVAILABLE' if net is not None else 'STORE_SILENT',
            missing_reason=None if net is not None else interval_invalid or
                ('LEVEL_NOT_VISIBLE_AT_BOTH_SNAPSHOTS' if before is None or after is None
                 else 'UNRESOLVED_EXECUTION_SIDE_BLOCK_STATUS_OR_INTERVAL_ORDER')))
    return result,dict(interval=[previous[0],current[0]],levels=rows,per_level=per_level,
        known_at_receipt_epoch=current[0] if known_at_epoch is None else known_at_epoch,
        reason=interval_invalid,raw_previous_snapshot=previous,raw_current_snapshot=current,
        distance_reference='current receipt last true print, YES cents; missing when unavailable',
        execution_authority='exact API identity, canonical direction, is_block_trade=false; arithmetic is never execution attribution',
        zero_execution_refill='STORE_SILENT',snapshot_boundary_print_order='unknown => affected level residual missing',
        measurement='NET maker residual, not gross adds/cancels; shared displayed visibility only')


def receipt_features(*,epoch,previous_epoch,seconds_per_minute,formation,books,book_epochs,
                     first_q,bid,ask,previous_bid,previous_ask,prints,maker_previous=None,maker_current=None,
                     attributed_prints=(),last=None):
    """No lookup at a future epoch; both queue measurements use current FIRST Q."""
    if previous_epoch is not None and previous_epoch>=epoch:
        raise ValueError('PRIOR_RECEIPT_NOT_STRICTLY_EARLIER')
    now=asof_book(books,book_epochs,epoch)
    before=asof_book(books,book_epochs,previous_epoch)
    result={name:None for name,block,definition in NEW_FIELDS}
    for top,label in ((True,'top'),(False,'five')):
        a=imbalance(now[1],now[2],top_only=top) if usable_book(now) else None
        z=imbalance(before[1],before[2],top_only=top) if usable_book(before) else None
        result['book_imbalance_'+label]=a
        result['book_imbalance_'+label+'_change']=difference(a,z)
    minutes=(epoch-previous_epoch)/seconds_per_minute if previous_epoch is not None else None
    current_depth=visible_depth(now[1],first_q,'bid') if usable_book(now) and finite(first_q) else None
    prior_depth=visible_depth(before[1],first_q,'bid') if usable_book(before) and finite(first_q) else None
    result['displayed_depth_at_first_q']=float(current_depth) if current_depth is not None else None
    change=difference(prior_depth,current_depth)
    result['queue_decay_per_minute']=rate(float(change) if change is not None else None,minutes)
    current_spread,previous_spread=spread(bid,ask),spread(previous_bid,previous_ask)
    result['behavior_spread_cents']=current_spread
    result['spread_rate_per_minute']=rate(difference(current_spread,previous_spread),minutes)
    end=math.floor(epoch/seconds_per_minute)*seconds_per_minute
    start=max(formation,end-seconds_per_minute)
    if start<end:
        move,retraced=spike_reversion(prints,start,end,formation)
        result['completed_minute_largest_move']=move
        result['completed_minute_retraced_share']=retraced
    if maker_current is not None and maker_current[0]>epoch:
        raise ValueError('FUTURE_MAKER_STATE')
    maker,proof=maker_summary(maker_previous,maker_current,attributed_prints,
        reference_price=last,known_at_epoch=epoch)
    result.update(maker)
    return result,dict(previous_receipt_epoch=previous_epoch,first_q=first_q,
        current_book_invalid_reason=book_invalid_reason(now),
        previous_book_invalid_reason=book_invalid_reason(before),
        queue_basis='UNCHANGED_FIRST_Q_CURRENT_LEVEL_BOTH_CLOCKS; displayed depth, not queue priority',
        spike_window=[start,end],maker=proof)
