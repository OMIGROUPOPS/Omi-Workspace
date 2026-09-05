// Lossless dictionary encoding of repeated strings/objects, not a data transformation.
export function packFace(face) {
  const counts=new Map();
  function count(value){if(value===null||value===undefined)return;const s=JSON.stringify(value);if(s.length>120)counts.set(s,(counts.get(s)??0)+1);if(typeof value==='object')for(const v of Object.values(value))count(v);}
  count(face.os);
  const dictionary=[],indices=new Map();
  function encode(value){if(value===null||value===undefined)return value;const s=JSON.stringify(value);if(s.length>120&&counts.get(s)>1){if(!indices.has(s)){indices.set(s,dictionary.length);dictionary.push(value);}return {$ref:indices.get(s)};}if(Array.isArray(value))return value.map(encode);if(typeof value==='object')return Object.fromEntries(Object.entries(value).map(([k,v])=>[k,encode(v)]));return value;}
  return {...face,os:face.os.map(encode),dictionary};
}
export function unpackFace(face){
  const decode=value=>value&&typeof value==='object' ? ('$ref' in value?face.dictionary[value.$ref]:Array.isArray(value)?value.map(decode):Object.fromEntries(Object.entries(value).map(([k,v])=>[k,decode(v)]))) : value;
  return face.dictionary?{...face,os:face.os.map(decode)}:face;
}
