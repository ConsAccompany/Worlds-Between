const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..', 'outputs');
const port = 18724;
const inventoryFile = 'rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json';
const files = {
  '/': ['rpg-2-star-ocean-the-second_mvp-progress-and-assets_widget_v02_20261013-191348-5fb2c4e0.html','text/html; charset=utf-8'],
  '/state': ['rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json','application/json; charset=utf-8'],
  '/plan': ['rpg-2-star-ocean-the-second_mvp-implementation-plan_v01_20261013-183550-0f7c4d21.md','text/markdown; charset=utf-8'],
  '/inventory': [inventoryFile,'application/json; charset=utf-8'],
};
function respond(response, code, value, mime='text/plain; charset=utf-8') {
  response.writeHead(code, {'content-type':mime,'cache-control':'no-store','x-content-type-options':'nosniff'});
  response.end(value);
}
function saveCheck(request,response) {
  let body='';
  request.on('data',chunk=>{body+=chunk; if(body.length>1024)request.destroy();});
  request.on('end',()=>{
    try {
      const {id,checked}=JSON.parse(body);
      if(typeof id!=='string'||typeof checked!=='boolean')return respond(response,400,'Invalid check');
      const file=path.join(root,inventoryFile);
      const inventory=JSON.parse(fs.readFileSync(file,'utf8'));
      const item=inventory.categories.flatMap(c=>c.subcategories.flatMap(s=>s.items)).find(i=>i.id===id);
      if(!item||item.stage==='planned')return respond(response,400,'Asset not ready for acceptance');
      item.checked=checked;
      inventory.updatedAt=new Date().toISOString();
      fs.writeFileSync(file,JSON.stringify(inventory,null,2)+'\n','utf8');
      respond(response,200,JSON.stringify({id,checked}),'application/json; charset=utf-8');
    } catch(_) {respond(response,400,'Could not save check');}
  });
}
http.createServer((request,response)=>{
  const pathname=new URL(request.url,'http://127.0.0.1').pathname;
  if(pathname==='/asset-check'&&request.method==='POST')return saveCheck(request,response);
  if(request.method!=='GET')return respond(response,405,'Method not allowed');
  if(pathname==='/health')return respond(response,200,'ok');
  if(pathname.startsWith('/assets/')) {
    const filename=decodeURIComponent(pathname.slice('/assets/'.length));
    if(path.basename(filename)!==filename||!filename.endsWith('.png'))return respond(response,404,'Not found');
    fs.readFile(path.join(root,filename),(error,data)=>error?respond(response,404,'Not found'):respond(response,200,data,'image/png'));
    return;
  }
  if(!Object.hasOwn(files,pathname))return respond(response,404,'Not found');
  const [filename,mime]=files[pathname];
  fs.readFile(path.join(root,filename),(error,data)=>error?respond(response,503,'File unavailable'):respond(response,200,data,mime));
}).listen(port,'127.0.0.1');
