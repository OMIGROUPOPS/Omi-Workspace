#!/usr/bin/env node
"use strict";
const assert=require('assert'),fs=require('fs'),path=require('path'),zlib=require('zlib');
const {MIN_CELL_N,conditionalFloorDistribution,narrowSiblingShapes}=require('../analysis/window1_second_leg_x_pricer_v17.js');
let n=0;const ok=(x,m)=>{assert.ok(x,m);n++;};
const training=Array.from({length:25},(_,i)=>({event_id:`E${i}`,first_fill_x_cents:20+i,sibling_eventual_ask_floor_cents:79-i}));
const library={cells:{'ATP|split':{training_rows:training}},shape_floor_support:{A:{rows:Array.from({length:25},(_,i)=>({event_id:`S${i}`,qualifying_ask_floor_cents:68+i%3}))},B:{rows:Array.from({length:25},(_,i)=>({event_id:`T${i}`,qualifying_ask_floor_cents:5+i%2}))},THIN:{rows:[{event_id:'T',qualifying_ask_floor_cents:50}]}}};
const c=conditionalFloorDistribution(library,{eventId:'E0',category:'ATP',startingPriceSplit:'split',firstFillX:30});
ok(c.usable,'supported LOO cell');ok(c.leave_one_event_out_n===24,'target event excluded');ok(c.residual_distribution.n>=MIN_CELL_N,'LOO residual support');ok(Number.isFinite(c.central_distribution_floor_low_cents),'distribution bound');
const d=narrowSiblingShapes(library,{eventId:'E0',category:'ATP',startingPriceSplit:'split',firstFillX:30,shapeIds:['A','B','THIN']});
ok(d.applied,'X distribution applied');ok(d.retained_shape_ids.includes('A'),'overlapping distribution retained');ok(d.eliminated_shapes.some(x=>x.shape_id==='B'),'disjoint distribution eliminated');ok(d.retained_shape_ids.includes('THIN')&&d.abstaining_shapes.some(x=>x.shape_id==='THIN'),'thin shape abstains rather than vetoes');ok(d.comparison_law.includes('NO_POINT_TARGET'),'no point target');
const thin=conditionalFloorDistribution({cells:{'ATP|split':{training_rows:training.slice(0,10)}}},{eventId:'Z',category:'ATP',startingPriceSplit:'split',firstFillX:30});ok(!thin.usable&&thin.reason.includes('THIN'),'thin cell unusable');
const replay=fs.readFileSync(path.join(__dirname,'../analysis/build_window1_quote_shape_elimination_replay_v11_frozen.js'),'utf8');ok(replay.includes('candidate.order.action_ts < ts'),'strictly later X arming');ok(!replay.includes('first_leg_realized_fall'),'dead inversion not consumed');ok(!replay.includes('pair_prints_'),'flow diagnostic not consumed');
console.log(`PASS ${n}`);
