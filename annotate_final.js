
<script>
// ===== 版本条 =====
const VERSIONS=[{v:1,date:"2026-09-28",desc:"首版:lesson4最终判定(该等6道/不该等9道)+建议等待秒数+模糊带语义判定表+118题受阻说明"}];
(function(){
  const badge=document.getElementById('verBadge'),panel=document.getElementById('verPanel');
  badge.textContent='版本 v'+VERSIONS[VERSIONS.length-1].v;
  panel.innerHTML='<h4>版本历史</h4>'+[...VERSIONS].reverse().map(x=>
    `<div class="vitem"><b>v${x.v}</b><span class="d">${x.date}</span><p>${x.desc}</p></div>`).join('');
  badge.onclick=()=>panel.style.display=panel.style.display==='block'?'none':'block';
})();

// ===== 批注层 =====
(function(){
  const toggle=document.getElementById('annToggle');
  const editor=document.getElementById('annEditor');
  const textEl=document.getElementById('annText');
  const panel=document.getElementById('annPanel');
  const list=document.getElementById('annList');
  const toast=document.getElementById('annToast');
  let anns=[];          // {name, txt, target}
  let mode=false, pendingTarget=null, editingIdx=-1;

  toggle.onclick=()=>{
    mode=!mode;
    document.body.classList.toggle('annmode',mode);
    toggle.classList.toggle('on',mode);
    toggle.textContent=mode?'✅ 批注中(点元素)':'✏️ 批注模式';
    panel.style.display=mode?'block':(anns.length?'block':'none');
  };

  document.addEventListener('click',(e)=>{
    if(!mode) return;
    const t=e.target;
    if(editor.contains(t)||panel.contains(t)||t===toggle||t.closest('.ann-mark')
       ||t===document.getElementById('verBadge')||document.getElementById('verPanel').contains(t)) return;
    const host=t.closest('[data-name]');
    if(!host) return;
    e.preventDefault();e.stopPropagation();
    pendingTarget=host; editingIdx=-1;
    textEl.value='';
    openEditorAt(host);
  },true);

  function openEditorAt(el){
    const r=el.getBoundingClientRect();
    editor.style.display='block';
    let left=Math.max(10,Math.min(r.left,window.innerWidth-270));
    let top=Math.max(10,Math.min(r.bottom+6,window.innerHeight-180));
    editor.style.left=left+'px'; editor.style.top=top+'px';
    setTimeout(()=>textEl.focus(),30);
  }

  textEl.addEventListener('keydown',(e)=>{
    if(e.key==='Enter' && !e.shiftKey && !e.isComposing && e.keyCode!==229){
      e.preventDefault(); saveAnn();
    } else if(e.key==='Escape'){ closeEditor(); }
  });

  function saveAnn(){
    const txt=textEl.value.trim();
    if(!txt){closeEditor();return;}
    if(editingIdx>=0){ anns[editingIdx].txt=txt; }
    else { anns.push({name:pendingTarget.getAttribute('data-name'),txt,target:pendingTarget}); }
    closeEditor(); renderAll();
    panel.style.display='block';
  }
  function closeEditor(){editor.style.display='none';pendingTarget=null;editingIdx=-1;}

  function renderAll(){
    document.querySelectorAll('.ann-mark').forEach(m=>m.remove());
    anns.forEach((a,i)=>{
      const r=a.target.getBoundingClientRect();
      const mark=document.createElement('div');
      mark.className='ann-mark';mark.textContent=i+1;
      mark.style.left=(window.scrollX+r.left+r.width-6)+'px';
      mark.style.top=(window.scrollY+r.top+10)+'px';
      mark.onclick=(ev)=>{ev.stopPropagation();focusAnn(i);};
      document.body.appendChild(mark);
    });
    list.innerHTML=anns.map((a,i)=>
      `<div class="annrow" data-i="${i}"><span class="no">${i+1}</span>
       <span class="tx">${esc(a.txt)}<div class="nm">@${esc(a.name)}</div></span>
       <span class="del" data-del="${i}">✕</span></div>`).join('')
       ||'<p style="color:#aaa;font:12px sans-serif">还没有批注,开启批注模式后点任意区块</p>';
    list.querySelectorAll('.annrow').forEach(row=>{
      row.onclick=(e)=>{if(e.target.dataset.del!==undefined)return;focusAnn(+row.dataset.i);};
    });
    list.querySelectorAll('[data-del]').forEach(b=>{
      b.onclick=(e)=>{e.stopPropagation();anns.splice(+b.dataset.del,1);renderAll();};
    });
  }
  function focusAnn(i){
    const el=anns[i].target;
    el.scrollIntoView({block:'center',behavior:'smooth'});
    el.classList.remove('annflash');void el.offsetWidth;el.classList.add('annflash');
    list.querySelectorAll('.annrow').forEach(r=>r.classList.toggle('active',+r.dataset.i===i));
  }
  function repositionMarks(){
    document.querySelectorAll('.ann-mark').forEach((m,i)=>{
      if(!anns[i])return;
      const r=anns[i].target.getBoundingClientRect();
      m.style.left=(window.scrollX+r.left+r.width-6)+'px';
      m.style.top=(window.scrollY+r.top+10)+'px';
    });
  }
  window.addEventListener('scroll',repositionMarks,{passive:true});
  window.addEventListener('resize',()=>setTimeout(repositionMarks,160));

  document.getElementById('annExport').onclick=()=>{
    if(!anns.length){showToast('还没有批注',true);return;}
    const md=anns.map((a,i)=>`${i+1}. 【${a.name}】${a.txt}`).join('\n');
    const payload='请根据以下批注修改这个数据分析报告页面:\n\n'+md;
    copyText(payload);
  };
  function copyText(t){
    if(navigator.clipboard&&navigator.clipboard.writeText){
      navigator.clipboard.writeText(t).then(()=>showToast('✅ 已复制,回对话框 Cmd/Ctrl+V 粘贴'))
        .catch(()=>fallback(t));
    } else fallback(t);
  }
  function fallback(t){
    const ta=document.createElement('textarea');ta.value=t;
    ta.style.position='fixed';ta.style.left='-9999px';document.body.appendChild(ta);ta.select();
    try{document.execCommand('copy');showToast('✅ 已复制,回对话框 Cmd/Ctrl+V 粘贴');}
    catch(e){showToast('复制失败,请重试',true);}
    document.body.removeChild(ta);
  }
  function showToast(msg,err){
    toast.textContent=msg;toast.style.background=err?'#c0392b':'#1a1a2e';
    toast.style.display='block';setTimeout(()=>toast.style.display='none',2200);
  }
  function esc(s){return s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
})();
</script>
