#!/usr/bin/env node
// Records start/end meter values in the existing Bible. Never changes ledger scores.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const output='outputs/';
const bibleFile=path.join(root,output+'rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json');
const ledgerFile=path.join(root,output+'rpg-2-star-ocean-the-second_production-completion_task-ledger_v01_20261018-140533-3de52073.json');
const [command,...args]=process.argv.slice(2),flags={};
for(let i=0;i<args.length;i+=2){if(!args[i]?.startsWith('--')||!args[i+1])throw Error('Expected --name value');flags[args[i].slice(2)]=args[i+1];}
if(!['begin','finish'].includes(command)||!flags.id)throw Error('Use begin|finish --id task-id [--title-zh text --title-en text] [--evidence repo-relative-file]');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
const bible=read(bibleFile),ledger=read(ledgerFile),computed=ledger.computed;
const current={production:computed?.production?.percent,inspection:computed?.inspection?.percent,approval:computed?.approval?.percent};
if(Object.values(current).some(v=>typeof v!=='number'||!Number.isFinite(v)||v<0||v>100))throw Error('Canonical meters unavailable');
const now=new Date().toISOString(),source=execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim();
if(command==='begin'){
 if(bible.latestTaskProgress?.status==='in_progress')throw Error('Finish the active task record first');
 if(!flags['title-zh']||!flags['title-en'])throw Error('Both task titles are required');
 if(bible.latestTaskProgress)(bible.taskProgressHistory??=[]).push(bible.latestTaskProgress);
 bible.latestTaskProgress={id:flags.id,status:'in_progress',title:{zh:flags['title-zh'],en:flags['title-en']},startedAt:now,sourceBefore:source,meters:Object.fromEntries(Object.entries(current).map(([k,v])=>[k,{before:v,after:null,changePercentagePoints:null}]))};
}else{
 const record=bible.latestTaskProgress;
 if(record?.status!=='in_progress'||record.id!==flags.id)throw Error('No matching active task record');
 const evidence=flags.evidence||'',absolute=path.resolve(root,evidence),relative=path.relative(root,absolute);
 if(!evidence||relative.startsWith('..')||path.isAbsolute(relative)||!fs.statSync(absolute).isFile())throw Error('A verified project evidence file is required');
 for(const [key,v] of Object.entries(current)){
  const before=record.meters[key]?.before;
  if(typeof before!=='number'||!Number.isFinite(before))throw Error('Invalid start meter');
  record.meters[key]={before,after:v,changePercentagePoints:Math.round((v-before)*10)/10};
 }
 Object.assign(record,{status:'completed',completedAt:now,sourceAfter:source,evidence:[relative.split(path.sep).join('/')]});
}
bible.progressReporting={requiredFormat:'before → after (change in percentage points)',sameMetricAndFrozenBaseline:true,productionInspectionApprovalSeparate:true};
bible.updatedAt=now;
fs.writeFileSync(bibleFile,JSON.stringify(bible,null,2)+'\n','utf8');
const r=bible.latestTaskProgress.meters.production;
console.log(`${flags.id}: ${r.before.toFixed(1)}% → ${r.after===null?'pending':r.after.toFixed(1)+'% ('+(r.changePercentagePoints>=0?'+':'')+r.changePercentagePoints.toFixed(1)+' pp)'}`);
