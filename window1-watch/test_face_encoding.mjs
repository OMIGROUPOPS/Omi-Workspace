import test from 'node:test';
import assert from 'node:assert/strict';
import {packFace,unpackFace} from './face_encoding.mjs';
test('dictionary encoding never serializes the unused whole timeline',()=>{
 const value={reason:'stored '.repeat(30),unknown:{all:'retained'}};
 const os=[{index:0,value},{index:1,value}];
 Object.defineProperty(os,'toJSON',{value:()=>{throw Error('Whole timeline serialized')}});
 const packed=packFace({os});
 assert.deepEqual(unpackFace(packed).os,[{index:0,value},{index:1,value}]);
 assert(packed.dictionary.length>0);
});
