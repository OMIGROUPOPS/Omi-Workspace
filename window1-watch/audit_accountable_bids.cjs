"use strict";
const fs=require('fs'),cp=require('child_process'),path=require('path'),assert=require('node:assert/strict');
const repo=path.resolve(__dirname,'..'),acorn=require('../node_modules/acorn');
const baseline=process.argv[2],out=process.argv[3];assert.ok(baseline&&out);
const tokens=s=>[...acorn.tokenizer(s,{ecmaVersion:'latest'})].map(t=>[t.type.label,t.value]);
const functions=s=>Object.fromEntries(acorn.parse(s,{ecmaVersion:'latest'}).body.filter(n=>n.type==='FunctionDeclaration').map(n=>[n.id.name,JSON.stringify(tokens(s.slice(n.start,n.end)))]));
const rows=[];
for(const name of ['window1_v54_dual_belief_os.js','window1_v54_functionable_os.js','build_window1_v54_dual_belief.js']){
 const file='arb-executor/analysis/'+name,before=cp.execFileSync('git',['show',baseline+':'+file],{cwd:repo,maxBuffer:2000000}).toString(),after=fs.readFileSync(path.join(repo,file),'utf8');
 const prior=functions(before),current=functions(after),added=Object.keys(current).filter(k=>!prior[k]);
 const changed=Object.keys(prior).filter(k=>current[k]!==prior[k]),newFunctions=acorn.parse(after,{ecmaVersion:'latest'}).body.filter(n=>n.type==='FunctionDeclaration'&&added.includes(n.id.name)).map(n=>after.slice(n.start,n.end)).join('\n');
 const numeric=tokens(newFunctions).filter(t=>t[0]==='num');
 const identities=[...newFunctions.matchAll(/KX[A-Z]+MATCH-\w+|\b(?:ALT|GAS|PAL|GIU|LAJ|SVA)\b/g)].map(m=>m[0]);
 assert.equal(numeric.length,0);assert.equal(identities.length,0);
 if(name==='window1_v54_dual_belief_os.js')assert.equal(changed.length,0,'pre-existing OS functions changed');
 if(name==='window1_v54_functionable_os.js')assert.equal(before,after,'pool/functionable changed');
 if(name.startsWith('build_'))assert.deepEqual(changed.sort(),['digestReplay','main','replayEvent']);
 rows.push({file,changed,added,new_function_numeric_literals:numeric,new_function_game_or_leg_ids:identities,
  unchanged_functions:Object.keys(prior).filter(k=>current[k]===prior[k])});
}
const output={baseline,rows,scope:'Only receipt observation and serialization in OS/builder; existing OS functions and entire functionable file identical. Face changes are projection/markers, not conduct.',
 boolean_explanations:{conduct_changed:'false: observer only mutates its own ledger, verified by original stage/action/fill comparison; not a trading success claim',
  terminal_status:'Computed from causal positive print/deadline comparisons; never a literal success verdict'}};
output.literal_boolean_audit=require('../arb-executor/analysis/build_window1_v54_dual_belief.js').literalClaimAudit(repo);
assert.equal(output.literal_boolean_audit.unexplained_count,0);
fs.writeFileSync(out,JSON.stringify(output,null,2)+'\n');console.log(JSON.stringify(output,null,2));
