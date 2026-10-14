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
    const jobs=state.bible.jobProposal;
    const jobProposal=selected.number===4&&jobs ? `<div class="section-label">20 系列 × 5 阶 · 待确认提案</div><div class="card small"><strong>设计边界</strong><ul>${jobs.rules.map(rule=>`<li>${esc(rule)}</li>`).join('')}</ul></div>${['武艺','应变','研学','灵觉'].map(aptitude=>`<details class="group"><summary>${aptitude} · 5 个系列</summary><div class="card">${jobs.series.filter(series=>series.aptitude===aptitude).map(series=>`<details class="subgroup"><summary>${esc(series.name)} <span class="group-count">${esc(series.en)}</span></summary><div class="card small"><p><strong>定位：</strong>${esc(series.role)}</p><p><strong>五阶：</strong>${series.stages.map((name,index)=>`${index+1}. ${esc(name)}`).join(' → ')}</p><p><strong>终阶解锁：</strong>${esc(series.finalQuest)}</p></div></details>`).join('')}</div></details>`).join('')}<p class="muted small">五阶名称、终阶任务与技能效果均为待确认提案；正式数值待战斗平衡后确定。</p>`:'';
    const skillTrees=state.bible.skillTreeProposal;
    const skillTreeProposal=selected.number===4&&skillTrees ? `<div class="section-label">职业技能树提案 · ${skillTrees.trees.length} / 20 系列</div><div class="card small"><p>第 2、4 阶各有两条并列技能，两条都能学会。技能满级 3 级，达到对应角色等级和职业阶级后获得 1 级；2、3 级消耗 JP。</p><p>${esc(skillTrees.progression.aptitudeDiscount)} 当前数值为提案，战斗平衡后再定。</p></div>${skillTrees.trees.map(tree=>`<details class="group"><summary>${esc(tree.name)} · 7 个技能节点</summary><div class="card">${tree.nodes.map(node=>`<div class="skill-node"><strong>第 ${node.tier} 阶${node.branch?' · '+esc(node.branch):''}：${esc(node.name)}</strong><span class="muted small">${esc(node.type)}${node.type==='主动'?' · '+node.energy+' 能量':''} · ${esc(node.tags.join(' / '))}</span><p class="small">${esc(node.effect)}</p></div>`).join('')}</div></details>`).join('')}<p class="muted small">${skillTrees.trees.length===20?'20 条职业技能树均有提案；主角与 15 位主线伙伴的个人树见人物档案，其余 35 位伙伴及平衡数值仍待设计。':`其余 ${20-skillTrees.trees.length} 条职业技能树仍待设计。`}</p>`:'';
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
    const groups=['全部来源','主角','主线伙伴','支线伙伴','情境招募伙伴'];
    const visible=b.characters.filter(c=>(state.board==='全部板块'||c.board===state.board)&&(state.group==='全部来源'||c.group===state.group));
    const selected=visible.find(c=>c.id===state.character)||visible[0];
    if(selected)state.character=selected.id;
    const personal=selected&&b.personalSkillTrees?.trees.find(tree=>tree.characterId===selected.id);
    const personalHtml=personal?`<div class="section-label">个人专属技能树 · 待确认提案</div><div class="card small"><strong>${esc(personal.skill)}</strong><p>与当前职业无关；角色达到对应等级时获得节点 1 级，节点 2、3 级使用 JP 提升。新加入伙伴按同步等级开放节点。</p><p>${esc(b.personalSkillTrees.progression.aptitude)}</p></div><details class="group"><summary>${esc(personal.name)} · 5 个成长节点</summary><div class="card">${personal.nodes.map(node=>`<div class="skill-node"><strong>角色 ${node.level} 级：${esc(node.name)}</strong><span class="muted small">${esc(node.mode)}${node.energy?' · '+node.energy+' 能量':''}${node.tags?' · '+esc(node.tags.join(' / ')):''}</span><p class="small">${esc(node.effect)}</p></div>`).join('')}</div></details>`:'';
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
            ${gate('G2 探索动画',rt(walk.status),`${walk.placeholder_idle_frames||walk.placeholder_walk_frames?`占位 待机 ${esc(walk.placeholder_idle_frames||0)} + 行走 ${esc(walk.placeholder_walk_frames||0)} · `:''}正式帧数${walk.frame_counts_user_approved===true?'已获用户批准':'未批准'}`)}
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
      M2:['世界地图与探索','开放三个目的地，加入俯视移动、NPC 与可绕开的可见敌人。','不用开发工具即可往返三个地点，并绕开至少一场普通战斗。'],
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
    const checked=items=>items.filter(item=>item.checked).length;
    const pct=Math.round(100*done/p.steps.length);
    // Female south idle refinement candidates (2026-10-14): static frames awaiting the user's review, not approved.
    const idleRefineCapture=(area,variant)=>`/assets/rpg-2-star-ocean-the-second_${area}_protagonist-female-south-idle-refine-${variant}-candidate-h48_m8-v01_20261014-231811-850083fd.png`;
    const idleRefineCandidates=[
      ['inkline','描线版 inkline','全轮廓近黑描线，41 色；睫毛带外挑，2 像素嘴。','fb830d80'],
      ['selout','选择性描线版 selout','轮廓按各材质取最深色，26 色；无外挑睫毛，带腮红像素。','4d141ad5'],
    ];
    const idleRefineCard=([variant,title,note,hash])=>`<section class="card" id="idle-refine-${variant}"><div class="step-top"><h3>女主南向静态待机 · ${esc(title)}</h3>${badge('待用户审阅 · 未批准','warn')}</div><p class="small">${esc(note)} 80×112 单帧，可见身体 43×96，按 48 逻辑像素显示。</p><figure class="visual-sample idle-refine"><a href="${idleRefineCapture('city',variant)}" target="_blank" rel="noopener"><img src="${idleRefineCapture('city',variant)}" alt="科技城 1280×720 Godot 实机画面：女主南向待机 ${esc(variant)} 候选与 32×48 占位并排" loading="lazy"></a><figcaption>科技城 1280×720 实机画面，左侧为旧 32×48 占位。点击打开原尺寸。</figcaption></figure><p class="small">其他 1280×720 实机画面：<a href="${idleRefineCapture('outskirts-bright',variant)}" target="_blank" rel="noopener">明亮城外</a> · <a href="${idleRefineCapture('prototype-room-dark',variant)}" target="_blank" rel="noopener">暗色原型室</a></p><p class="muted small">先定静态帧，行走帧暂停，尚未开始任何行走帧。未接入可玩角色。探索精灵验收仍为 0/52，场景画质仍为 0/11。自动 QA 只做测量，未经人工审阅。</p><p class="muted small receipt-name">源文件：game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-refine-${variant}-candidate_m8-v01_20261014-231100-${hash}.png</p></section>`;
    content.innerHTML=`${head('制作路线','新版 MVP：完整角色视觉身份与精致科技区场景',badge(done+' / '+p.steps.length+' 阶段','accent'))}
      <div class="card"><div class="step-top"><strong>已完成阶段</strong><span>${done} / ${p.steps.length}</span></div><div class="meter" role="progressbar" aria-valuemin="0" aria-valuemax="${p.steps.length}" aria-valuenow="${done}"><span style="width:${pct}%"></span></div><p class="muted small">当前重点：${current?esc(current.id+' · '+copy[current.id][0]):'全部阶段已完成'}。阶段数量不代表剩余工作量。</p></div>
      <div class="section-label">新版画面验收</div>
      <section class="card"><h3>51 位角色 · 科技区完成画面</h3><p>目标是主角男女两版与 50 位伙伴都有游戏内展示图及四方向探索精灵；试玩仍只开放科技区角色。场景画质以《逸剑风云决》为参考，验收科技区自己的完成画面。</p><p class="small">来源设定图 ${checked(portraits)} / ${portraits.length} 已验收 · 游戏内展示图 ${checked(displays)} / ${displays.length} · 探索精灵 ${checked(sprites)} / ${sprites.length} · 场景画质 ${checked(scenes)} / ${scenes.length}</p><p class="small">功能占位：${characterReview.nativeWalkCharactersAuthored||0} 套旧 32×48 四向探索动作（画质基线已否定） · ${characterReview.nativeRecruitNpcDisplaysIntegrated||0} 位科技区伙伴已作为 NPC 显示 · ${characterReview.sideviewCombatSetsIntegrated||0} 套横向战斗原型已接入、均未获美术批准 · 地图 ${environmentReview.mapCandidatesIntegrated||0}、户外 ${environmentReview.outdoorCandidatesIntegrated||0}、勘察室 ${environmentReview.surveyRoomCandidatesIntegrated||0} 张背景候选已接入。</p><p class="muted small">用户已批准三人同城展示采用 48 逻辑像素比例；这只批准显示比例，探索精灵仍是 0/52 验收。男女主和梁序各有南／东／北三张高精度静态候选（共九张），均未接入可玩角色或获美术批准。梁序东向躯干、北向头部与低透明度边缘仍待修正；女主四相试循环出现围巾尾与护膝跳边，动画验收受阻。女主南向静态待机的 Box 与 Lanczos 两张量化候选均已被用户否定（打磨不足），基线选择为“两者都不用”；当前先继续精修静态待机帧，行走帧制作暂停，待新的静态待机获用户批准后再开始。1280×720 画布点击与键盘交互回归已通过，英文地图说明与存档按钮重叠已修复。独立审查画廊可查看 ${characterReview.sourceGalleryImagesLoaded||0} 张来源设定图（9 张已批准、43 张概念稿）；画廊不计作游戏内展示图或精灵验收。M7 人工试玩仍待完成。</p>${citySample?.file?`<figure class="visual-sample"><a href="${esc(citySample.file)}" target="_blank" rel="noopener"><img src="${esc(citySample.file)}" alt="科技城市与主角、梁序的 Godot 实际画面样板" loading="lazy"></a><figcaption>Godot 可玩科技城候选画面；仍待视觉与操作验收。</figcaption></figure>`:''}<p class="muted small">候选图与动作原型不计为已验收完成画面。各项仍按资产清单单独验收。</p><button type="button" class="chip" id="open-visual-assets">查看视觉资产清单</button></section>
      <div class="section-label">女主南向静态待机 · 两张新候选待审阅</div>
      <p class="muted small">此前 Box 与 Lanczos 两张量化候选已被用户否定。以下两张为新的静态候选，各自独立审阅；不代表批准。</p>
      ${idleRefineCandidates.map(idleRefineCard).join('')}
      ${readinessSection()}
      <div class="section-label">分步实施</div>
      <div class="stack">${p.steps.map(step=>`<details class="group"><summary>${esc(step.id+' · '+copy[step.id][0])} <span class="group-count">${esc(status[step.status]||step.status)}</span></summary><div class="card"><p>${esc(copy[step.id][1])}</p><strong>验收标准</strong><p>${esc(copy[step.id][2])}</p>${step.details?.length?'<strong>当前内容</strong><ul>'+step.details.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>':''}${step.remaining?.length?'<strong>尚需完成</strong><ul>'+step.remaining.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>':''}${step.evidence?.length?'<strong>已有依据</strong><ul>'+step.evidence.map(x=>'<li>'+esc(x)+'</li>').join('')+'</ul>':''}</div></details>`).join('')}</div>
      <div class="section-label">M7 试玩记录</div>
      <section class="card"><div class="step-top"><h3>本地汇报记录</h3><button type="button" class="chip" id="refresh-playtests">刷新记录</button></div><div class="playtest-launch"><button type="button" class="chip" id="start-playtest" ${launchDisabled?'disabled':''}>${launchPhase==='running'?'试玩进行中':'开始新档试玩'}</button><span class="muted small" role="status">${launchHint}</span></div><p class="muted small">目前这份游戏可用于 M7 内容试玩，画面仍是原型；最终 MVP 要在 M8 美术完成后再进行 M9 整体验收。两条不同首访顺序、25–35 分钟、三处勘察和三位伙伴的内容记录：${Math.min(2,routeTrials.size)}/2。</p><details class="group"><summary>两轮试玩指引</summary><div class="card small"><p><strong>第一轮：</strong>城市 → 城外 → 遗址。<strong>第二轮：</strong>遗址 → 城外 → 城市。每轮都从主菜单开始新游戏，三位伙伴可暂缓邀请，但在回城汇报前请招募齐。</p><ol><li>各地查看六条线索、完成三组证据关联与最终研判。</li><li>检查城外中继和遗址记录；绕过或击败一台机械。两处现场痕迹和伙伴协助是可选内容。</li><li>回城市提交汇报。出现完成画面后关闭游戏，等待记录回传。</li></ol><p>试玩时留意迷路、操作不明、文字溢出、战斗难度和想继续探索的动力；这些体验无法由自动记录判断。</p></div></details><div class="stack">${playtestRows||'<div class="empty">尚无正式试玩记录。M7 仍需两次不同顺序的实际计时试玩。</div>'}</div></section>
      <details class="group" id="playtest-feedback" ${state.feedbackOpen?'open':''}><summary>试玩感受记录</summary><div class="card"><p class="muted small">试玩时随手记下观察；输入后自动保存在当前浏览器。完成后请把反馈发到聊天里，以便纳入项目验收。</p>${feedbackFields}<p class="muted small" role="status" id="feedback-status">等待输入</p></div></details>
      <div class="section-label">仍待确定</div>
      <div class="stack">${state.bible.openQuestions.map(q=>`<div class="card"><h3>${esc(q.title)}</h3><p>${esc(q.detail)}</p></div>`).join('')}</div>
      <div class="card"><button type="button" class="chip" id="open-job-proposal">查看 20 系列五阶职业提案</button></div>
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
