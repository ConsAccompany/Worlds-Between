(() => {
  const content = document.getElementById('content');
  const search = document.getElementById('search');
  const nav = [...document.querySelectorAll('.main-nav button')];
  const state = {
    bible:null, inventory:null, progress:null, playtests:[], playtestStatus:{phase:'loading'}, view:'home', query:'',
    chapter:'chapter-3', character:'hero', board:'全部板块',
    group:'全部来源', assetScope:'all', openGroups:new Set(['characters']), feedbackOpen:false,
    readiness:null, readinessRaw:'', readinessStatus:'idle', readinessFilter:'all',
  };
  const assetStages={planned:'待制作',concept:'概念稿',approved:'已修订',production:'制作中',ready:'可验收'};
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
  // Production-completion side panel. Every number comes from the ledger's derived `computed` block (one CLI computes
  // it); the panel never recomputes a percentage. The legacy acceptance estimate stays collapsed and labelled as legacy.
  function productionPanel(ledger) {
    const c=ledger?.computed;
    if(!c?.production)return '';
    const p=c.production, owners={claude:'Claude',codex:'Codex',creator:'创作者 / Creator'};
    const stageName=s=>({coding:'编码',content:'内容','technical-inspection':'技术检查','visual-review':'视觉审查','creator-approval':'创作者批准'}[s]||s);
    const row=(label,v,extra='')=>`<div class="step-top"><span>${label}</span><span>${esc(v.done)} / ${esc(v.total)} · ${esc(v.percent)}%${extra}</span></div>`;
    const ownerRows=Object.entries(c.byOwner||{}).map(([o,v])=>`<tr><td>${esc(owners[o]||o)}</td><td>${esc(v.tasks)}</td><td>${esc(v.pointsDone)} / ${esc(v.points)}</td><td>${esc(v.readyInQueue)}</td><td class="small">${Object.entries(v.byStatus||{}).map(([s,n])=>esc(s)+' '+esc(n)).join(' · ')}</td></tr>`).join('');
    const queue=(c.queue?.items||[]).map(q=>`<li><span class="muted small">${esc(owners[q.owner]||q.owner)} · ${esc(stageName(q.stage))}</span> <code>${esc(q.id)}</code></li>`).join('');
    const lg=c.legacy||{};
    return `<section class="card" id="production-completion"><div class="step-top"><h3>制作完成度 / Production completion</h3>${badge(p.percentLabel,'accent')}</div>
      <div class="meter" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${esc(p.percent)}"><span style="width:${Math.max(0,Math.min(100,Number(p.percent)||0))}%"></span></div>
      <p class="muted small">衡量已完成的工作量：编码 ${esc(p.coding.weight)}% + 内容 ${esc(p.content.weight)}%（冻结基线任务分值）。检查与批准另计，不增减制作分。与旧版验收估算是不同指标，不是“增长”。</p>
      ${row('编码 / Coding',p.coding,' × '+esc(p.coding.weight)+'%')}${row('内容 / Content',p.content,' × '+esc(p.content.weight)+'%')}
      ${row('检查与审查 / Inspection',c.inspection)}${row('创作者批准 / Creator approval',c.approval)}
      <div class="step-top"><span>正式验收 / Final accepted</span><span>${c.release?.finalAccepted?'是':'否 / false'}</span></div>
      <details class="group"><summary>负责方 / Owners</summary><table class="small"><thead><tr><th>负责方</th><th>任务</th><th>分值</th><th>待处理</th><th>状态</th></tr></thead><tbody>${ownerRows}</tbody></table></details>
      <details class="group"><summary>待检查／审查／批准队列（${esc(c.queue?.count||0)}）</summary><ul class="small">${queue}</ul></details>
      <details class="group"><summary>旧版验收加权估算（不同指标）· ${esc(lg.percentLabel||'')}</summary><p class="small">${esc(lg.note?.zh||'')} ${esc(lg.note?.en||'')}</p></details>
      <p class="muted small receipt-name">任务台账：${esc(ledger.updater||'')} · ${esc(ledger.tasks?.length||0)} 项任务</p></section>`;
  }
  const feedbackKey = route => `worlds-between-m7-feedback-${route}`;
  const readFeedback = route => { try { return localStorage.getItem(feedbackKey(route)) || ''; } catch (_) { return ''; } };
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
        <button class="link-card" data-go="world"><strong>世界与历史</strong><small>地下社区、五个地球文明圈与终局星球、文明协议与幕后威胁</small></button>
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
    const jobs=state.bible.jobProposal;
    const jobProposal=selected.number===4&&jobs ? `<div class="section-label">20 系列 × 5 阶 · 名称与终阶任务已批准</div><div class="card small"><strong>设计边界</strong><ul>${jobs.rules.map(rule=>`<li>${esc(rule)}</li>`).join('')}</ul></div>${['武艺','应变','研学','灵觉'].map(aptitude=>`<details class="group"><summary>${aptitude} · 5 个系列</summary><div class="card">${jobs.series.filter(series=>series.aptitude===aptitude).map(series=>`<details class="subgroup"><summary>${esc(series.name)} <span class="group-count">${esc(series.en)}</span></summary><div class="card small"><p><strong>定位：</strong>${esc(series.role)}</p><p><strong>五阶：</strong>${series.stages.map((name,index)=>`${index+1}. ${esc(name)}`).join(' → ')}</p><p><strong>终阶解锁：</strong>${esc(series.finalQuest)}</p></div></details>`).join('')}</div></details>`).join('')}<p class="muted small">系列名单、五阶名称与终阶任务已获创作者批准（2026-10-15，原文不改）；设计边界条目与技能效果仍为提案，正式数值待战斗平衡后确定。</p>`:'';
    const skillTrees=state.bible.skillTreeProposal;
    const skillTreeProposal=selected.number===4&&skillTrees ? `<div class="section-label">职业技能树 · 已被取代的 7 节点草案（${skillTrees.trees.length} / 20 系列，待重设计）</div><div class="card small"><p><strong>已批准规则（2026-10-15）：</strong>每条系列 10 个节点，5 个阶级各 2 个在进入该阶时立即开放；所有分支最终都可学会；每项技能最高 5 级，用 JP 提升。下列 7 节点、3 级上限的内容是已被取代的草案，仅供参考，不是已批准设计。</p><p>旧草案：第 2、4 阶各有两条并列技能，两条都能学会。技能满级 3 级，达到对应角色等级和职业阶级后获得 1 级；2、3 级消耗 JP。</p><p>${esc(skillTrees.progression.aptitudeDiscount)} 当前数值为提案，战斗平衡后再定。</p></div>${skillTrees.trees.map(tree=>`<details class="group"><summary>${esc(tree.name)} · 7 个节点（旧草案）</summary><div class="card">${tree.nodes.map(node=>`<div class="skill-node"><strong>第 ${node.tier} 阶${node.branch?' · '+esc(node.branch):''}：${esc(node.name)}</strong><span class="muted small">${esc(node.type)}${node.type==='主动'?' · '+node.energy+' 能量':''} · ${esc(node.tags.join(' / '))}</span><p class="small">${esc(node.effect)}</p></div>`).join('')}</div></details>`).join('')}<p class="muted small">按新规则需设计 20 × 10 = 200 个职业节点与 51 × 10 = 510 个个人节点，尚未开始；旧草案（20 条职业树、16 个个人树）均已被取代。</p>`:'';
    const skillNotes=selected.number===4&&skillTrees?.designNotes?.length ? `<details class="group"><summary>职业技能的系统边界</summary><div class="card small"><ul>${skillTrees.designNotes.map(note=>`<li>${esc(note)}</li>`).join('')}</ul></div></details>`:'';
    content.innerHTML=`${head('系统规则','点击章节阅读完整需求基线',badge('6 个章节','accent'))}
      <div class="subnav" role="group" aria-label="规则章节">${chapters.map(c=>`<button type="button" data-chapter="${c.id}" aria-pressed="${c.id===selected.id}">${esc(c.title)}</button>`).join('')}</div>
      <div class="card"><div class="kicker">第 ${selected.number} 章 · ${esc(selected.status)}</div><h3>${esc(selected.title)}</h3><p class="muted">${esc(selected.summary)}</p></div>
      <article class="document">${markdown(selected.body)}${sourceLine(selected.source)}</article>${jobProposal}${skillTreeProposal}${skillNotes}`;
    content.querySelectorAll('[data-chapter]').forEach(el=>el.addEventListener('click',()=>{state.chapter=el.dataset.chapter;render();}));
  }
  function renderCharacters() {
    const b=state.bible;
    const boards=['全部板块','地下社区','科技','自然','奇幻','魔法','星外'];
    // Character data keeps the legacy board values; labels follow the 2026-10-15 creator decisions until companions are re-mapped.
    const boardLabel={'奇幻':'文化（原奇幻）','星外':'终局星球（原星外）'};
    const groups=['全部来源','主角','主线伙伴','支线伙伴','情境招募伙伴'];
    const visible=b.characters.filter(c=>(state.board==='全部板块'||c.board===state.board)&&(state.group==='全部来源'||c.group===state.group));
    const selected=visible.find(c=>c.id===state.character)||visible[0];
    if(selected)state.character=selected.id;
    const personal=selected&&b.personalSkillTrees?.trees.find(tree=>tree.characterId===selected.id);
    const personalHtml=personal?`<div class="section-label">个人专属技能树 · 已被取代的 5 节点草案（待重设计）</div><div class="card small"><p><strong>已批准规则（2026-10-15）：</strong>51 个角色各 10 个个人节点，全部在个人等级 100 以内开放；加入时立即拥有至少一项专属技能；技能最高 5 级，用 JP 提升；任何职业均可使用。下列内容是旧草案，不是已批准设计。</p><strong>${esc(personal.skill)}</strong><p>旧草案：与当前职业无关；角色达到对应等级时获得节点 1 级，节点 2、3 级使用 JP 提升。新加入伙伴按同步等级开放节点。</p><p>${esc(b.personalSkillTrees.progression.aptitude)}</p></div><details class="group"><summary>${esc(personal.name)} · 5 个节点（旧草案）</summary><div class="card">${personal.nodes.map(node=>`<div class="skill-node"><strong>角色 ${node.level} 级：${esc(node.name)}</strong><span class="muted small">${esc(node.mode)}${node.energy?' · '+node.energy+' 能量':''}${node.tags?' · '+esc(node.tags.join(' / ')):''}</span><p class="small">${esc(node.effect)}</p></div>`).join('')}</div></details>`:'';
    const images=selected?.portraits||[selected?.portrait].filter(Boolean);
    const imageHtml=images.length===2
      ? '<div class="portrait-pair">'+images.map((p,i)=>`<a href="${p}" target="_blank" rel="noopener"><img class="portrait" src="${p}" alt="主角${i?'女':'男'}设定图" loading="lazy"></a>`).join('')+'</div>'
      : images.length ? `<a href="${images[0]}" target="_blank" rel="noopener"><img class="portrait" src="${images[0]}" alt="${esc(selected.cn)}的21:9人物设定图" loading="lazy"></a>`:'';
    content.innerHTML=`${head('人物档案','主角和 50 位可招募伙伴；姓名与外观仍可修订',badge('51 份档案','warn'))}
      <div class="filters">
        <label><span class="visually-hidden">按板块筛选</span><select id="board-filter">${boards.map(x=>`<option value="${x}" ${x===state.board?'selected':''}>${boardLabel[x]||x}</option>`).join('')}</select></label>
        <label><span class="visually-hidden">按来源筛选</span><select id="group-filter">${groups.map(x=>`<option ${x===state.group?'selected':''}>${x}</option>`).join('')}</select></label>
      </div>
      <div class="character-layout">
        <div class="character-list" aria-label="角色列表">${visible.map(c=>`<button type="button" class="list-button" data-character="${c.id}" aria-pressed="${c.id===selected?.id}"><strong>${c.number?String(c.number).padStart(2,'0')+' · ':''}${esc(c.cn)}</strong><small>${esc(c.board)} · ${esc(c.group)}</small></button>`).join('')}</div>
        <div class="character-detail">${selected?`
          <div class="card"><div class="kicker">${esc(selected.group)} · ${esc(selected.board)}</div><h3 class="character-name">${esc(selected.cn)} <span class="muted small">/ ${esc(selected.en)}</span></h3>
          <div class="filters">${badge(selected.status,'warn')}${selected.portraitStage?badge(selected.portraitAccepted?'画像已验收':'画像'+(selected.portraitStage==='planned'?'待制作':'概念稿')):''}</div>
          ${imageHtml}<p class="small muted">点击画像查看独立原图。设定图不等同于游戏精灵。</p></div>
          <article class="document">${markdown(selected.body)}${sourceLine(selected.source)}</article>${personalHtml}`:'<div class="empty">当前筛选没有角色。</div>'}</div>
      </div>`;
    document.getElementById('board-filter').addEventListener('change',e=>{state.board=e.target.value;render();});
    document.getElementById('group-filter').addEventListener('change',e=>{state.group=e.target.value;render();});
    content.querySelectorAll('[data-character]').forEach(el=>el.addEventListener('click',()=>{state.character=el.dataset.character;render();}));
  }
  // Character sprite readiness checklist: read-only facts from /character-readiness. Every label below is a lookup
  // of the checklist's own value; unknown values are shown verbatim (escaped) rather than reinterpreted as approval.
  const readinessKind='character_sprite_production_readiness_checklist';
  const readinessValid=data=>data?.schema_version===1&&data.kind===readinessKind&&Array.isArray(data.variants)&&Array.isArray(data.hair_review?.candidate_confusion_groups)&&data.summary&&typeof data.summary==='object';
  const readinessText={
    approved:'已批准',concept:'概念稿',pending:'待定',out_of_mvp_scope:'非 MVP 范围',pending_pilot_values:'待试点数值',
    pending_human_review:'待人工复核',undeclared:'未声明',user_only:'仅用户',not_run_no_production_frames:'未运行（无正式帧）',
    not_started:'未开始',placeholder_32x48_rejected_baseline:'32×48 占位（已否定为画质基线）',unregistered_placeholder_manifest:'未登记的 32×48 占位清单',
  };
  const rt=value=>esc(value==null?'未记录':readinessText[value]??value);
  const readinessRosters={all:'全部 52 个变体',protagonist:'主角',main:'主线伙伴',side:'支线伙伴',situational:'情境招募伙伴',review:'仅含发型复核提示'};
  const portraitHref=file=>typeof file==='string'&&/^outputs\/[A-Za-z0-9._-]+\.png$/.test(file)?'/assets/'+encodeURIComponent(file.slice('outputs/'.length)):'';
  const checkedText=value=>value===true?'已勾选':value===false?'未勾选':'未记录';
  function readinessSection() {
    const status=state.readinessStatus, data=state.readiness;
    const intro='<div class="section-label">角色精灵就绪清单 · 逐变体</div>';
    if(!data){
      const message=status==='error'?'角色就绪清单暂时无法读取。请用当前 server v05 重新启动本地面板以启用 /character-readiness。':'正在读取角色就绪清单…';
      return intro+`<section class="card" id="character-readiness"><p class="muted small" role="status">${esc(message)}</p></section>`;
    }
    const s=data.summary, ready=s.readiness_states||{}, source=s.source_portraits||{};
    const groups=data.hair_review.candidate_confusion_groups;
    const prompts=new Map();
    for(const group of groups)for(const member of group.members||[]){if(!prompts.has(member.visual_id))prompts.set(member.visual_id,[]);prompts.get(member.visual_id).push(group);}
    const filter=state.readinessFilter;
    const visible=data.variants.filter(v=>filter==='all'||(filter==='review'?prompts.has(v.visual_id):v.roster===filter));
    const open=key=>state.openGroups.has(key)?'open':'';
    const gate=(label,value,detail)=>`<div class="gate-row"><span class="gate-name">${esc(label)}</span><span class="badge warn">${value}</span><span class="small muted">${detail}</span></div>`;
    const variantRow=v=>{
      const g=v.gates||{}, art=g.source_art||{}, facing=g.four_facing||{}, walk=g.exploration_animation||{}, combat=g.combat_animation||{}, scale=g.scale||{}, qa=g.qa||{}, accept=g.art_acceptance||{}, display=g.runtime_display||{};
      const href=portraitHref(art.portrait?.path), mine=prompts.get(v.visual_id)||[];
      const placeholderDirections=Object.keys(facing.placeholder_directions||{}).length;
      const scaleOpen=['master','scale','cell_size','ground_pin'].filter(key=>scale[key]==null).length;
      const key='readiness.'+v.visual_id;
      return `<details class="readiness-row" data-readiness-open="${esc(key)}" ${open(key)}><summary><span class="readiness-num">${esc(String(v.ordinal).padStart(2,'0'))}</span><strong>${esc(v.display_name_zh)}</strong> <code>${esc(v.visual_id)}</code><span class="readiness-badges">${badge('立绘'+(readinessText[art.approval]??art.approval??'未记录'),art.approval==='approved'?'good':'warn')}${badge('美术验收 '+(readinessText[accept.status]??accept.status??'未记录'),'warn')}${mine.length?badge('复核提示 ×'+mine.length,'prompt'):''}</span></summary>
        <div class="readiness-body small">
          <p><strong>身份／发型锚点（注册表原文）：</strong>${v.anchor_has_hair===false?'<span class="muted">（锚点无发型，机器人头部外廓）</span>':''}「${esc(v.identity_and_hair_anchor)}」</p>
          <p><strong>来源立绘：</strong>${rt(art.approval)} · <span class="receipt-name">${esc(art.portrait?.path||'未登记')}</span>${art.portrait?.exists===false?' · <span class="warn-text">文件缺失</span>':''}${href?` · <a href="${href}" target="_blank" rel="noopener">查看</a>`:''}</p>
          <p><strong>就绪状态：</strong>${rt(v.readiness_state)} · 入库阶段 ${esc(v.intake_stage)}</p>
          <div class="gate-list">
            ${gate('G1 四方向',rt(facing.status),`正式 ${esc((facing.production_directions_done||[]).length)}/${esc((facing.required_directions||[]).length)}${placeholderDirections?` · 占位 ${esc(placeholderDirections)} 向`:''} · 西向绘制 ${rt(facing.west_authoring)}`)}
            ${gate('G2 探索动画',rt(walk.status),`${walk.placeholder_idle_frames||walk.placeholder_walk_frames?`占位 待机 ${esc(walk.placeholder_idle_frames||0)} + 行走 ${esc(walk.placeholder_walk_frames||0)} · `:''}正式帧数${walk.frame_counts_user_approved===true?'已获用户批准':'未批准'}${walk.static_idle_baseline?` · 静态基准帧：${esc(walk.static_idle_baseline.facing)} ${esc(walk.static_idle_baseline.pose)} ${esc(walk.static_idle_baseline.candidate)}，用户回复「${esc(walk.static_idle_baseline.user_reply_zh)}」（只是单张静态基准，本闸门不因此通过）`:''}`)}
            ${gate('G2c 战斗动画',rt(combat.status),combat.mvp_required?`MVP 必需 · 原型 ${esc(combat.prototype_actions??0)} 动作 ${esc(combat.prototype_frames??0)} 帧 · 资产清单${checkedText(combat.inventory_checked)}`:'资产清单为完整游戏范围')}
            ${gate('G3 比例',rt(scale.status),`显示高度 ${esc(scale.target_display_height_logical_px??'未记录')} 逻辑像素 · ${scaleOpen?`${esc(scaleOpen)} 项数值未定`:'数值已登记'}`)}
            ${gate('G4 QA',rt(qa.status),`自动检查 ${rt(qa.automated_metadata_checks)} · 实机回执${qa.in_engine_capture_receipt?'已登记':'无'} · 人工复核 ${rt(qa.human_identity_direction_review)}`)}
            ${gate('G5 美术验收',rt(accept.status),`决定人 ${rt(accept.decided_by)} · 资产清单${checkedText(accept.inventory_checked)} · 回执${accept.receipt?'已登记':'无'}`)}
            ${gate('显示图',rt(display.status),`${esc(assetStages[display.inventory_stage]||display.inventory_stage||'未记录')} · 资产清单${checkedText(display.inventory_checked)}`)}
          </div>
          ${mine.length?`<div class="review-prompt"><strong>复核提示（不是决定）：</strong><ul>${mine.map(group=>`<li><code>${esc(group.group)}</code> · ${esc(group.concern)}</li>`).join('')}</ul></div>`:''}
        </div></details>`;
    };
    const groupCard=group=>`<div class="review-prompt"><div class="step-top"><span><span class="kicker">复核提示</span> <code>${esc(group.group)}</code></span>${badge(readinessText[group.decision]??group.decision??'未记录','prompt')}</div><ul>${(group.members||[]).map(m=>`<li><strong>${esc(m.display_name_zh)}</strong> <code>${esc(m.visual_id)}</code>：「${esc(m.anchor)}」</li>`).join('')}</ul><p class="muted">${esc(group.concern)}</p></div>`;
    const notes=data.hair_review.anchor_notes||[], robots=data.hair_review.no_hair_robot_variants||[], paths=data.path_check||{};
    return intro+`<section class="card" id="character-readiness">
      <p class="muted small">事实清单，只读显示，不批准任何素材。下列数值均来自清单 JSON；美术验收只由用户决定。生成与校验见清单所附脚本。</p>
      <div class="readiness-summary small">
        <div><strong>来源立绘</strong>已批准 ${esc(source.approved??0)} · 概念稿 ${esc(source.concept??0)}</div>
        <div><strong>就绪状态</strong>未开始 ${esc(ready.not_started??0)} · 32×48 占位（已否定）${esc(ready.placeholder_32x48_rejected_baseline??0)} · 未登记占位清单 ${esc(ready.unregistered_placeholder_manifest??0)}</div>
        <div><strong>美术验收</strong>${esc(s.art_accepted??0)} / ${esc(data.variants.length)} · MVP 战斗 ${esc(s.combat_mvp_accepted??0)} / ${esc((data.scope?.combat_mvp_variants||[]).length)} · 显示图 ${esc(s.runtime_display_accepted??0)} / ${esc(data.variants.length)}</div>
        <div><strong>入库阶段</strong>阶段 0：${esc(s.intake_stage_0??0)} · 正式帧数${s.any_manifest_declares_frame_counts?'已有清单声明':'均未声明'}</div>
      </div>
      <p class="muted small">四方向、探索动画、比例、QA 与美术验收闸门对全部变体均为待定；战斗动画只对 MVP 可玩五形象要求。</p>
      <div class="filters"><label><span class="visually-hidden">筛选就绪清单</span><select id="readiness-filter">${Object.entries(readinessRosters).map(([value,label])=>`<option value="${value}" ${value===filter?'selected':''}>${label}</option>`).join('')}</select></label><span class="muted small">显示 ${esc(visible.length)} / ${esc(data.variants.length)}</span></div>
      <div class="readiness-list">${visible.map(variantRow).join('')||'<div class="empty">当前筛选没有变体。</div>'}</div>
      <details class="group" data-readiness-open="readiness.hair" ${open('readiness.hair')}><summary>发型潜在混淆 · ${esc(groups.length)} 组复核提示 <span class="group-count">待人工复核</span></summary><div class="card small">
        <p class="muted">以下只是 48 px 精灵尺度下的潜在混淆提示，不改写角色设定、发型或已批准立绘；是否处理由用户决定。</p>
        ${groups.map(groupCard).join('')}
        ${notes.length?`<strong>锚点本身含糊</strong><ul>${notes.map(n=>`<li><code>${esc(n.visual_id)}</code>：${esc(n.note)}</li>`).join('')}</ul>`:''}
        ${robots.length?`<p><strong>无发型的机器人变体（${esc(robots.length)}）：</strong>${robots.map(id=>`<code>${esc(id)}</code>`).join(' ')}；需确认以头部外廓代替发型锚点。</p>`:''}
      </div></details>
      <p class="muted small">路径核对：缺失 ${esc((paths.missing||[]).length)} · 已引用未跟踪 ${esc((paths.untracked_but_referenced||[]).length)} · 注册表差异 ${esc((paths.registry_discrepancies||[]).length)}（只记录，未修改注册表）。</p>
    </section>`;
  }
  async function refreshReadiness(){
    try {
      const response=await fetch('/character-readiness',{cache:'no-store'});if(!response.ok)throw new Error('Readiness unavailable');
      const text=await response.text();
      if(text===state.readinessRaw&&state.readiness)return;
      const data=JSON.parse(text);if(!readinessValid(data))throw new Error('Unexpected readiness format');
      Object.assign(state,{readiness:data,readinessRaw:text,readinessStatus:'ready'});
    } catch (_) {
      if(state.readiness)return;
      state.readinessStatus='error';
    }
    if(state.view==='production'&&!state.query)render();
  }
  function renderProduction() {
    const p=state.progress, done=p.steps.filter(s=>s.status==='done').length;
    const current=p.steps.find(s=>s.id===p.currentStep)||p.steps.find(s=>s.status!=='done');
    const status={done:'已完成',ready:'待开始',todo:'未开始',in_progress:'进行中',review:'待验收',blocked:'受阻'};
    const copy={
      M1:['项目基础','可启动游戏、切换中英文，并进入和离开基础场景。','Windows 上正常启动；语言可切换；像素显示清晰。'],
      M2:['全球地图与探索','全球与地区地图、路线预览、整点旅时与只显示日期的日历、存档迁移、首城、开始年份和纽约—芝加哥航线已实现，并通过自动测试；地图美术和人工审阅仍未完成。','从全球地图进入科技区真实地点；旅行按固定整点旅时推进日历（只显示年月日），并可正确存读档。'],
      M3:['战斗核心','建立横向平地战斗、基础动作、能量、敌人和战后恢复。','能打赢或战败；无跳跃；验证 20%／10% 恢复和重复接敌。'],
      M4:['伙伴与 AI','实现五个队伍位置、三种招募路线、等级同步、切换角色与指令。','三位伙伴都能招募；四人队伍可获胜；AI 与临时指令生效。'],
      M5:['等级与职业','加入经验、JP、四项天分、四条职业系列和 10 级必选职业。','可留任、晋升、切换并保留原系列进度；候补获得 25% 收益。'],
      M6:['存档与恢复','加入战后自动存档、手动存档及队伍和职业状态加载。','重新启动后能读取关键状态；战败回菜单后可加载。'],
      M7:['可玩内容','科技板块三地探索、六处勘察空间、九组证据关联、六处现场痕迹、六段伙伴交流、三位伙伴招募与回城汇报已连通。','不用开发工具通关；两种探索和招募顺序可行；中英文显示完整，并实测 25–35 分钟内容长度。'],
      M8:['角色与场景美术','51 位角色的游戏内展示图和探索精灵；科技区地图、三地点、六勘察空间及战场的完成画面。','52 份视觉身份可按角色读取；可玩角色使用独立动作；11 项场景画质通过运行画面审查。'],
      M9:['整体验收与调整','将科技区玩法与完成美术合并，实测画质、性能、操作、招募、存档与双语。','两次不同顺序的新档试玩均完整通关；画面与内容通过验收。'],
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
    const feedbackFields=[['first','第一轮 · 城市 → 城外 → 遗址'],['second','第二轮 · 遗址 → 城外 → 城市']].map(([key,label])=>`<label class="feedback-field"><strong>${label}</strong><textarea data-feedback="${key}" rows="4" maxlength="4000" placeholder="记下迷路、操作不明、文字溢出、战斗难度，以及你想继续探索的原因。">${esc(readFeedback(key))}</textarea></label>`).join('');
    const assets=state.inventory.categories.flatMap(category=>category.subcategories.flatMap(group=>group.items));
    const countAssets=prefix=>assets.filter(item=>item.id.startsWith(prefix));
    const portraits=countAssets('portrait.'), displays=countAssets('display.'), sprites=countAssets('runtime-sprite.'), scenes=countAssets('visual-scene.');
    const citySample=assets.find(item=>item.id==='art.scifi-city-sample');
    const characterReview=state.bible.characterVisualReview||{};
    const environmentReview=state.bible.environmentVisualReview||{};
    // Cross-device review queue (2026-10-16): six actual Godot captures, badges read from the recorded flags; generated concepts listed apart, never as images.
    const reviewQueue=environmentReview.crossDeviceReviewQueue;
    const queueSrc=file=>typeof file==='string'&&/^outputs\/([A-Za-z0-9][A-Za-z0-9._-]*\/){0,2}[A-Za-z0-9][A-Za-z0-9._-]*\.png$/.test(file)?'/assets/'+file.slice('outputs/'.length).split('/').map(encodeURIComponent).join('/'):'';
    const queueBadge=item=>badge((item.creatorApproved===true?'已批准静态基准':'未批准')+(item.runtimeIntegrated===true?' · 已接入运行时':' · 未接入运行时')+(item.artAccepted===true?'':' · 未验收'),item.creatorApproved===true?'good':'warn');
    const queueSync=item=>item.syncState==='local-only'?badge('仅本机 · 尚未同步到 GitHub','warn'):item.syncState==='staged-not-pushed'?badge('已暂存为 Git 候选 · 尚未推送，其他设备不可见','warn'):/^committed-at-[0-9a-f]{7,40}$/.test(String(item.syncState))?badge('已在 GitHub（'+item.syncState.slice('committed-at-'.length)+'）'):badge('同步状态未知','warn');
    const queueFigure=item=>{const src=queueSrc(item.file);return `<figure class="visual-sample review-queue-item" data-queue-order="${esc(item.order)}">${src?`<a href="${esc(src)}" target="_blank" rel="noopener"><img src="${esc(src)}" alt="${esc((item.label?.zh||'')+' · Godot 实机截图')}" loading="lazy"></a>`:'<div class="empty small">图片路径无法解析，未显示</div>'}<figcaption><span class="preview-head"><strong>${esc(item.order+'. '+(item.label?.zh||''))}</strong> ${queueBadge(item)} ${queueSync(item)}</span>${esc(item.caption?.zh||'')} <span class="muted">${esc(item.caption?.en||'')}</span></figcaption></figure>`;};
    const queueItems=Array.isArray(reviewQueue?.items)?reviewQueue.items.filter(item=>item&&item.kind==='actual-godot-capture'):[];
    const queueConcepts=Array.isArray(reviewQueue?.nonruntimeConcepts?.items)?reviewQueue.nonruntimeConcepts.items:[];
    // Current candidates first (2026-10-18): the latest committed UNAPPROVED candidates lead, each with its limited scope; the
    // scoped reference (#1) follows, and every older entry stays in a collapsed history section. Flags still drive the badges.
    const currentView=reviewQueue?.currentCandidates;
    // Typed media (2026-10-18): every card keeps kind actual-godot-capture (the contract the private Site v15 also enforces) and
    // mediaType alone picks image or video. No mediaType, or image/png, keeps the flat PNG path; video/mp4 needs an outputs/ root
    // .mp4 and a sha256 pin, and plays only through the server's pinned /media/ route with native controls, no autoplay or loop,
    // at the default 1x rate. Any other type, path or pin renders as text only; any other kind is not rendered.
    const currentItems=Array.isArray(currentView?.items)?currentView.items.filter(item=>item&&item.kind==='actual-godot-capture'):[];
    const supersededCurrent=Array.isArray(currentView?.supersededCurrent)?currentView.supersededCurrent.filter(item=>item&&item.kind==='actual-godot-capture'):[];
    const queueMedia=item=>{
      if(item.mediaType===undefined||item.mediaType==='image/png'){const src=queueSrc(item.file);return src?`<a href="${esc(src)}" target="_blank" rel="noopener"><img src="${esc(src)}" alt="${esc((item.label?.zh||'')+' · Godot 实机截图')}" loading="lazy"></a>`:'<div class="empty small">图片路径无法解析，未显示</div>';}
      if(item.mediaType==='video/mp4'){const ok=typeof item.file==='string'&&/^outputs\/[A-Za-z0-9][A-Za-z0-9._-]*\.mp4$/.test(item.file)&&/^[0-9a-f]{64}$/.test(String(item.sha256));
        return ok?`<video class="review-queue-video" controls preload="metadata" playsinline src="${esc('/media/'+encodeURIComponent(item.file.slice('outputs/'.length)))}" data-sha256="${esc(item.sha256)}" aria-label="${esc((item.label?.zh||'')+' · Godot 实机录像，正常 1× 播放')}"></video>`:'<div class="empty small">视频路径或固定哈希无效，未显示</div>';}
      return '<div class="empty small">不支持的媒体类型，未显示</div>';};
    const motionText=item=>{const m=item.motionView;if(!m)return '';return `<span class="small">画面：${esc(m.canvas||'')} · 女主 ${esc(m.heroineHeightLogicalPx)} 逻辑像素 · ${esc(m.playback||'')}</span> <span class="small">${esc(m.inspection?.zh||'')}</span><ul class="small">${(m.limits?.zh||[]).map(l=>`<li>${esc(l)}</li>`).join('')}</ul><span class="small">${esc(m.approvalNote?.zh||'')}</span>`;};
    const choicesText=item=>Array.isArray(item.unresolvedChoices?.zh)&&item.unresolvedChoices.zh.length?`<span class="small">未决选择：</span><ul class="small">${item.unresolvedChoices.zh.map(c=>`<li>${esc(c)}</li>`).join('')}</ul>`:'';
    const scopeBadges=item=>(item.optInOnly===true?' '+badge('仅选择性开启 · 默认关闭','warn'):'')+(item.testOnly===true?' '+badge('仅测试','warn'):'')+(item.designCandidateOnly===true?' '+badge('仅设计候选','warn'):'');
    const referenceOrders=new Set(Array.isArray(currentView?.scopedReferenceOrders)?currentView.scopedReferenceOrders:[]);
    const currentFigure=(item,old=false)=>{const supersedes=(item.supersedesQueueOrders||[]).length?' · 取代历史 '+item.supersedesQueueOrders.map(o=>'#'+o).join('、'):'';return `<figure class="visual-sample review-queue-item review-queue-current${old?' review-queue-superseded':''}" ${old?'data-superseded-id':'data-current-id'}="${esc(item.id)}"${item.mediaType?` data-media-type="${esc(item.mediaType)}"`:''}>${queueMedia(item)}<figcaption><span class="preview-head"><strong>${esc((old?'已被取代 · ':'当前 '+item.rank+'. ')+(item.label?.zh||''))}</strong> ${queueBadge(item)}${scopeBadges(item)} ${queueSync(item)}</span><span class="small">范围：${esc(item.scope?.zh||'')}${esc(supersedes)}</span> ${esc(item.caption?.zh||'')} ${motionText(item)}${choicesText(item)}<span class="muted">${esc(item.scope?.en||'')} ${esc(item.caption?.en||'')}</span></figcaption></figure>`;};
    const referenceItems=queueItems.filter(item=>referenceOrders.has(item.order)), historyItems=queueItems.filter(item=>!referenceOrders.has(item.order));
    const queueBody=currentItems.length?`<p class="small">${esc(currentView.zh||'')}</p><p class="muted small">${esc(currentView.en||'')}</p><h4 id="review-queue-current">当前候选（${currentItems.length}）· 均未批准 · ${esc(currentView.asOf||'')}</h4><div class="idle-v2-grid">${currentItems.map(item=>currentFigure(item)).join('')}</div>${referenceItems.length?`<h4>限定范围参考（${referenceItems.length}）</h4><div class="idle-v2-grid">${referenceItems.map(queueFigure).join('')}</div>`:''}<details class="group" id="review-queue-history"><summary>历史对照（${historyItems.length+supersededCurrent.length}）· 较早条目，仅作比较</summary><div class="idle-v2-grid">${supersededCurrent.map(item=>currentFigure(item,true)).join('')}${historyItems.map(queueFigure).join('')}</div></details>`:`<div class="idle-v2-grid">${queueItems.map(queueFigure).join('')}</div>`;
    const reviewQueueCard=queueItems.length?`<section class="card" id="cross-device-review-queue"><div class="step-top"><h3>跨设备视觉审查队列 · ${esc(reviewQueue.asOf||'')}</h3>${badge((queueItems.length+currentItems.length+supersededCurrent.length)+' 项 Godot 实机截图／录像 · 均不计入验收','warn')}</div><p class="small">${esc(reviewQueue.zh||'')}</p><p class="muted small">${esc(reviewQueue.en||'')}</p>${queueBody}${queueConcepts.length?`<details class="group"><summary>非运行时参考（${queueConcepts.length}）· 生成概念图，不是游戏画面</summary><div class="card small"><p>${esc(reviewQueue.nonruntimeConcepts.zh||'')}</p><ul>${queueConcepts.map(c=>`<li>${badge(c.kind==='identity-reference'?'身份参考 · 非运行时':'生成概念 · 非运行时','warn')} ${esc(c.label||'')} <code class="source-path">${esc(c.file||'')}</code></li>`).join('')}</ul></div></details>`:''}<p class="muted small receipt-name">队列记录：${esc(reviewQueue.source||'')}</p></section>`:'';
    const checked=items=>items.filter(item=>item.checked).length;
    const pct=Math.round(100*done/p.steps.length);
    // Female south idle refinement candidates (2026-10-14): static frames awaiting the user's review, not approved.
    const idleRefineCapture=(area,variant)=>`/assets/rpg-2-star-ocean-the-second_${area}_protagonist-female-south-idle-refine-${variant}-candidate-h48_m8-v01_20261014-231811-850083fd.png`;
    const idleRefineCandidates=[
      ['inkline','描线版 inkline','全轮廓近黑描线，41 色；睫毛带外挑，2 像素嘴。','fb830d80'],
      ['selout','选择性描线版 selout','轮廓按各材质取最深色，26 色；无外挑睫毛，带腮红像素。','4d141ad5'],
    ];
    const idleRefineCard=([variant,title,note,hash])=>`<section class="card" id="idle-refine-${variant}"><div class="step-top"><h3>女主南向静态待机 · ${esc(title)}</h3>${badge('待用户审阅 · 未批准','warn')}</div><p class="small">${esc(note)} 80×112 单帧，可见身体 43×96，按 48 逻辑像素显示。</p><figure class="visual-sample idle-refine"><a href="${idleRefineCapture('city',variant)}" target="_blank" rel="noopener"><img src="${idleRefineCapture('city',variant)}" alt="科技城 1280×720 Godot 实机画面：女主南向待机 ${esc(variant)} 候选与 32×48 占位并排" loading="lazy"></a><figcaption>科技城 1280×720 实机画面，左侧为旧 32×48 占位。点击打开原尺寸。</figcaption></figure><p class="small">其他 1280×720 实机画面：<a href="${idleRefineCapture('outskirts-bright',variant)}" target="_blank" rel="noopener">明亮城外</a> · <a href="${idleRefineCapture('prototype-room-dark',variant)}" target="_blank" rel="noopener">暗色原型室</a></p><p class="muted small">先定静态帧，行走帧暂停：此前的实验性行走帧原型与已否定的四相试循环仍保留，静态门槛之后没有新做行走帧，也没有任何行走动画获批准。未接入可玩角色。探索精灵验收仍为 0/52，场景画质仍为 0/11。自动 QA 只做测量，未经人工审阅。</p><p class="muted small receipt-name">源文件：game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-refine-${variant}-candidate_m8-v01_20261014-231100-${hash}.png</p></section>`;
    // Selout v2 static polish (2026-10-14): the user chose selout v1 as closer and called v2 closer still, but v2 is NOT approved.
    const seloutV2Capture=(area,variant)=>`/assets/rpg-2-star-ocean-the-second_${area}_protagonist-female-south-idle-selout-${variant}-h48_m8-v02_20261014-234215-2a1b6b58.png`;
    const seloutV2Areas=[
      ['city','科技城','科技城默认首访布局，左侧为旧 32×48 占位'],
      ['outskirts-bright','明亮城外','阳光下的城外铺地（亮场景），右侧为旧 32×48 占位'],
      ['survey-annex-room2-dark','暗色勘察附楼','科技城勘察附楼 2 号室（最暗的可玩房间），左侧为旧 32×48 占位'],
    ];
    const seloutV2Figure=([area,label,note])=>`<figure class="visual-sample idle-refine"><a href="${seloutV2Capture(area,'v2')}" target="_blank" rel="noopener"><img src="${seloutV2Capture(area,'v2')}" alt="${esc(label)} 1280×720 Godot 实机画面：女主南向待机 selout v2 候选" loading="lazy"></a><figcaption>${esc(label)} · ${esc(note)}。<a href="${seloutV2Capture(area,'v1-reference')}" target="_blank" rel="noopener">同场景 v1 对照</a></figcaption></figure>`;
    const pilotDir='game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-';
    const seloutV2Card=`<section class="card" id="idle-selout-v2"><div class="step-top"><h3>女主南向静态待机 · 选择性描线版 selout v2 精修</h3>${badge('比 v1 更接近 · 仍未批准','warn')}</div><p class="small">在 selout v1 上逐像素精修 550 个像素：马尾轮廓与留白、马尾暖色高光走向、3/4 侧脸五官与下巴、青色围巾与棕色外套分界、外套与双手分离。27 色（新增嘴部 1 色），80×112 单帧，可见身体 43×96，按 48 逻辑像素显示；第 72 行以下（护膝、腿、靴）与 v1 逐字节相同。</p><div class="idle-v2-grid">${seloutV2Areas.map(seloutV2Figure).join('')}</div><p class="small">另一张暗场景：<a href="${seloutV2Capture('prototype-room-dark','v2')}" target="_blank" rel="noopener">暗色原型测试室 v2</a>（<a href="${seloutV2Capture('prototype-room-dark','v1-reference')}" target="_blank" rel="noopener">v1 对照</a>）。均为单独的 1280×720 Godot 画面，v1 对照为同一次运行所拍。</p><p class="muted small"><strong>状态：未批准。</strong>用户认为 v2 比 v1 更接近，但尚未批准；静态帧继续打磨，行走帧仍暂停：此前的实验性行走帧原型与已否定的四相试循环仍保留，静态门槛之后没有新做行走帧，也没有任何行走动画获批准。未接入可玩角色。探索精灵验收仍为 0/52，场景画质仍为 0/11。自动 QA 只做测量（human_reviewed: false）。</p><p class="muted small receipt-name">v2 源文件：${pilotDir}selout-v2-polish-candidate_m8-v02_20261014-233300-d2eeefa2.png</p><p class="muted small receipt-name">v1 可编辑基线（Pixelorama .pxo，内容为 v1，不是 v2）：${pilotDir}selout-pixelorama-baseline_m8-v01_20261014-233500-5e93c40a.pxo</p></section>`;
    const seloutV4Capture=(area,variant)=>`/assets/rpg-2-star-ocean-the-second_${area}_protagonist-female-south-idle-selout-${variant}-h48_m8-v04_20261015-001305-7973118b.png`;
    const seloutV4Figure=([area,label,note])=>`<figure class="visual-sample idle-refine"><a href="${seloutV4Capture(area,'v4')}" target="_blank" rel="noopener"><img src="${seloutV4Capture(area,'v4')}" alt="${esc(label)} 1280×720 Godot 实机画面：女主南向待机 selout v4 结构性技术候选" loading="lazy"></a><figcaption>${esc(label)} · ${esc(note)}。<a href="${seloutV4Capture(area,'v3-reference')}" target="_blank" rel="noopener">同场景 v3 对照</a></figcaption></figure>`;
    const seloutV4Card=`<section class="card" id="idle-selout-v4"><div class="step-top"><h3>女主南向静态待机 · selout v4 结构性技术候选</h3>${badge('技术候选 · 未批准 · 未经用户审阅','warn')}</div><p class="small">在 selout v3 上做结构性重画：躯干第 34–62 行改为成组的明暗块面（外套前襟、衬衫与系带、腰带、侧挂罐、衬衫下摆），马尾顶簇由单个尖角改为收拢的扇形。相对 v3 改动 358 个像素，仍为 27 色、无新增颜色，80×112 单帧，可见身体 43×96，按 48 逻辑像素显示。自动测量的躯干杂点由 95/983 降到 49/983；这只是数字，不代表画质判断。</p><div class="idle-v2-grid">${seloutV2Areas.map(seloutV4Figure).join('')}</div><p class="small">另一张暗场景：<a href="${seloutV4Capture('prototype-room-dark','v4')}" target="_blank" rel="noopener">暗色原型测试室 v4</a>（<a href="${seloutV4Capture('prototype-room-dark','v3-reference')}" target="_blank" rel="noopener">v3 对照</a>）。均为单独的 1280×720 Godot 画面，v3 对照为同一次运行所拍；每个场景 v4 与 v3 相差 358 个窗口像素，v4 纹素与源图 2443/2443 完全一致。</p><p class="muted small">已知局限：编辑图依据纹素角色表编写；Codex 先渲染一张 8 倍预览，Claude 看过后修订脚本，Codex 再渲染第二张 8 倍预览，之后才输出最终 PNG 与 Godot 截图；48 像素下改动仍很小，大块马尾仍是最重的形状；左下外套下摆、腰包与裤子保留 v3 纹理；部分小细节（额外的带子、缝线、下方腰包）被简化。可能还需要再改一轮。</p><p class="muted small"><strong>状态：未批准。</strong>v4 是技术候选，用户尚未做视觉审阅（human_reviewed: false），也未获美术批准。行走帧仍暂停：此前的实验性行走帧原型与已否定的四相试循环仍保留，静态门槛之后没有新做行走帧，没有任何行走动画获批准（动画验收为 0）。未接入可玩角色。探索精灵验收仍为 0/52，场景画质仍为 0/11。</p><p class="muted small receipt-name">v4 源文件：${pilotDir}selout-v4-structural-candidate_m8-v04_20261015-001500-e5b81f36.png</p><p class="muted small receipt-name">QA 报告：outputs/rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v4-visual-qa-report_m8-v04_20261015-001305-7973118b.json</p></section>`;
    // Selout v5 (2026-10-14): lower body + ponytail fall over v4. The user reviewed the v5 city/dark captures and replied
    // "更接近了，继续精修" (closer, keep refining): reviewed, NOT approved, further refinement requested.
    const seloutV5Capture=(area,variant)=>`/assets/rpg-2-star-ocean-the-second_${area}_protagonist-female-south-idle-selout-${variant}-h48_m8-v05_20261015-002513-a59b7bc1.png`;
    const seloutV5Figure=([area,label,note])=>`<figure class="visual-sample idle-refine"><a href="${seloutV5Capture(area,'v5')}" target="_blank" rel="noopener"><img src="${seloutV5Capture(area,'v5')}" alt="${esc(label)} 1280×720 Godot 实机画面：女主南向待机 selout v5 技术候选" loading="lazy"></a><figcaption>${esc(label)} · ${esc(note)}。<a href="${seloutV5Capture(area,'v4-reference')}" target="_blank" rel="noopener">同场景 v4 对照</a></figcaption></figure>`;
    const seloutV5Card=`<section class="card" id="idle-selout-v5"><div class="step-top"><h3>女主南向静态待机 · selout v5 下半身与马尾技术候选</h3>${badge('技术候选 · 未批准 · 用户要求继续精修','warn')}</div><p class="small">在 selout v4 上改动 309 个像素：下半身与外套下摆改为三阶明暗块面（202），腰带减为一行、扣环改为 2×1 金属标记（18），马尾下垂部分收窄 1 像素、缩短 2 行（56，只有这里改动透明度），左袖口调暗（32），左拳高光 1 像素。仍为 27 色、无新增颜色，80×112 单帧，可见身体 43×96，按 48 逻辑像素显示；马尾变细后不透明纹素为 2419（v4 为 2443）。自动测量的下半身杂点由 30/434 降到 21/434，右腿 13→3，但左腿 4→6、马尾 2→4 略有上升；这只是数字，不代表画质判断。</p><div class="idle-v2-grid">${seloutV2Areas.map(seloutV5Figure).join('')}</div><p class="small">另一张暗场景：<a href="${seloutV5Capture('prototype-room-dark','v5')}" target="_blank" rel="noopener">暗色原型测试室 v5</a>（<a href="${seloutV5Capture('prototype-room-dark','v4-reference')}" target="_blank" rel="noopener">v4 对照</a>）。均为单独的 1280×720 Godot 画面，v4 对照为同一次运行所拍；每个场景 v5 与 v4 相差 309 个窗口像素，v5 纹素与源图 2419/2419 完全一致。</p><p class="muted small">已知局限：编辑图依据纹素重建编写，编写时 Claude 没有看到 v5 的结果；之后才有一张 8 倍放大复查图。马尾顶簇、扎带与头冠未改，头发仍是最大的单一形状；右手后方的外套下摆和小腿以下（护膝、靴子）保留 v4 纹理；缝线和额外的带子没有画；在暖米色铺地上外套对比仍偏低。48 像素下改动仍很小，可能还需要再改一轮。</p><p class="muted small"><strong>状态：未批准。</strong>用户已查看 v5 的城市与暗场景截图，回复“更接近了，继续精修”：v5 比之前更接近目标，但仍未获美术批准，需要继续精修。QA 报告与 v5 清单（manifest）中的 human_reviewed: false 是生成时的记录：报告早于用户回复生成，清单中的值由编辑脚本固定写入；两者保留不改，不代表当前审阅状态。行走帧仍暂停：此前的实验性行走帧原型与已否定的四相试循环仍保留，静态门槛之后没有新做行走帧，没有任何行走动画获批准（动画验收为 0）。未接入可玩角色。探索精灵验收仍为 0/52，场景画质仍为 0/11。</p><p class="muted small receipt-name">v5 源文件：${pilotDir}selout-v5-lowerbody-hair-candidate_m8-v05_20261015-004000-8b3e5c07.png</p><p class="muted small receipt-name">QA 报告：outputs/rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v5-visual-qa-report_m8-v05_20261015-002513-a59b7bc1.json</p></section>`;
    // Selout v6 (2026-10-14): darker coat + ink contour on cloth edges over v5. The user reviewed v6 and replied
    // "明亮场景对比度仍不足" (contrast in bright scenes is still not enough): reviewed, NOT approved.
    const seloutV6Capture=(area,variant)=>`/assets/rpg-2-star-ocean-the-second_${area}_protagonist-female-south-idle-selout-${variant}-h48_m8-v06_20261015-003321-9bfd5b9e.png`;
    const seloutV6Figure=([area,label,note])=>`<figure class="visual-sample idle-refine"><a href="${seloutV6Capture(area,'v6')}" target="_blank" rel="noopener"><img src="${seloutV6Capture(area,'v6')}" alt="${esc(label)} 1280×720 Godot 实机画面：女主南向待机 selout v6 技术候选" loading="lazy"></a><figcaption>${esc(label)} · ${esc(note)}。<a href="${seloutV6Capture(area,'v5-reference')}" target="_blank" rel="noopener">同场景 v5 对照</a></figcaption></figure>`;
    const seloutV6Card=`<section class="card" id="idle-selout-v6"><div class="step-top"><h3>女主南向静态待机 · selout v6 明度与轮廓分离技术候选</h3>${badge('技术候选 · 未批准 · 明亮场景对比度仍不足','warn')}</div><p class="small">在 selout v5 上改动 301 个像素，只换颜色、不改形状：外套区域整体压暗一档（275），第 34–79 行布料外缘改为近黑描边 #0a0a0e（26）。透明度与 v5 完全相同；第 8–33 行（头发、马尾、脸）和第 80 行以下（靴子）不变，青色、皮肤和金属纹素不变。仍为 27 色、无新增颜色，80×112 单帧，可见身体 43×96，不透明纹素 2419，按 48 逻辑像素显示。自动测量：外套平均亮度 76.55→63.70，衬衫 178.55 不变；132 个轮廓纹素中亮度低于 40 的比例 79.6%→99.2%。这只是数字，不代表画质判断。</p><div class="idle-v2-grid">${seloutV2Areas.map(seloutV6Figure).join('')}</div><p class="small">另一张暗场景：<a href="${seloutV6Capture('prototype-room-dark','v6')}" target="_blank" rel="noopener">暗色原型测试室 v6</a>（<a href="${seloutV6Capture('prototype-room-dark','v5-reference')}" target="_blank" rel="noopener">v5 对照</a>）。均为单独的 1280×720 Godot 画面，v5 对照为同一次运行所拍；每个场景 v6 与 v5 相差 301 个窗口像素，v6 纹素与源图 2419/2419 完全一致。</p><p class="muted small">已知局限：编辑脚本编写时 Claude 没有看到 v6 的结果。压暗一档后外套最暗的两阶合并，阴影里的褶皱细节变少；描边是统一的近黑色，没有按光照方向留亮边；外套变暗后在肩部更接近头发暗部，在暗色勘察室里可能显得更重。衬衫、腿、围巾、皮肤、头发和靴子沿用 v5，马尾仍是最大的单一形状。在暖米色铺地上，外套与地面的对比仍然不够。</p><p class="muted small"><strong>状态：未批准。</strong>用户已查看 v6，回复“明亮场景对比度仍不足”：v6 未获美术批准，明亮场景（科技城、城外）的对比度仍需改进。QA 报告与 v6 清单（manifest）中的 human_reviewed: false 是生成时写入的记录：两者保留不改，不代表当前审阅状态。行走帧仍暂停：此前的实验性行走帧原型与已否定的四相试循环仍保留，静态门槛之后没有新做行走帧，没有任何行走动画获批准（动画验收为 0）。未接入可玩角色。探索精灵验收仍为 0/52，场景画质仍为 0/11，人工试玩记录仍为 0/2。</p><p class="muted small receipt-name">v6 源文件：${pilotDir}selout-v6-value-separation-candidate_m8-v06_20261015-010000-5a7d3f18.png</p><p class="muted small receipt-name">QA 报告：outputs/rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v6-visual-qa-report_m8-v06_20261015-003321-9bfd5b9e.json</p></section>`;
    // Selout v8 (2026-10-14): cloth/leather material split over v7 (v7 itself got a technical QA note only, no user verdict).
    // The user reviewed the bright city + bright outskirts captures and replied "够了，可作为静止帧基准": approved ONLY as the
    // female south idle static still-frame baseline at 48 logical px. No animation, other facing, runtime swap or counter change.
    const seloutV8Capture=(area,variant)=>`/assets/rpg-2-star-ocean-the-second_${area}_protagonist-female-south-idle-selout-${variant}-h48_m8-v08_20261015-022215-e2203167.png`;
    const seloutV8Areas=[
      ['city-bright','明亮科技城','用户审阅的截图'],
      ['outskirts-bright','明亮城外','用户审阅的截图'],
      ['survey-annex-room2-dark','暗色勘察附楼','同一次运行所拍，仅供参考，不在用户回复范围内'],
    ];
    const seloutV8Figure=([area,label,note])=>`<figure class="visual-sample idle-refine"><a href="${seloutV8Capture(area,'v8')}" target="_blank" rel="noopener"><img src="${seloutV8Capture(area,'v8')}" alt="${esc(label)} 1280×720 Godot 实机画面：女主南向待机 selout v8 静态基准帧" loading="lazy"></a><figcaption>${esc(label)} · ${esc(note)}。<a href="${seloutV8Capture(area,'v7-reference')}" target="_blank" rel="noopener">同场景 v7 对照</a></figcaption></figure>`;
    const seloutV8Card=`<section class="card" id="idle-selout-v8"><div class="step-top"><h3>女主南向静态待机 · selout v8 布料与皮革材质分离</h3>${badge('用户已批准 · 仅南向待机静态基准帧','good')}</div><p class="small">在 selout v7 上改动 793 个像素，只换颜色、不改形状和透明度：外套改为偏蓝的冷色石板灰（330，另手调 25），裤子改为深色冷调云杉灰（288），靴子保留暖色皮革、整体压低一档（143），腰间小罐并入相邻颜色（7）。32 色（已到上限），80×112 单帧，可见身体 43×96，不透明纹素 2419，按 48 逻辑像素显示。此前的 v7 在 v6 上改了 369 个像素（石板色外套），只有技术 QA，没有用户结论，未批准：Codex 目检认为外套色相变化不明显，下半身仍与暖色铺地融在一起。</p><div class="idle-v2-grid">${seloutV8Areas.map(seloutV8Figure).join('')}</div><p class="small">均为单独的 1280×720 Godot 画面，v7 对照为同一次运行、同一位置所拍；每个场景 v8 与 v7 相差 793 个窗口像素，v8 纹素与源图 2419/2419 完全一致。自动测量的外套、裤子、靴子与背景的色差在三个场景中都不低于 v7。</p><p class="muted small">已知局限（摘自 QA 说明）：人物整体比设定图偏冷，石板蓝外套不是设定图颜色，云杉灰裤子是设定图青灰色的加深版；裤子与青色披风色相接近；靴子的对比提升最少；小腿第 80–84 行仍有少量单像素交替；调色板已用满 32 色，之后若需新颜色须先合并一色。</p><p class="muted small"><strong>用户决定：</strong>用户查看了明亮科技城与明亮城外两张 1280×720 Godot 实机截图，回复“够了，可作为静止帧基准”。批准范围只有一项：女主南向待机这一张静态帧，作为 48 逻辑像素下的视觉基准。<strong>不批准：</strong>探索动画（静态门槛之后没有新做行走帧，此前的实验性行走帧原型与已否定的四相试循环仍未获批准，动画验收为 0）、北／东／西其他朝向、替换游戏内运行时精灵（v8 未接入可玩角色）、52 个变体中任何一个的探索精灵验收（仍为 0/52）、任何环境或场景画质闸门（v8 不计入场景画质；场景画质只由 2026-10-17 另行验收的三间室内环境计为 3/12）、人工计时试玩（仍为 0/2）。v8 清单与 QA 报告里的 art_approved: false、human_reviewed: false 是生成时写入的记录，早于用户回复，保留不改；决定另存于单独的决定记录。v1–v7 的历史结论不变，v6 仍是“明亮场景对比度仍不足”、未批准。</p><p class="muted small receipt-name">v8 源文件：${pilotDir}selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png（sha256 ccf9d2a293e7f1b9…）</p><p class="muted small receipt-name">v8 清单：${pilotDir}selout-v8-cloth-leather-manifest_m8-v08_20261015-021600-2d6c5eff.json</p><p class="muted small receipt-name">QA 报告：outputs/rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v8-visual-qa-report_m8-v08_20261015-022215-e2203167.json</p><p class="muted small receipt-name">QA 说明：docs/qa/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8_visual-qa-note_m8-v08_20261015-021600-c1694107.md</p><p class="muted small receipt-name">决定记录：docs/character-visuals/rpg-2-star-ocean-the-second_protagonist-female_south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md</p></section>`;
    // M2 global-travel gates, scoped approvals and pending decisions come from the progress state; none of them changes an acceptance counter.
    // "implemented" means code plus passing automated tests, never final acceptance; user decisions get a neutral badge, not a warning.
    const gateStatus={done:['已完成 / Done','good'],implemented:['已实现 · 自动测试通过 / Implemented, tests pass','good'],in_progress:['进行中 / In progress','accent'],awaiting_decision:['待用户决定 / Awaiting user decision','accent'],estimate_only:['仅初步估算 / Preliminary estimate','warn'],research_only:['仅研究资料 / Research only','warn'],decided_runtime_pending:['已决定 · 运行时未迁移 / Decided, runtime not migrated','accent'],no_evidence:['未见证据 / No evidence yet','warn'],not_started:['未开始 / Not started','warn'],human_pending:['待人工审阅 / Awaiting human review','warn'],blocked:['待决定 / Awaiting decision','warn']};
    const approvalStatus={approved:['已批准（限定范围）/ Approved, scoped','good'],direction_accepted:['方向已接受 / Direction accepted','accent'],not_accepted:['未接受 / Not accepted','warn'],unapproved_concept:['未批准概念 / Unapproved concept','warn']};
    const decisionKind={blocked:['受阻 · 待决定 / Blocked','warn'],candidate:['候选 · 待审 / Candidate','accent']};
    // Evidence stays one click away but collapsed: a short human label per file, the raw repo path only inside the disclosure.
    // Only plain docs/ or outputs/ paths become links (served read-only by /evidence); anything else shows a safe fallback.
    const evidenceKinds=[['docs/design/','设计文档 / Design doc'],['docs/qa/','QA 记录 / QA note'],['docs/character-visuals/','角色决定 / Character decision'],['outputs/','产出文件 / Output']];
    const safeEvidencePath=file=>typeof file==='string'&&file.length<=300&&/^(docs|outputs)\/[A-Za-z0-9._\/-]+\.(md|png|json)$/.test(file)&&!file.includes('..')&&!file.includes('//');
    const evidenceTitle=file=>{const base=file.split('/').pop().replace(/\.(md|png|json)$/,'').replace(/^rpg-2-star-ocean-the-second_/,'').replace(/_\d{8}-\d{6}-[0-9a-f]{8}$/,'');return base.split('_').slice(0,2).join(' · ').replace(/-/g,' ')||base;};
    const evidenceItem=file=>{
      if(!safeEvidencePath(file))return `<li class="source-missing">来源路径无效或缺失 / Source path unavailable</li>`;
      const kind=(evidenceKinds.find(([prefix])=>file.startsWith(prefix))||['','来源 / Source'])[1]+(file.endsWith('.png')?' · 图片 / Image':'');
      return `<li><a href="/evidence?path=${encodeURIComponent(file)}" target="_blank" rel="noopener">${esc(evidenceTitle(file))}</a><span class="muted"> · ${esc(kind)}</span><code class="source-path">${esc(file)}</code></li>`;
    };
    const evidenceLine=list=>Array.isArray(list)&&list.length?`<details class="sources"><summary>查看来源 / View source（${list.length}）</summary><ul>${list.map(evidenceItem).join('')}</ul></details>`:'<div class="muted small sources-none">暂无来源 / No source yet</div>';
    const m2x=p.m2Expansion, ledger=p.approvalLedger, ledgerCounts=ledger?.counters;
    const m2GateRow=g=>{const [label,kind]=gateStatus[g.status]||[g.status,'warn'];return `<li class="m2-gate" data-gate="${esc(g.id)}"><div class="m2-gate-head"><span><strong>${esc(g.zh)}</strong> <span class="muted small">${esc(g.en)}</span></span>${badge(label,kind)}</div><div class="small">${esc(g.detail)}</div><div class="m2-gate-foot"><span class="muted small">负责 / Owner：${esc(g.owner)}</span>${evidenceLine(g.evidence)}</div></li>`;};
    // Implemented (or done) gates first, then everything still open, so the card reads "what works" vs "what is left".
    const m2Built=m2x?m2x.gates.filter(g=>g.status==='implemented'||g.status==='done'):[], m2Open=m2x?m2x.gates.filter(g=>!m2Built.includes(g)):[];
    const m2GateList=(title,list)=>list.length?`<p class="small m2-gate-group"><strong>${title}（${list.length}）</strong></p><ol class="m2-gates" aria-label="关卡 / Gate · 状态 / Status">${list.map(m2GateRow).join('')}</ol>`:'';
    const m2GatesCard=m2x?`<section class="card" id="m2-global-travel-gates"><div class="step-top"><h3>M2 全球旅行 · 实施关卡 / Global travel gates</h3>${badge(m2Built.length+' / '+m2x.gates.length+' 已实现 · M2 未完成 / Not complete','warn')}</div><p class="small">首城锚点 / Anchor：<strong>${esc(m2x.anchor.zh)}</strong> · ${esc(m2x.anchor.en)}。${esc(m2x.anchor.note)}</p><p class="muted small">“已实现”指代码和 Godot 自动测试已通过，不等于验收。“待用户决定”是设计选择，不是程序缺陷。旧三点 M2_SMOKE_OK 不计入新规则。</p>${m2GateList('已实现 / Implemented',m2Built)}${m2GateList('仍未完成 / Still open',m2Open)}<p class="muted small">${safeEvidencePath(m2x.researchPacket)?`<a href="/evidence?path=${encodeURIComponent(m2x.researchPacket)}" target="_blank" rel="noopener" title="${esc(m2x.researchPacket)}">查看当前美国路线来源 / View current US route sources</a> · `:''}<a href="/source/shanghai-liangzhu" target="_blank" rel="noopener">归档：已取代的上海／良渚路线研究 / Archive: superseded Shanghai-Liangzhu route research</a></p></section>`:'';
    const approvalCard=ledger?`<section class="card" id="approval-ledger"><div class="step-top"><h3>批准范围与验收数 / Approval scope & counters</h3>${badge('验收数只计已验收台账条目 · Counts only accepted ledger items','warn')}</div><p class="small"><strong>探索精灵 / Runtime sprites ${ledgerCounts.runtimeSpritesAccepted} / ${ledgerCounts.runtimeSpritesTarget}</strong> · <strong>科技区场景画质 / Science scene visuals ${ledgerCounts.sceneVisualsAccepted} / ${ledgerCounts.sceneVisualsTarget}</strong> · <strong>人工计时试玩 / Human playtests ${ledgerCounts.humanPlaytests} / ${ledgerCounts.humanPlaytestsTarget}</strong> · 角色 ${ledgerCounts.identities} 位 / ${ledgerCounts.visualVariants} 个视觉版本 (identities / variants)</p><p class="muted small">方向被接受不等于资产验收；下列每项只在注明的范围内有效。Direction acceptance is not asset acceptance.</p><ul>${ledger.items.map(item=>{const [label,kind]=approvalStatus[item.status]||[item.status,'warn'];return `<li data-approval="${esc(item.id)}">${badge(label,kind)} <strong>${esc(item.zh)}</strong> <span class="muted small">${esc(item.en)}</span><div class="small">${esc(item.scope)}</div>${evidenceLine(item.evidence)}</li>`;}).join('')}</ul></section>`:'';
    const decisionsCard=p.decisions?.length?`<section class="card" id="pending-decisions"><div class="step-top"><h3>候选与受阻决定 / Candidate & blocked decisions</h3>${badge(p.decisions.length+' 项待决定 · pending','warn')}</div><ul>${p.decisions.map(d=>{const [label,kind]=decisionKind[d.kind]||[d.kind,'warn'];return `<li data-decision="${esc(d.id)}">${badge(label,kind)} <strong>${esc(d.zh)}</strong> <span class="muted small">${esc(d.en)}</span><div class="small">${esc(d.detail)}</div><div class="muted small">等待 / Awaiting：${esc(d.awaiting)}</div></li>`;}).join('')}</ul></section>`:'';
    content.innerHTML=`${head('制作路线','新版 MVP：完整角色视觉身份与精致科技区场景',badge(done+' / '+p.steps.length+' 阶段','accent'))}
      ${productionPanel(state.production)}
      <div class="card"><div class="step-top"><strong>已完成阶段</strong><span>${done} / ${p.steps.length}</span></div><div class="meter" role="progressbar" aria-valuemin="0" aria-valuemax="${p.steps.length}" aria-valuenow="${done}"><span style="width:${pct}%"></span></div><p class="muted small">当前重点：${current?esc(current.id+' · '+copy[current.id][0]):'全部阶段已完成'}。阶段数量不代表剩余工作量。</p></div>
      <div class="section-label">全球地图与旅行 · 新规则</div>
      <section class="card" id="global-map-travel-rule"><div class="step-top"><h3>真实地名与汽车／飞机旅行</h3>${badge('规则已定 · 地图与旅时核心已实现 · M2 未完成','warn')}</div><p>地球地图覆盖全球；城市使用现实城市名称，遗迹使用现实存在的著名遗址或景点名称。队伍在地图上乘汽车或飞机，每段按固定整点旅时结算（现实城市间典型旅时取整到小时，至少 1 小时），不按出发时刻、机场或值机分项计算；进入场景后主角步行。终局星球仍经传送门抵达。</p><p class="small">旅时推进日历，玩家只看到年月日、不显示钟点；连续不足一天的行程会累计；每周商会结算共用同一时间轴：暂定商会账目已接入日历并通过 Godot 自动测试；工程候选（未验收）中，伙伴可在 10 级职业选择时转为行商（只做两阶 MVP，完整 20 系列 × 5 阶职业设定留待以后），并在已发现的城市从世界地图「商会」派驻经营。行商职业技能在战斗中都不可用；一阶补给协议仍是占位，不能花 JP；二阶公平报价是暂定的经营被动，可花 JP 升级，每级为伙伴驻守满周的收益加基础收益的 5 %，NPC 经营周不加成（派驻或重新派驻后的未满一周按普通 NPC 80 % 结算，商会面板会单独注明）；账目点数不是货币，没有平衡、劫匪事件或价格影响。游戏内已换成真实地球全图与美国东北部、五大湖地区图，出发按路线的整点旅时推进日历（纽约⇄扬克斯 1 小时，纽约／扬克斯⇄华盛顿 5 小时，纽约⇄芝加哥 6 小时），并通过 Godot 自动测试。创作者 2026-10-15 的决定已在运行时实现为技术候选：新游戏从纽约（曼哈顿下城市政厅公园）开始，日期 2537-05-25，可到扬克斯城外与华盛顿国会大厦废墟，纽约—芝加哥航线到达卢普区技术占位街区；卡茨基尔山附近的地下社区尚无运行时地点。整点旅时已实现；其参考里程与分钟仍是初步估算，只作取整依据；场景与地图美术未制作或未验收，人工审阅未完成。场景与角色美术验收数不因此变化。</p><p class="muted small"><a href="/source/earth-rules" target="_blank" rel="noopener" title="docs/design/rpg-2-star-ocean-the-second_global-earth-map-real-place-travel_rules-v01_20261014-235354-2b5d4d98.md">查看规则与验收 / View rules &amp; acceptance</a></p></section>
      ${m2GatesCard}
      ${approvalCard}
      ${decisionsCard}
      ${reviewQueueCard?`<div class="section-label">跨设备视觉审查队列（未批准候选 · 不改变验收数）</div>${reviewQueueCard}`:''}
      <div class="section-label">新版画面验收</div>
      <section class="card"><h3>51 位角色 · 科技区完成画面</h3><p>目标是主角男女两版与 50 位伙伴都有游戏内展示图及四方向探索精灵；试玩仍只开放科技区角色。场景画质以《逸剑风云决》为参考，验收科技区自己的完成画面。</p><p class="small">来源设定图 ${checked(portraits)} / ${portraits.length} 已验收 · 游戏内展示图 ${checked(displays)} / ${displays.length} · 探索精灵 ${checked(sprites)} / ${sprites.length} · 场景画质 ${checked(scenes)} / ${scenes.length}</p><p class="small">功能占位：${characterReview.nativeWalkCharactersAuthored||0} 套旧 32×48 四向探索动作（画质基线已否定） · ${characterReview.nativeRecruitNpcDisplaysIntegrated||0} 位科技区伙伴已作为 NPC 显示 · ${characterReview.sideviewCombatSetsIntegrated||0} 套横向战斗原型已接入、均未获美术批准 · 地图 ${environmentReview.mapCandidatesIntegrated||0}、户外 ${environmentReview.outdoorCandidatesIntegrated||0}、勘察室 ${environmentReview.surveyRoomCandidatesIntegrated||0} 张背景候选已接入。</p><p class="muted small">用户已批准三人同城展示采用 48 逻辑像素比例；这只批准显示比例，探索精灵仍是 0/52 验收。男女主和梁序各有南／东／北三张高精度静态候选（共九张），均未接入可玩角色或获美术批准。梁序东向躯干、北向头部与低透明度边缘仍待修正；女主四相试循环出现围巾尾与护膝跳边，动画验收受阻。女主南向静态待机的 Box 与 Lanczos 两张量化候选均已被用户否定（打磨不足），基线选择为“两者都不用”；此后经 selout v1–v8 逐版静态精修，用户已批准 selout v8 作为女主南向待机静态帧基准（只批准这一张静态帧，48 逻辑像素）；静态门槛之后尚未新做行走帧，其他朝向、动画与运行时替换均未批准。1280×720 画布点击与键盘交互回归已通过，英文地图说明与存档按钮重叠已修复。独立审查画廊可查看 ${characterReview.sourceGalleryImagesLoaded||0} 张来源设定图（9 张已批准、43 张概念稿）；画廊不计作游戏内展示图或精灵验收。M7 人工试玩仍待完成。</p>${citySample?.file?`<figure class="visual-sample"><a href="${esc(citySample.file)}" target="_blank" rel="noopener"><img src="${esc(citySample.file)}" alt="科技城市与主角、梁序的 Godot 实际画面样板" loading="lazy"></a><figcaption>Godot 可玩科技城候选画面；仍待视觉与操作验收。</figcaption></figure>`:''}<p class="muted small">候选图与动作原型不计为已验收完成画面。各项仍按资产清单单独验收。</p><button type="button" class="chip" id="open-visual-assets">查看视觉资产清单</button></section>
      <div class="section-label">女主南向静态待机 · 两张新候选待审阅</div>
      <p class="muted small">此前 Box 与 Lanczos 两张量化候选已被用户否定。以下两张为新的静态候选，各自独立审阅；不代表批准。</p>
      ${idleRefineCandidates.map(idleRefineCard).join('')}
      <div class="section-label">女主南向静态待机 · selout v2 精修待审阅</div>
      <p class="muted small">用户在上面两张中选了 selout v1，认为它更接近目标；v1 本身未获批准。下面是在 v1 基础上的 v2 静态精修，单独审阅。之后的 v3（只改 91 个像素）经内部复核：技术上无误，但与 v2 几乎看不出差别，外套躯干仍显杂乱；v3 未批准，不作为审阅选项。结构性更大的静态 v4 见下方单独卡片。</p>
      ${seloutV2Card}
      <div class="section-label">女主南向静态待机 · selout v4 结构性技术候选</div>
      <p class="muted small">以下只记录 v4 的技术结果与实机截图，与上方的美术审阅卡片分开；它不是已批准的版本，也不计入任何验收。</p>
      ${seloutV4Card}
      <div class="section-label">女主南向静态待机 · selout v5 下半身与马尾技术候选</div>
      <p class="muted small">以下只记录 v5 的技术结果与实机截图，与上方的美术审阅卡片分开；用户已审阅并回复“更接近了，继续精修”，它不是已批准的版本，也不计入任何验收。</p>
      ${seloutV5Card}
      <div class="section-label">女主南向静态待机 · selout v6 明度与轮廓分离技术候选</div>
      <p class="muted small">以下只记录 v6 的技术结果与实机截图，与上方的美术审阅卡片分开；用户已审阅并回复“明亮场景对比度仍不足”，它不是已批准的版本，也不计入任何验收。</p>
      ${seloutV6Card}
      <div class="section-label">女主南向静态待机 · selout v8 静态基准帧（用户已批准）</div>
      <p class="muted small">v7（石板色外套）只有技术 QA、未获批准，未单独成卡，见下方 v8 卡片中的说明与同场景 v7 对照。v8 经用户批准作为南向待机静态帧基准；这只批准一张静态帧，不计入任何验收数。</p>
      ${seloutV8Card}
      ${readinessSection()}
      <div class="section-label">分步实施</div>
      <div class="stack">${p.steps.map(step=>`<details class="group"><summary>${esc(step.id+' · '+copy[step.id][0])} <span class="group-count">${esc(status[step.status]||step.status)}</span></summary><div class="card"><p>${esc(copy[step.id][1])}</p><strong>验收标准</strong><p>${esc(copy[step.id][2])}</p>${step.details?.length?'<strong>当前内容</strong><ul>'+step.details.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>':''}${step.remaining?.length?'<strong>尚需完成</strong><ul>'+step.remaining.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>':''}${step.evidence?.length?'<strong>已有依据</strong><ul>'+step.evidence.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>':''}</div></details>`).join('')}</div>
      <div class="section-label">M7 试玩记录</div>
      <section class="card"><div class="step-top"><h3>本地汇报记录</h3><button type="button" class="chip" id="refresh-playtests">刷新记录</button></div><div class="playtest-launch"><button type="button" class="chip" id="start-playtest" ${launchDisabled?'disabled':''}>${launchPhase==='running'?'试玩进行中':'开始新档试玩'}</button><span class="muted small" role="status">${launchHint}</span></div><p class="muted small">目前这份游戏可用于 M7 内容试玩，画面仍是原型；最终 MVP 要在 M8 美术完成后再进行 M9 整体验收。两条不同首访顺序、25–35 分钟、三处勘察和三位伙伴的内容记录：${Math.min(2,routeTrials.size)}/2。</p><details class="group"><summary>两轮试玩指引</summary><div class="card small"><p><strong>第一轮：</strong>城市 → 城外 → 遗址。<strong>第二轮：</strong>遗址 → 城外 → 城市。每轮都从主菜单开始新游戏，三位伙伴可暂缓邀请，但在回城汇报前请招募齐。</p><ol><li>各地查看六条线索、完成三组证据关联与最终研判。</li><li>检查城外中继和遗址记录；绕过或击败一台机械。两处现场痕迹和伙伴协助是可选内容。</li><li>回城市提交汇报。出现完成画面后关闭游戏，等待记录回传。</li></ol><p>试玩时留意迷路、操作不明、文字溢出、战斗难度和想继续探索的动力；这些体验无法由自动记录判断。</p></div></details><div class="stack">${playtestRows||'<div class="empty">尚无正式试玩记录。M7 仍需两次不同顺序的实际计时试玩。</div>'}</div></section>
      <details class="group" id="playtest-feedback" ${state.feedbackOpen?'open':''}><summary>试玩感受记录</summary><div class="card"><p class="muted small">试玩时随手记下观察；输入后自动保存在当前浏览器。完成后请把反馈发到聊天里，以便纳入项目验收。</p>${feedbackFields}<p class="muted small" role="status" id="feedback-status">等待输入</p></div></details>
      <div class="section-label">仍待确定</div>
      <div class="stack">${state.bible.openQuestions.map(q=>`<div class="card"><h3>${esc(q.title)}</h3><p>${esc(q.detail)}</p></div>`).join('')}</div>
      <div class="card"><button type="button" class="chip" id="open-job-proposal">查看 20 系列五阶职业（名称已批准）</button></div>
      <div class="section-label">设计稿中的实施顺序与待细化清单</div>
      <div class="stack">${state.bible.chapters.filter(c=>[8,9].includes(c.number)).map(c=>`<details class="group" data-production-chapter="${c.id}"><summary>${esc(c.title)}</summary><div class="document">${markdown(c.body)}${sourceLine(c.source)}</div></details>`).join('')}</div>
      <div class="section-label">计划与完整实施顺序</div>
      <div class="card"><a href="/source/mvp" target="_blank" rel="noopener">打开 MVP 实施计划</a> · <a href="/source/brief" target="_blank" rel="noopener">打开完整设计稿</a></div>`;
    const currentCityCaption=content.querySelector('.visual-sample:not(.idle-refine) figcaption');
    if(currentCityCaption)currentCityCaption.textContent='Godot 可玩科技城 · 当前旧 32×48 角色帧仅作功能占位，已被否定为完成画质基线。';
    const visualCard=content.querySelector('.visual-sample:not(.idle-refine)')?.parentElement;
    if(visualCard){
      for(const sample of state.bible.characterVisualReview?.previews||[]){
        if(sample.file===citySample?.file)continue;
        const figure=document.createElement('figure');figure.className='visual-sample';
        const link=document.createElement('a');link.href=sample.file;link.target='_blank';link.rel='noopener';
        const img=document.createElement('img');img.src=sample.file;img.alt=sample.label+' 的角色画质审查样板';img.loading='lazy';
        const caption=document.createElement('figcaption');caption.textContent=sample.label+' · '+sample.caption;
        link.append(img);figure.append(link,caption);visualCard.append(figure);
      }
    }
    content.querySelector('#refresh-playtests').addEventListener('click',()=>refreshPlaytests().catch(()=>{document.getElementById('footer-status').textContent='试玩记录暂时无法读取';}));
    content.querySelector('#open-visual-assets').addEventListener('click',()=>{state.assetScope='mvp';state.openGroups.add('characters');state.openGroups.add('world');state.openGroups.delete('characters.runtime-displays');state.openGroups.delete('world.scene-quality');navigate('assets');});
    content.querySelector('#start-playtest').addEventListener('click',startPlaytest);
    content.querySelector('#readiness-filter')?.addEventListener('change',event=>{state.readinessFilter=event.target.value;render();});
    content.querySelectorAll('[data-readiness-open]').forEach(el=>el.addEventListener('toggle',()=>el.open?state.openGroups.add(el.dataset.readinessOpen):state.openGroups.delete(el.dataset.readinessOpen)));
    if(state.readinessStatus==='idle'){state.readinessStatus='loading';refreshReadiness();}
    content.querySelector('#open-job-proposal').addEventListener('click',()=>navigate('rules',{chapter:'chapter-4'}));
    content.querySelector('#playtest-feedback').addEventListener('toggle',event=>{state.feedbackOpen=event.target.open;});
    content.querySelectorAll('[data-feedback]').forEach(field=>field.addEventListener('input',()=>{
      const message=content.querySelector('#feedback-status');
      try { localStorage.setItem(feedbackKey(field.dataset.feedback),field.value);message.textContent='已保存在当前浏览器'; }
      catch (_) { message.textContent='此浏览器无法保存，请复制笔记到聊天'; }
    }));
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
          meta.textContent=(item.scope==='MVP'?'MVP':'完整游戏')+' · '+(assetStages[item.stage]||item.stage)+(item.target>1?' · 目标 '+item.target+' 份':'')+(item.board?' · '+item.board:'');
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
  async function refreshProduction(){
    const response=await fetch('/production',{cache:'no-store'});if(!response.ok)throw new Error('Production ledger unavailable');
    const ledger=await response.json();
    if(state.production?.updatedAt!==ledger.updatedAt||JSON.stringify(state.production?.computed)!==JSON.stringify(ledger.computed)){state.production=ledger;if(state.view==='production'&&!state.query)render();}
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
  document.addEventListener('visibilitychange',()=>{if(!document.hidden){refreshInventory().catch(()=>{});refreshProgress().catch(()=>{});refreshPlaytests().catch(()=>{});refreshPlaytestStatus().catch(()=>{});if(state.readinessStatus!=='idle')refreshReadiness();}});
  setInterval(()=>{if(!document.hidden){refreshProgress().catch(()=>{});refreshProduction().catch(()=>{});refreshInventory().catch(()=>{});refreshPlaytests().catch(()=>{});refreshPlaytestStatus().catch(()=>{});}},10000);
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
    refreshProduction().catch(()=>{});
    refreshPlaytests().catch(()=>{});
    refreshPlaytestStatus().catch(()=>{});
  }).catch(()=>{content.innerHTML='<div class="empty">游戏圣经暂时无法读取。请确认本地项目面板已启动。</div>';});
})();
