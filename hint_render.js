(function(){
  const tiers=[
    {name:"强提示",key:"strong",color:"var(--strong)",desc:"慢答>40% · 一半左右学生需要时间,郑重给一句思考引导"},
    {name:"轻提示",key:"light",color:"var(--light)",desc:"慢答20-40% · 相当一部分人需要想,给一句淡提示"},
    {name:"不提示",key:"none",color:"var(--none)",desc:"慢答<20% · 多数人几秒内秒答,保持原样不打扰"},
  ];
  const box=document.getElementById("tierList");
  let html="";
  tiers.forEach(t=>{
    const qs=H.filter(h=>h.tier===t.name);
    html+=`<div class="tierhead" data-name="${t.name}标题"><span class="dot" style="background:${t.color}"></span>${t.name}(${qs.length}道)<span style="font-size:12px;color:var(--sub);font-weight:400">— ${t.desc}</span></div>`;
    if(t.key==="none"){
      html+=`<div class="card" data-name="不提示表"><table><thead><tr><th>题号</th><th>题目</th><th>慢答%</th><th>慢答人数</th></tr></thead><tbody>`;
      qs.forEach(h=>{html+=`<tr><td>${h.k}</td><td>${h.title}</td><td>${h.slow_share}</td><td>${h.n_slow}</td></tr>`;});
      html+=`</tbody></table></div>`;
    }else{
      qs.forEach(h=>{
        const w=Math.min(100,h.slow_share*1.6);
        html+=`<div class="qcard ${t.key}" data-name="题-${h.k}">
          <div class="qhead"><span class="qid">${h.k}</span><span class="title">${h.title}</span></div>
          <div class="share">慢答者占比 <b style="color:${t.color}">${h.slow_share}%</b>(${h.n_slow}人 / 共${h.n}人) · 全体开口中位${h.med_all}s · P75 ${h.p75_all}s</div>
          <div class="bar"><i style="width:${w}%;background:${t.color}"></i></div>
          ${h.copy?`<div class="copy">${h.copy}</div>`:''}
          ${h.k==="466168-1"?'<div class="flagnote">⚠️ 边界题:慢答者长答率仅21.6%,慢的人多半卡壳而非思考。放轻提示(安抚)或降为不提示都可,你定。</div>':''}
        </div>`;
      });
    }
  });
  box.innerHTML=html;
})();
