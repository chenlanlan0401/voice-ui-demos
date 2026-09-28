// 渲染最终判定
(function(){
  const wait=F.filter(f=>f.verdict==="该等").sort((a,b)=>b.misfire-a.misfire);
  const ok=F.filter(f=>f.verdict==="不该等").sort((a,b)=>b.misfire-a.misfire);
  const fuzzy=F.filter(f=>f.band==="模糊带").sort((a,b)=>b.misfire-a.misfire);

  // 该等卡片
  document.getElementById("waitCards").innerHTML=wait.map(f=>{
    const real=(f.p75-1.5).toFixed(1);
    return `<div class="qcard wait" data-name="该等-${f.key}">
      <div class="qhead">
        <span class="badge wait">该等</span>
        <span class="qid">${f.key}</span>
        <span class="title">${f.title}</span>
      </div>
      <div class="metrics">
        <span>误伤率 <b>${f.misfire}%</b></span>
        <span>慢答 <b>${f.slow_share}%</b>(${f.n_slow}人)</span>
        <span>慢答者长答率 <b>${f.cond_long}%</b></span>
        <span>建议等待 <b class="wait-sec">真实约${real}s</b>(埋点P75=${f.p75}s)</span>
      </div>
      <div class="reason"><b>判定依据:</b>${f.reason}</div>
    </div>`;
  }).join("");

  // 不该等表
  document.querySelector("#okTable tbody").innerHTML=ok.map(f=>
    `<tr><td>${f.key}</td><td>${f.title}</td><td>${f.misfire}</td><td>${f.slow_share}</td><td>${f.cond_long}</td></tr>`
  ).join("");

  // 模糊带表
  document.querySelector("#fuzzyTable tbody").innerHTML=fuzzy.map(f=>{
    const vc=f.verdict==="该等"?'style="color:var(--wait);font-weight:700"':'style="color:var(--ok);font-weight:700"';
    return `<tr><td>${f.key}</td><td>${f.title}</td><td>${f.misfire}</td><td>${f.cond_long}</td><td ${vc}>${f.verdict}</td><td style="text-align:left;white-space:normal;max-width:280px">${f.reason}</td></tr>`;
  }).join("");
})();
