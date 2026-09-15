// Migrate already-graded compact faces without replaying any game or changing a rule.
import fs from 'node:fs';
import path from 'node:path';
import {gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {packFace,unpackFace} from '../face_encoding.mjs';
import {writeBidDetails} from '../bid_card_details.mjs';
import {build as buildGrade} from '../build_grade.mjs';
import {buildPressure} from '../build_lab_pressure.mjs';
import {writeTimelineChunks,readTimelineChunks,refreshTimelinePreview,columnizeTimelinePreview} from '../timeline_chunks.mjs';
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
export async function compactCompletedFaces(events,data,runRoot,oldRoot) {
 const extracts=JSON.parse(fs.readFileSync(path.join(oldRoot,'SELECTED_PRINTS_RECEIPT.json'))).outputs;
 const results=[];
 for(const event of events){
  const file=path.join(data,event+'.face.json'),beforeBytes=fs.readFileSync(file),stored=JSON.parse(beforeBytes);
  const needsTimelinePreview=stored.timeline&&(!stored.timeline.receipt_columns.some(key=>key.startsWith('legs.'))||stored.timeline.receipt_storage!=='columns');
  if((stored.bid_card_details&&!needsTimelinePreview)||stored.availability?.status==='UNGRADABLE')continue;
  const face=unpackFace(stored),gradePath=path.join(data,event+'.grade.json'),before=JSON.parse(fs.readFileSync(gradePath));
  const preview=needsTimelinePreview?columnizeTimelinePreview(refreshTimelinePreview(stored,readTimelineChunks(stored,data))):writeTimelineChunks(writeBidDetails(face,data),data);
  const bytes=Buffer.from(JSON.stringify(preview.timeline?preview:packFace(preview))+'\n'),compressed=gzipSync(bytes,{level:9});
  assert(compressed.length<2*1024*1024,event+' main face exceeds cap');
  fs.writeFileSync(file+'.tmp',bytes);fs.renameSync(file+'.tmp',file);fs.writeFileSync(file+'.gz',compressed);
  buildPressure(data,event);
  const prints=extracts.find(e=>e.event===event)??JSON.parse(fs.readFileSync(path.join(runRoot,'ALT_PRINTS_RECEIPT.json')));
  // build() accepts parsed prints, not a path; the same approved extract is parsed here.
  const {readGradePrints}=await import('../grade_prints.mjs');
  const input=await readGradePrints(prints.path,[{event,legs:face.legs}]);
  assert.equal(input[event].provenance.sha256,prints.sha256);
  await buildGrade(event,input[event]);
  const after=JSON.parse(fs.readFileSync(gradePath));
  for(const section of ['SENTENCE','MACRO','MICRO','HANDS','OUTCOME','LETTER','display'])
    assert.deepEqual(after[section],before[section],`Packaging changed grade: ${event}/${section}`);
  const complete=path.join(runRoot,'runs',event,'FACE_COMPLETE.json');
  if(fs.existsSync(complete)){
   const old=JSON.parse(fs.readFileSync(complete));
   fs.writeFileSync(complete,JSON.stringify({...old,face_sha256:sha(bytes),grade_sha256:sha(fs.readFileSync(gradePath)),packaging_only:true},null,2)+'\n');
  }
  results.push({event,before_face_sha256:sha(beforeBytes),after_face_sha256:sha(bytes),gzip_bytes:compressed.length,grade_sections_identical:true});
  console.log('COMPACT_EXISTING_FACE',event,compressed.length);
 }
 if(results.length)fs.writeFileSync(path.join(runRoot,'BID_DETAIL_MIGRATION.json'),JSON.stringify(results,null,2)+'\n');
 return results;
}
