// Lossless artifact storage, not a change to any market or grading rule.
import {existsSync,readFileSync,writeFileSync,renameSync} from 'node:fs';
import {gzipSync,gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
export const GZIP_ARCHIVE_BYTES=64*1024*1024; // repository file-size headroom
export const jsonFileExists=file=>existsSync(file)||existsSync(file+'.gz');
export function readJsonBytes(file){return existsSync(file)?readFileSync(file):gunzipSync(readFileSync(file+'.gz'));}
export function gzipMirror(file,bytes=readJsonBytes(file)){
 const encoded=gzipSync(bytes,{level:9});
 const hash=b=>createHash('sha256').update(b).digest('hex');
 assert.equal(hash(gunzipSync(encoded)),hash(bytes),'Lossless JSON archive');
 writeFileSync(file+'.gz.tmp',encoded);renameSync(file+'.gz.tmp',file+'.gz');
 return {path:file+'.gz',json_bytes:bytes.length,gzip_bytes:encoded.length,sha256_uncompressed:hash(bytes),sha256_gzip:hash(encoded)};
}
export function refreshGzipMirror(file,bytes){
 if(bytes.length>=GZIP_ARCHIVE_BYTES||existsSync(file+'.gz'))return gzipMirror(file,bytes);
 return null;
}
