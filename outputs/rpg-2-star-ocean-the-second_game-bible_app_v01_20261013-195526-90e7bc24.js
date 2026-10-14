(() => {
  const content = document.getElementById('content');
  const search = document.getElementById('search');
  const nav = [...document.querySelectorAll('.main-nav button')];
  const state = {
    bible:null, inventory:null, progress:null, playtests:[], playtestStatus:{phase:'loading'}, view:'home', query:'',
    chapter:'chapter-3', character:'hero', board:'全部板块',
    group:'全部来源', assetScope:'all', openGroups:new Set(['characters']),
  };
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const inline = value => esc(value)
    .replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>')
    .replace(/`([^`]+)`/g,'<code>$1</code>');
  const source = id => state.bible.sources.find(item => item.id === id);
  const sourceLine = id => {
    const item=source(id);
    return item ? `<div class="source-line">资料来源：<a href="${item.url}" target="_blank" rel="noopener">${esc(item.filename)}</a></div>` : '';
  };
  const badge = (label,kind='') => `<span class="badge ${kind}">${esc(label)}</span>`;
  function markdown(input) {
    const lines=String(input||'').split('\n');
    const out=[];
    let i=0;
    while(i<lines.length) {
      const line=lines[i].trim();
      if(!line){i++;continue;}
      if(/^#{3,5} /.test(line)){out.push('<h3>'+inline(line.replace(/^#{3,5} /,''))+'</h3>');i++;continue;}
      if(line.startsWith('> ')){out.push('<blockquote>'+inline(line.slice(2))+'</blockquote>');i++;continue;}
      if(line.startsWith('|') && i+1<lines.length && /^\|?\s*:?-{3,}/.test(lines[i+1].trim())) {
        const rows=[]; while(i<lines.length && lines[i].trim().startsWith('|')){rows.push(lines[i].trim().replace(/^\||\|$/g,'').split('|').map(cell=>cell.trim()));i++;}
        const header=rows.shift(); rows.shift();
        out.push('<table><thead><tr>'+header.map(cell=>'<th>'+inline(cell)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map(cell=>'<td>'+inline(cell)+'</td>').join('')+'</tr>').join('')+'</tbody></table>');
        continue;
      }
      const list=line.match(/^(?:- |\d+\. )/);
      if(list) {
        const ordered=/^\d/.test(line), tag=ordered?'ol':'ul', parts=[];
        while(i<lines.length && (ordered?/^\d+\. /:/^- /).test(lines[i].trim())) {
          parts.push('<li>'+inline(lines[i].trim().replace(ordered?/^\d+\. /:/^- /,''))+'</li>');i++;
        }
        out.push('<'+tag+'>'+parts.join('')+'</'+tag+'>');continue;
      }
      const parts=[line];i++;
      while(i<lines.length && lines[i].trim() && !/^(?:#{3,5} |>|- |\d+\. |\|)/.test(lines[i].trim())){parts.push(lines[i].trim());i++;}
      out.push('<p>'+inline(parts.join(' '))+'</p>');
    }
    return out.join('');
  }
  const head = (title,subtitle,right='') => `<div class="page-head"><div><h2>${esc(title)}</h2><p>${esc(subtitle)}</p></div>${right}</div>`;
  function navigate(view,options={}) {
    state.view=view;state.query='';search.value='';
    Object.assign(state,options);
    nav.forEach(button=>button.setAttribute('aria-current',button.dataset.view===view?'page':'false'));
    render();
  }
  function renderHome() {
    const b=state.bible, done=state.progress.steps.filter(step=>step.status==='done').length;
    const facts=b.facts.map(f=>`<div class="fact"><strong>${esc(f.label)}</strong><span>${esc(f.value)}</span></div>`).join('');
    content.innerHTML=`
      ${head('游戏圣经','一处查阅已定规则、人物提案和制作状态',badge(b.edition,'accent'))}
      <section class="card hero-card"><div class="kicker">核心体验</div><p>${esc(b.pitch)}</p><div class="pillars">${b.pillars.map(p=>'<span>'+esc(p)+'</span>').join('')}</div></section>
      <div class="fact-grid">${facts}</div>
      <section class="card"><h3>设定状态</h3><p>${esc(b.note)}</p><p class="muted small">规则章标为「需求基线」；角色档案标为「人物提案」。资产勾选只代表该素材已验收。</p></section>
      <div class="section-label">进入游戏圣经</div>
      <div class="links">
        <button class="link-card" data-go="world"><strong>世界与历史</strong><small>地下社区、五个板块、文明协议与幕后威胁</small></button>
        <button class="link-card" data-go="rules"><strong>系统规则</strong><small>探索、战斗、职业、关系、经营与二周目</small></button>
        <button class="link-card" data-go="characters"><strong>人物档案</strong><small>主角 + 50 位伙伴，可按板块和招募来源筛选</small></button>
        <button class="link-card" data-go="production"><strong>MVP 与待定事项</strong><small>${done} / ${state.progress.steps.length} 阶段完成；查看下一步和待细化设计</small></button>
        <button class="link-card" data-go="assets"><strong>资产清单</strong><small>图像、场景、战斗、界面、声音与双语内容</small></button>
      </div>
      <div class="section-label">资料来源</div>
      <div class="card">${b.sources.map(s=>`<div><a href="${s.url}" target="_blank" rel="noopener">${esc(s.filename)}</a></div>`).join('')}</div>`;
    content.querySelectorAll('[data-go]').forEach(el=>el.addEventListener('click',()=>navigate(el.dataset.go)));
  }
  function renderWorld() {
    const chapter=state.bible.chapters.find(c=>c.number===2);
    content.innerHTML=`${head('世界与历史',chapter.summary,badge(chapter.status,'accent'))}
      <article class="document">${markdown(chapter.body)}${sourceLine(chapter.source)}</article>`;
  }
  function renderRules() {
    const chapters=state.bible.chapters.filter(c=>[1,3,4,5,6,7].includes(c.number));
    const selected=chapters.find(c=>c.id===state.chapter)||chapters[0];
    content.innerHTML=`${head('系统规则','点击章节阅读完整需求基线',badge('6 个章节','accent'))}
      <div class="subnav" role="group" aria-label="规则章节">${chapters.map(c=>`<button type="button" data-chapter="${c.id}" aria-pressed="${c.id===selected.id}">${esc(c.title)}</button>`).join('')}</div>
      <div class="card"><div class="kicker">第 ${selected.number} 章 · ${esc(selected.status)}</div><h3>${esc(selected.title)}</h3><p class="muted">${esc(selected.summary)}</p></div>
      <article class="document">${markdown(selected.body)}${sourceLine(selected.source)}</article>`;
    content.querySelectorAll('[data-chapter]').forEach(el=>el.addEventListener('click',()=>{state.chapter=el.dataset.chapter;render();}));
  }
  function renderCharacters() {
    const b=state.bible;
    const boards=['全部板块','地下社区','科技','自然','奇幻','魔法','星外'];
    const groups=['全部来源','主角','主线伙伴','支线伙伴','情境招募伙伴'];
    const visible=b.characters.filter(c=>(state.board==='全部板块'||c.board===state.board)&&(state.group==='全部来源'||c.group===state.group));
    const selected=visible.find(c=>c.id===state.character)||visible[0];
    if(selected)state.character=selected.id;
    const images=selected?.portraits||[selected?.portrait].filter(Boolean);
    const imageHtml=images.length===2
      ? '<div class="portrait-pair">'+images.map((p,i)=>`<a href="${p}" target="_blank" rel="noopener"><img class="portrait" src="${p}" alt="主角${i?'女':'男'}设定图" loading="lazy"></a>`).join('')+'</div>'
      : images.length ? `<a href="${images[0]}" target="_blank" rel="noopener"><img class="portrait" src="${images[0]}" alt="${esc(selected.cn)}的21:9人物设定图" loading="lazy"></a>`:'';
    content.innerHTML=`${head('人物档案','主角和 50 位可招募伙伴；姓名与外观仍可修订',badge('51 份档案','warn'))}
      <div class="filters">
        <label><span class="visually-hidden">按板块筛选</span><select id="board-filter">${boards.map(x=>`<option ${x===state.board?'selected':''}>${x}</option>`).join('')}</select></label>
        <label><span class="visually-hidden">按来源筛选</span><select id="group-filter">${groups.map(x=>`<option ${x===state.group?'selected':''}>${x}</option>`).join('')}</select></label>
      </div>
      <div class="character-layout">
        <div class="character-list" aria-label="角色列表">${visible.map(c=>`<button type="button" class="list-button" data-character="${c.id}" aria-pressed="${c.id===selected?.id}"><strong>${c.number?String(c.number).padStart(2,'0')+' · ':''}${esc(c.cn)}</strong><small>${esc(c.board)} · ${esc(c.group)}</small></button>`).join('')}</div>
        <div class="character-detail">${selected?`
          <div class="card"><div class="kicker">${esc(selected.group)} · ${esc(selected.board)}</div><h3 class="character-name">${esc(selected.cn)} <span class="muted small">/ ${esc(selected.en)}</span></h3>
          <div class="filters">${badge(selected.status,'warn')}${selected.portraitStage?badge(selected.portraitAccepted?'画像已验收':'画像'+(selected.portraitStage==='planned'?'待制作':'概念稿')):''}</div>
          ${imageHtml}<p class="small muted">点击画像查看独立原图。设定图不等同于游戏精灵。</p></div>
          <article class="document">${markdown(selected.body)}${sourceLine(selected.source)}</article>`:'<div class="empty">当前筛选没有角色。</div>'}</div>
      </div>`;
    document.getElementById('board-filter').addEventListener('change',e=>{state.board=e.target.value;render();});
    document.getElementById('group-filter').addEventListener('change',e=>{state.group=e.target.value;render();});
    content.querySelectorAll('[data-character]').forEach(el=>el.addEventListener('click',()=>{state.character=el.dataset.character;render();}));
  }
  function renderProduction() {
    const p=state.progress, done=p.steps.filter(s=>s.status==='done').length;
    const current=p.steps.find(s=>s.id===p.currentStep)||p.steps.find(s=>s.status!=='done');
    const status={done:'已完成',ready:'待开始',todo:'未开始',in_progress:'进行中',review:'待验收',blocked:'受阻'};
    const copy={
      M1:['项目基础','可启动游戏、切换中英文，并进入和离开基础场景。','Windows 上正常启动；语言可切换；像素显示清晰。'],
      M2:['世界地图与探索','开放三个目的地，加入俯视移动、NPC 与可绕开的可见敌人。','不用开发工具即可往返三个地点，并绕开至少一场普通战斗。'],
      M3:['战斗核心','建立横向平地战斗、基础动作、能量、敌人和战后恢复。','能打赢或战败；无跳跃；验证 20%／10% 恢复和重复接敌。'],
      M4:['伙伴与 AI','实现五个队伍位置、三种招募路线、等级同步、切换角色与指令。','三位伙伴都能招募；四人队伍可获胜；AI 与临时指令生效。'],
      M5:['等级与职业','加入经验、JP、四项天分、四条职业系列和 10 级必选职业。','可留任、晋升、切换并保留原系列进度；候补获得 25% 收益。'],
      M6:['存档与恢复','加入战后自动存档、手动存档及队伍和职业状态加载。','重新启动后能读取关键状态；战败回菜单后可加载。'],
      M7:['可玩内容','科技板块三地探索、六处勘察空间、九组证据关联、六处现场痕迹、六段伙伴交流、三位伙伴招募与回城汇报已连通。','不用开发工具通关；两种探索和招募顺序可行；中英文显示完整，并实测 25–35 分钟内容长度。'],
      M8:['验收与调整','完整试玩、记录转场时间和易用性问题，并修复阻碍。','两次新存档完整试玩无阻碍；存档和回访招募通过核验。'],
    };
    const place={'scifi.city':'城市','scifi.outskirts':'城外','scifi.ruins':'遗址'};
    const shortTime=seconds=>{const whole=Math.round(seconds);return `${Math.floor(whole/60)}:${String(whole%60).padStart(2,'0')}`;};
    const playtestRows=state.playtests.map(run=>{
      const seconds=Math.round(run.durationSeconds);
      const elapsed=`${Math.floor(seconds/60)} 分 ${String(seconds%60).padStart(2,'0')} 秒`;
      const route=run.visits.map(id=>place[id]).filter(Boolean).join(' → ')||'未记录';
      const placeTimes=Object.entries(run.timeByDestination||{}).filter(([id])=>place[id]).map(([id,seconds])=>`${place[id]} ${shortTime(seconds)}`).join(' · ');
      const surveyTimes=(run.surveyTimeline||[]).map(item=>`${place[item.destination]} ${shortTime(item.atSeconds)}`).join(' → ');
      return `<div class="playtest-run"><strong>${esc(elapsed)}</strong><span class="muted small">${esc(run.recordedAt)} · ${run.language==='en'?'英文':'中文'}</span><div class="small">路线：${esc(route)}</div><div class="small muted">已招募 ${run.recruited.length}/3 · 完成调查 ${run.surveysCompleted}/3 · 现场痕迹 ${run.fieldTraces||0}/6 · 同行交流 ${run.conversationsHeard}/6 · 战斗 ${run.battles} 场 · 错误证据关联 ${run.wrongEvidencePairs} 次 · 错误研判 ${run.wrongJudgments} 次</div>${placeTimes?`<div class="small">各地累计停留：${esc(placeTimes)}</div>`:''}${surveyTimes?`<div class="small muted">调查完成时点：${esc(surveyTimes)}</div>`:''}<div class="small muted receipt-name">原始记录：outputs/${esc(run.id)}</div></div>`;
    }).join('');
    const routeTrials=new Set(state.playtests.filter(run=>run.visits.length===3&&run.surveysCompleted===3&&run.recruited.length===3&&run.durationSeconds>=1500&&run.durationSeconds<=2100).map(run=>run.visits.join('>')));
    const launchPhase=state.playtestStatus.phase;
    const launchText={loading:'正在检查本地试玩入口…',idle:'可以从此处打开游戏。请从新档开始，完成城市汇报后关闭游戏，记录会自动显示在下方。',running:'游戏正在运行。完成城市汇报后关闭游戏，记录会自动回传。',completed:'上一轮试玩记录已回传，可以开始另一条路线。',no_report:'上一轮在完成城市汇报前结束，没有生成完成记录。可以重新开始。',error:'上一轮启动或运行失败，请检查本地游戏文件。',unavailable:'当前面板没有连接试玩入口。请打开最新版本地面板。'};
    const launchDisabled=!['idle','completed','no_report','error'].includes(launchPhase);
    const launchHint=launchPhase==='unavailable' ? '当前面板没有连接试玩入口。<a href="http://127.0.0.1:18727/">打开当前面板</a>。' : esc(launchText[launchPhase]||launchText.loading);
    const pct=Math.round(100*done/p.steps.length);
    content.innerHTML=`${head('制作路线','MVP 阶段状态与尚待细化的完整游戏设计',badge(done+' / '+p.steps.length+' 阶段','accent'))}
      <div class="card"><div class="step-top"><strong>MVP 完成情况</strong><span>${pct}%</span></div><div class="meter" role="progressbar" aria-valuemin="0" aria-valuemax="${p.steps.length}" aria-valuenow="${done}"><span style="width:${pct}%"></span></div><p class="muted small">当前：${current?esc(current.id+' · '+copy[current.id][0]):'全部阶段已完成'}</p></div>
      <div class="section-label">分步实施</div>
      <div class="stack">${p.steps.map(step=>`<details class="group"><summary>${esc(step.id+' · '+copy[step.id][0])} <span class="group-count">${esc(status[step.status]||step.status)}</span></summary><div class="card"><p>${esc(copy[step.id][1])}</p><strong>验收标准</strong><p>${esc(copy[step.id][2])}</p>${step.details?.length?'<strong>当前内容</strong><ul>'+step.details.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>':''}${step.remaining?.length?'<strong>尚需完成</strong><ul>'+step.remaining.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>':''}${step.evidence?.length?'<strong>已有依据</strong><ul>'+step.evidence.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>':''}</div></details>`).join('')}</div>
      <div class="section-label">M7 试玩记录</div>
      <section class="card"><div class="step-top"><h3>本地汇报记录</h3><button type="button" class="chip" id="refresh-playtests">刷新记录</button></div><div class="playtest-launch"><button type="button" class="chip" id="start-playtest" ${launchDisabled?'disabled':''}>${launchPhase==='running'?'试玩进行中':'开始新档试玩'}</button><span class="muted small" role="status">${launchHint}</span></div><p class="muted small">请分别用两个新档试玩。满足不同首访顺序、25–35 分钟、三处勘察和三位伙伴的路线：${Math.min(2,routeTrials.size)}/2。时间由游戏计时，是否有卡点和内容节奏还需玩家判断。</p><details class="group"><summary>两轮试玩指引</summary><div class="card small"><p><strong>第一轮：</strong>城市 → 城外 → 遗址。<strong>第二轮：</strong>遗址 → 城外 → 城市。每轮都从主菜单开始新游戏，三位伙伴可暂缓邀请，但在回城汇报前请招募齐。</p><ol><li>各地查看六条线索、完成三组证据关联与最终研判。</li><li>检查城外中继和遗址记录；绕过或击败一台机械。两处现场痕迹和伙伴协助是可选内容。</li><li>回城市提交汇报。出现完成画面后关闭游戏，等待记录回传。</li></ol><p>试玩时留意迷路、操作不明、文字溢出、战斗难度和想继续探索的动力；这些体验无法由自动记录判断。</p></div></details><div class="stack">${playtestRows||'<div class="empty">尚无正式试玩记录。M7 仍需两次不同顺序的实际计时试玩。</div>'}</div></section>
      <div class="section-label">仍待确定</div>
      <div class="stack">${state.bible.openQuestions.map(q=>`<div class="card"><h3>${esc(q.title)}</h3><p>${esc(q.detail)}</p></div>`).join('')}</div>
      <div class="section-label">设计稿中的实施顺序与待细化清单</div>
      <div class="stack">${state.bible.chapters.filter(c=>[8,9].includes(c.number)).map(c=>`<details class="group" data-production-chapter="${c.id}"><summary>${esc(c.title)}</summary><div class="document">${markdown(c.body)}${sourceLine(c.source)}</div></details>`).join('')}</div>
      <div class="section-label">计划与完整实施顺序</div>
      <div class="card"><a href="/source/mvp" target="_blank" rel="noopener">打开 MVP 实施计划</a> · <a href="/source/brief" target="_blank" rel="noopener">打开完整设计稿</a></div>`;
    content.querySelector('#refresh-playtests').addEventListener('click',()=>refreshPlaytests().catch(()=>{document.getElementById('footer-status').textContent='试玩记录暂时无法读取';}));
    content.querySelector('#start-playtest').addEventListener('click',startPlaytest);
  }
  function renderAssets() {
    const inventory=state.inventory;
    const visible=items=>items.filter(i=>state.assetScope==='all'||i.scope==='MVP');
    const all=inventory.categories.flatMap(c=>c.subcategories.flatMap(s=>visible(s.items)));
    const accepted=all.filter(i=>i.checked).length;
    const portraits=all.filter(i=>i.id.startsWith('portrait.')&&i.stage!=='planned').length;
    content.innerHTML=`${head('资产清单','概念稿、制作中与游戏可用素材分别验收',badge(accepted+' / '+all.length,'accent'))}
      <div class="asset-summary"><strong>${accepted} 项已验收</strong><div class="small muted">${portraits} 张人物设定图已有初稿 · ${all.length} 项清单条目</div></div>
      <div class="filters"><button type="button" class="chip" data-scope="all" aria-pressed="${state.assetScope==='all'}">全部</button><button type="button" class="chip" data-scope="mvp" aria-pressed="${state.assetScope==='mvp'}">仅 MVP</button></div>
      <div id="asset-tree"></div><p class="muted small">勾选表示该项已验收。未制作项目无法勾选；人物概念稿与游戏精灵分别记录。</p>`;
    content.querySelectorAll('[data-scope]').forEach(el=>el.addEventListener('click',()=>{state.assetScope=el.dataset.scope;render();}));
    const tree=document.getElementById('asset-tree');
    inventory.categories.forEach(cat=>{
      const catItems=cat.subcategories.flatMap(s=>visible(s.items));if(!catItems.length)return;
      const outer=document.createElement('details');outer.className='group';outer.open=state.openGroups.has(cat.id);
      outer.addEventListener('toggle',()=>outer.open?state.openGroups.add(cat.id):state.openGroups.delete(cat.id));
      const summary=document.createElement('summary');summary.textContent=cat.name;
      const tally=document.createElement('span');tally.className='group-count';tally.textContent=catItems.filter(i=>i.checked).length+' / '+catItems.length;summary.append(tally);outer.append(summary);
      cat.subcategories.forEach(sub=>{
        const items=visible(sub.items);if(!items.length)return;
        const key=cat.id+'.'+sub.id;
        const inner=document.createElement('details');inner.className='subgroup';inner.open=state.openGroups.has(key);
        inner.addEventListener('toggle',()=>inner.open?state.openGroups.add(key):state.openGroups.delete(key));
        const heading=document.createElement('summary');heading.textContent=sub.name;
        const tally=document.createElement('span');tally.className='group-count';tally.textContent=items.filter(i=>i.checked).length+' / '+items.length;heading.append(tally);inner.append(heading);
        const list=document.createElement('div');list.className='asset-list';
        items.forEach(item=>{
          const row=document.createElement('label');row.className='asset-row';row.dataset.assetId=item.id;
          const box=document.createElement('input');box.type='checkbox';box.checked=Boolean(item.checked);box.disabled=item.stage==='planned';box.setAttribute('aria-label',item.name+' 已验收');
          box.addEventListener('change',async()=>{
            box.disabled=true;
            try {
              const response=await fetch('/asset-check',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({id:item.id,checked:box.checked})});
              if(!response.ok)throw new Error('Save failed');
              await refreshInventory();
            } catch(_) {box.checked=!box.checked;box.disabled=false;document.getElementById('footer-status').textContent='资产状态未能保存';}
          });
          const body=document.createElement('div');const name=document.createElement('strong');name.textContent=item.name;body.append(name);
          const meta=document.createElement('div');meta.className='asset-meta';
          const stages={planned:'待制作',concept:'概念稿',approved:'已修订',production:'制作中',ready:'可验收'};
          meta.textContent=(item.scope==='MVP'?'MVP':'完整游戏')+' · '+(stages[item.stage]||item.stage)+(item.target>1?' · 目标 '+item.target+' 份':'')+(item.board?' · '+item.board:'');
          if(item.file){const link=document.createElement('a');link.href=item.file;link.target='_blank';link.rel='noopener';link.textContent='查看';meta.append(link);}
          body.append(meta);if(item.note){const note=document.createElement('div');note.className='asset-meta';note.textContent=item.note;body.append(note);}
          row.append(box,body);list.append(row);
        });
        inner.append(list);outer.append(inner);
      });
      tree.append(outer);
    });
  }
  function renderSearch() {
    const q=state.query.toLocaleLowerCase();
    const matches=[];
    for(const c of state.bible.chapters)if((c.title+' '+c.body).toLocaleLowerCase().includes(q))matches.push({type:'章节',title:c.title,subtitle:c.summary,go:()=>{
      navigate(c.number===2?'world':c.number>=8?'production':'rules',{chapter:c.id});
      if(c.number>=8){const detail=content.querySelector('[data-production-chapter="'+c.id+'"]');if(detail){detail.open=true;detail.scrollIntoView({block:'start'});}}
    }});
    for(const c of state.bible.characters)if((c.cn+' '+c.en+' '+c.board+' '+c.group+' '+c.body).toLocaleLowerCase().includes(q))matches.push({type:'角色',title:c.cn+' / '+c.en,subtitle:c.board+' · '+c.group,go:()=>navigate('characters',{board:'全部板块',group:'全部来源',character:c.id})});
    for(const category of state.inventory.categories)for(const sub of category.subcategories)for(const item of sub.items)if((item.name+' '+category.name+' '+sub.name).toLocaleLowerCase().includes(q))matches.push({type:'资产',title:item.name,subtitle:category.name+' · '+sub.name,go:()=>{
      state.assetScope='all';state.openGroups.add(category.id);state.openGroups.add(category.id+'.'+sub.id);navigate('assets');
      const row=[...content.querySelectorAll('[data-asset-id]')].find(el=>el.dataset.assetId===item.id);
      if(row){row.classList.add('highlight');row.scrollIntoView({block:'center'});}
    }});
    content.innerHTML=`${head('搜索结果','“'+state.query+'” · '+matches.length+' 项')}
      <div class="stack">${matches.slice(0,80).map((m,i)=>`<button type="button" class="list-button" data-result="${i}"><span class="kicker">${esc(m.type)}</span><strong>${esc(m.title)}</strong><small>${esc(m.subtitle)}</small></button>`).join('')||'<div class="empty">没有匹配的章节、角色或资产。</div>'}</div>
      ${matches.length>80?'<p class="muted small">结果较多，请输入更具体的关键词。</p>':''}`;
    content.querySelectorAll('[data-result]').forEach(el=>el.addEventListener('click',()=>matches[Number(el.dataset.result)].go()));
  }
  function render() {
    if(!state.bible||!state.inventory||!state.progress)return;
    nav.forEach(button=>button.setAttribute('aria-current',button.dataset.view===state.view?'page':'false'));
    if(state.query){renderSearch();return;}
    ({home:renderHome,world:renderWorld,rules:renderRules,characters:renderCharacters,production:renderProduction,assets:renderAssets}[state.view]||renderHome)();
  }
  async function refreshInventory(){
    const response=await fetch('/inventory',{cache:'no-store'});if(!response.ok)throw new Error('Inventory unavailable');
    const inventory=await response.json();
    if(state.inventory?.updatedAt!==inventory.updatedAt){state.inventory=inventory;if(state.view==='assets'&&!state.query)render();}
  }
  async function refreshProgress(){
    const response=await fetch('/state',{cache:'no-store'});if(!response.ok)throw new Error('Progress unavailable');
    const progress=await response.json();
    if(state.progress?.updatedAt!==progress.updatedAt){state.progress=progress;render();}
  }
  async function refreshPlaytests(){
    const response=await fetch('/playtests',{cache:'no-store'});if(!response.ok)throw new Error('Playtests unavailable');
    const data=await response.json();
    const runs=Array.isArray(data.runs)?data.runs:[];
    if(JSON.stringify(state.playtests)!==JSON.stringify(runs)){state.playtests=runs;if(state.view==='production'&&!state.query)render();}
  }
  async function refreshPlaytestStatus(){
    let next;
    try {
      const response=await fetch('/playtest-status',{cache:'no-store'});
      next=response.ok?await response.json():{phase:'unavailable'};
    } catch (_) {next={phase:'unavailable'};}
    if(JSON.stringify(state.playtestStatus)!==JSON.stringify(next)){
      state.playtestStatus=next;
      if(state.view==='production'&&!state.query)render();
    }
  }
  async function startPlaytest(){
    const button=content.querySelector('#start-playtest');
    if(button)button.disabled=true;
    try {
      const response=await fetch('/start-playtest',{method:'POST'});
      if(!response.ok)throw new Error('Launch failed');
      state.playtestStatus=await response.json();
      render();
    } catch (_) {
      await refreshPlaytestStatus();
      document.getElementById('footer-status').textContent='试玩未能启动；请检查本地游戏文件';
    }
  }
  nav.forEach(button=>button.addEventListener('click',()=>navigate(button.dataset.view)));
  search.addEventListener('input',()=>{state.query=search.value.trim();render();});
  document.addEventListener('visibilitychange',()=>{if(!document.hidden){refreshInventory().catch(()=>{});refreshProgress().catch(()=>{});refreshPlaytests().catch(()=>{});refreshPlaytestStatus().catch(()=>{});}});
  setInterval(()=>{if(!document.hidden){refreshProgress().catch(()=>{});refreshInventory().catch(()=>{});refreshPlaytests().catch(()=>{});refreshPlaytestStatus().catch(()=>{});}},10000);
  Promise.all([
    fetch('/bible',{cache:'no-store'}).then(r=>r.ok?r.json():Promise.reject()),
    fetch('/inventory',{cache:'no-store'}).then(r=>r.ok?r.json():Promise.reject()),
    fetch('/state',{cache:'no-store'}).then(r=>r.ok?r.json():Promise.reject()),
  ]).then(([bible,inventory,progress])=>{
    Object.assign(state,{bible,inventory,progress});
    document.getElementById('edition').textContent=bible.edition;
    document.getElementById('pitch').textContent=bible.pitch;
    document.getElementById('footer-status').textContent=bible.characters.length+' 份人物档案 · '+bible.chapters.length+' 个设计章节';
    render();
    refreshPlaytests().catch(()=>{});
    refreshPlaytestStatus().catch(()=>{});
  }).catch(()=>{content.innerHTML='<div class="empty">游戏圣经暂时无法读取。请确认本地项目面板已启动。</div>';});
})();
