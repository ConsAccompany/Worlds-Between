const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const folder = path.join(root, 'game', 'assets', 'audio');
fs.mkdirSync(folder, {recursive:true});
const prefix = 'rpg-2-star-ocean-the-second_';
const stamp = '_m7_20261013-211230-';
const assets = [
  {area:'scifi-city',purpose:'ambient-loop',id:'c8e1159a',notes:[164.81,246.94,329.63],speed:0.22},
  {area:'scifi-outskirts',purpose:'ambient-loop',id:'57ad4b20',notes:[146.83,220.00,293.66],speed:0.31},
  {area:'scifi-ruins',purpose:'ambient-loop',id:'6be0d93f',notes:[130.81,196.00,261.63],speed:0.13},
  {area:'scifi-battle',purpose:'ambient-loop',id:'37fcaa02',notes:[110.00,164.81,220.00],speed:1.5},
  {area:'discovery',purpose:'interaction-cue',id:'ad781e52',notes:[523.25,659.25,783.99],speed:0.4},
];
const sampleRate = 22050;
function writeWav(file, data) {
  const pcm = Buffer.alloc(data.length * 2);
  for (let i=0; i<data.length; i++) pcm.writeInt16LE(Math.round(Math.max(-1,Math.min(1,data[i]))*32767),i*2);
  const header=Buffer.alloc(44);
  header.write('RIFF',0);header.writeUInt32LE(36+pcm.length,4);header.write('WAVEfmt ',8);
  header.writeUInt32LE(16,16);header.writeUInt16LE(1,20);header.writeUInt16LE(1,22);
  header.writeUInt32LE(sampleRate,24);header.writeUInt32LE(sampleRate*2,28);
  header.writeUInt16LE(2,32);header.writeUInt16LE(16,34);header.write('data',36);
  header.writeUInt32LE(pcm.length,40);
  fs.writeFileSync(file,Buffer.concat([header,pcm]));
}
for(const asset of assets){
  const cue=asset.area==='discovery';
  const seconds=cue?0.5:8;
  const samples=[];
  for(let i=0;i<Math.floor(seconds*sampleRate);i++){
    const t=i/sampleRate;
    const swell=cue?Math.sin(Math.PI*t/seconds)**1.4:0.55+0.35*Math.cos(2*Math.PI*t/seconds);
    const pulse=cue?1:0.7+0.3*Math.cos(2*Math.PI*asset.speed*t);
    let value=0;
    for(let n=0;n<asset.notes.length;n++) value+=Math.sin(2*Math.PI*asset.notes[n]*t+(n*0.25))*[0.46,0.28,0.16][n];
    value+=0.09*Math.sin(2*Math.PI*asset.notes[0]*0.5*t);
    const edge=cue?1:Math.min(1,t/0.08,(seconds-t)/0.08);
    samples.push(value*swell*pulse*edge*(cue?0.30:0.17));
  }
  const filename=`${prefix}${asset.area}_${asset.purpose}${stamp}${asset.id}.wav`;
  writeWav(path.join(folder,filename),samples);
  console.log(filename);
}
