const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const output = path.resolve(__dirname, '..', 'outputs');
const port = 18724;
const inventoryName = 'rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json';
const routes = {
  '/': ['rpg-2-star-ocean-the-second_game-bible_widget_v03_20261013-195526-8e5a1c43.html','text/html; charset=utf-8'],
  '/bible.css': ['rpg-2-star-ocean-the-second_game-bible_styles_v01_20261013-195526-6c13fa09.css','text/css; charset=utf-8'],
  '/bible.js': ['rpg-2-star-ocean-the-second_game-bible_app_v01_20261013-195526-90e7bc24.js','text/javascript; charset=utf-8'],
  '/bible': ['rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json','application/json; charset=utf-8'],
  '/inventory': [inventoryName,'application/json; charset=utf-8'],
  '/state': ['rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json','application/json; charset=utf-8'],
  '/source/brief': ['rpg-2-star-ocean-the-second_game-design-brief_v01_20261012-233611-7c2e1f4a.md','text/markdown; charset=utf-8'],
  '/source/core': ['rpg-2-star-ocean-the-second_core-cast_character-bible_v01_20261012-234158-cc7e91a4.md','text/markdown; charset=utf-8'],
  '/source/extra': ['rpg-2-star-ocean-the-second_remaining-companions_character-bible_v01_20261013-181920-6d2a4f8c.md','text/markdown; charset=utf-8'],
  '/source/mvp': ['rpg-2-star-ocean-the-second_mvp-implementation-plan_v01_20261013-183550-0f7c4d21.md','text/markdown; charset=utf-8'],
};
function respond(response, code, value, mime='text/plain; charset=utf-8') {
  response.writeHead(code,{'content-type':mime,'cache-control':'no-store','x-content-type-options':'nosniff'});
  response.end(value);
}
function saveCheck(request,response) {
  let body='';
  request.on('data',chunk=>{body+=chunk;if(body.length>1024)request.destroy();});
  request.on('end',()=>{
    try {
      const {id,checked}=JSON.parse(body);
      if(typeof id!=='string'||typeof checked!=='boolean')return respond(response,400,'Invalid check');
      const file=path.join(output,inventoryName);
      const inventory=JSON.parse(fs.readFileSync(file,'utf8'));
      const item=inventory.categories.flatMap(c=>c.subcategories.flatMap(s=>s.items)).find(i=>i.id===id);
      if(!item||item.stage==='planned')return respond(response,400,'Asset not ready for acceptance');
      item.checked=checked;inventory.updatedAt=new Date().toISOString();
      fs.writeFileSync(file,JSON.stringify(inventory,null,2)+'\n','utf8');
      respond(response,200,JSON.stringify({id,checked}),'application/json; charset=utf-8');
    } catch(_) {respond(response,400,'Could not save check');}
  });
}
http.createServer((request,response)=>{
  let pathname;
  try {pathname=new URL(request.url,'http://127.0.0.1').pathname;}
  catch(_) {return respond(response,400,'Invalid URL');}
  if(pathname==='/asset-check'&&request.method==='POST')return saveCheck(request,response);
  if(request.method!=='GET')return respond(response,405,'Method not allowed');
  if(pathname==='/health')return respond(response,200,'ok');
  if(pathname.startsWith('/assets/')){
    let filename;
    try {filename=decodeURIComponent(pathname.slice('/assets/'.length));}
    catch(_) {return respond(response,400,'Invalid image path');}
    if(path.basename(filename)!==filename||!filename.endsWith('.png'))return respond(response,404,'Not found');
    fs.readFile(path.join(output,filename),(error,data)=>error?respond(response,404,'Not found'):respond(response,200,data,'image/png'));
    return;
  }
  if(!Object.hasOwn(routes,pathname))return respond(response,404,'Not found');
  const [filename,mime]=routes[pathname];
  fs.readFile(path.join(output,filename),(error,data)=>error?respond(response,503,'File unavailable'):respond(response,200,data,mime));
}).listen(port,'127.0.0.1');
