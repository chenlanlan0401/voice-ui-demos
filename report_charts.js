// ===== 通用 =====
function setupCanvas(cv){
  const dpr=window.devicePixelRatio||1, W=cv.clientWidth, H=cv.height;
  cv.width=W*dpr; cv.height=H*dpr;
  const ctx=cv.getContext('2d'); ctx.scale(dpr,dpr);
  return {ctx,W,H};
}
const C={tier1:'#e17055',tier2:'#f0a500',tier3:'#00b894',ink:'#1a1a2e',sub:'#8890a0',
  grid:'#eef0f4',brand:'#6c5ce7',brand2:'#a29bfe'};
function roundRect(ctx,x,y,w,h,r){r=Math.min(r,Math.abs(h)/2,Math.abs(w)/2);
  ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);
  ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath();}
function shortTitle(t){return t.replace(/[，。？！,.?].*/,'').slice(0,8);}

// 梯队划分：第一梯队>25%，第二梯队16~25%，第三梯队<16%
function tierOf(m){return m>=25?1:(m>=16?2:3);}
function tierColor(m){return [null,C.tier1,C.tier2,C.tier3][tierOf(m)];}

// ① 误伤率梯队条形图
function drawMisfireBar(){
  const cv=document.getElementById('misfireBar');const {ctx,W,H}=setupCanvas(cv);
  const rows=[...D.table].sort((a,b)=>b.misfire-a.misfire);
  const maxV=Math.max(...rows.map(r=>r.misfire));
  const padL=140,padR=48,padT=8,padB=8,plotW=W-padL-padR;
  const n=rows.length,gap=5,bh=(H-padT-padB-(n-1)*gap)/n;
  ctx.clearRect(0,0,W,H);
  ctx.strokeStyle=C.grid;ctx.fillStyle=C.sub;ctx.font='11px sans-serif';ctx.textAlign='center';
  for(let v=0;v<=50;v+=10){const x=padL+v/maxV*plotW;if(x>W-padR+2)break;
    ctx.beginPath();ctx.moveTo(x,padT);ctx.lineTo(x,H-padB);ctx.stroke();
    ctx.fillText(v+'%',x,H-padB);}
  rows.forEach((r,i)=>{
    const y=padT+i*(bh+gap),w=r.misfire/maxV*plotW,c=tierColor(r.misfire);
    ctx.fillStyle=c;roundRect(ctx,padL,y,w,bh,4);ctx.fill();
    ctx.fillStyle=C.ink;ctx.font='12px sans-serif';ctx.textAlign='right';ctx.textBaseline='middle';
    ctx.fillText('Q'+r.qid.slice(-3)+'-'+r.sub+' '+shortTitle(r.title),padL-8,y+bh/2);
    ctx.fillStyle='#fff';ctx.textAlign='right';ctx.font='bold 11px sans-serif';
    if(w>42)ctx.fillText(r.misfire+'%',padL+w-6,y+bh/2);
    else{ctx.fillStyle=c;ctx.textAlign='left';ctx.fillText(r.misfire+'%',padL+w+5,y+bh/2);}
  });
  // 门槛线
  [16,25].forEach(thr=>{const x=padL+thr/maxV*plotW;
    ctx.strokeStyle=C.brand;ctx.setLineDash([4,3]);ctx.lineWidth=1.5;
    ctx.beginPath();ctx.moveTo(x,padT);ctx.lineTo(x,H-padB);ctx.stroke();ctx.setLineDash([]);
    ctx.fillStyle=C.brand;ctx.font='10px sans-serif';ctx.textAlign='center';
    ctx.fillText(thr+'%门槛',x,padT+8);});
}

// ② 两列散点：慢答占比 × 慢答者长答率
function drawScatter2d(){
  const cv=document.getElementById('scatter2d');const {ctx,W,H}=setupCanvas(cv);
  const rows=D.table;
  const padL=54,padR=20,padT=16,padB=44,plotW=W-padL-padR,plotH=H-padT-padB;
  const maxX=60,maxY=100;
  const X=v=>padL+v/maxX*plotW,Y=v=>padT+plotH-v/maxY*plotH;
  ctx.clearRect(0,0,W,H);
  ctx.strokeStyle=C.grid;ctx.fillStyle=C.sub;ctx.font='11px sans-serif';
  ctx.textAlign='center';ctx.textBaseline='top';
  for(let v=0;v<=maxX;v+=10){const x=X(v);ctx.beginPath();ctx.moveTo(x,padT);ctx.lineTo(x,padT+plotH);ctx.stroke();ctx.fillText(v+'%',x,padT+plotH+6);}
  ctx.textAlign='right';ctx.textBaseline='middle';
  for(let v=0;v<=maxY;v+=20){const y=Y(v);ctx.beginPath();ctx.moveTo(padL,y);ctx.lineTo(padL+plotW,y);ctx.stroke();ctx.fillText(v+'%',padL-5,y);}
  // 门槛虚线：慢答25% + 长答率55%
  ctx.strokeStyle=C.brand;ctx.setLineDash([4,3]);ctx.lineWidth=1.3;
  ctx.beginPath();ctx.moveTo(X(25),padT);ctx.lineTo(X(25),padT+plotH);ctx.stroke();
  ctx.beginPath();ctx.moveTo(padL,Y(55));ctx.lineTo(padL+plotW,Y(55));ctx.stroke();ctx.setLineDash([]);
  // 轴标题
  ctx.fillStyle=C.sub;ctx.font='12px sans-serif';ctx.textAlign='center';ctx.textBaseline='top';
  ctx.fillText('慢答者占比 → 越右越多人要等',padL+plotW/2,padT+plotH+24);
  // 点
  rows.forEach(r=>{
    const x=X(r.slow_share),y=Y(r.cond_long);
    ctx.fillStyle=tierColor(r.misfire);ctx.globalAlpha=.85;
    ctx.beginPath();ctx.arc(x,y,6,0,7);ctx.fill();ctx.globalAlpha=1;
    ctx.fillStyle=C.ink;ctx.font='10px sans-serif';ctx.textAlign='left';ctx.textBaseline='middle';
    ctx.fillText(' '+shortTitle(r.title),x+5,y);
  });
}

// ③ 秒数覆盖曲线（只画该等的题：误伤率≥16%）
function drawSecCurve(){
  const cv=document.getElementById('secCurve');const {ctx,W,H}=setupCanvas(cv);
  const rows=D.table.filter(r=>r.misfire>=16).sort((a,b)=>b.misfire-a.misfire);
  const padL=48,padR=130,padT=14,padB=40,plotW=W-padL-padR,plotH=H-padT-padB;
  const maxT=18;
  const X=t=>padL+t/maxT*plotW,Y=p=>padT+plotH-p/100*plotH;
  ctx.clearRect(0,0,W,H);
  ctx.strokeStyle=C.grid;ctx.fillStyle=C.sub;ctx.font='11px sans-serif';ctx.textAlign='center';ctx.textBaseline='top';
  for(let t=0;t<=maxT;t+=2){const x=X(t);ctx.beginPath();ctx.moveTo(x,padT);ctx.lineTo(x,padT+plotH);ctx.stroke();ctx.fillText(t+'s',x,padT+plotH+6);}
  ctx.textAlign='right';ctx.textBaseline='middle';
  for(let p=0;p<=100;p+=25){const y=Y(p);ctx.beginPath();ctx.moveTo(padL,y);ctx.lineTo(padL+plotW,y);ctx.stroke();ctx.fillText(p+'%',padL-5,y);}
  const pal=[C.tier1,'#e8843f','#f0a500','#c9962a','#8b7bd8','#00b894'];
  rows.forEach((r,idx)=>{
    const secs=r.slowlong_secs;const total=secs.length;
    ctx.strokeStyle=pal[idx%pal.length];ctx.lineWidth=2;ctx.beginPath();
    for(let t=0;t<=maxT;t+=0.5){
      const covered=secs.filter(s=>s<=t).length/total*100;
      const x=X(t),y=Y(covered);
      if(t===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
    }
    ctx.stroke();
    // 标签
    const lastY=Y(secs.filter(s=>s<=maxT).length/total*100);
    ctx.fillStyle=pal[idx%pal.length];ctx.font='11px sans-serif';ctx.textAlign='left';ctx.textBaseline='middle';
    ctx.fillText(shortTitle(r.title),padL+plotW+6,padT+8+idx*16);
  });
  ctx.fillStyle=C.sub;ctx.font='12px sans-serif';ctx.textAlign='center';ctx.textBaseline='top';
  ctx.fillText('等待秒数(含1-2s延迟) →',padL+plotW/2,padT+plotH+22);
}

// ④ 主表
function fillTable(){
  const tb=document.querySelector('#mainTable tbody');
  const rows=[...D.table].sort((a,b)=>b.misfire-a.misfire);
  // 口径A：误伤率≥16% 该等
  // 口径B：慢答≥25%且长答率≥55% → 该等；或 长答率≥70%(小众强需求) → 该等
  function vA(r){return r.misfire>=16?'wait':'ok';}
  function vB(r){
    if(r.slow_share>=25 && r.cond_long>=55)return 'wait';
    if(r.cond_long>=70)return 'wait'; // 人少但个个憋长答
    if(r.slow_share>=25)return 'short';
    return 'ok';
  }
  const lab={wait:'该等',ok:'立即开麦',short:'答案本就短'};
  tb.innerHTML=rows.map(r=>{
    const a=vA(r),b=vB(r);
    const diff=((a==='wait')!==(b==='wait'))?'<span class="pill diff">★分歧</span>':'';
    const tier=tierOf(r.misfire);
    const dot=`<span class="tierband" style="background:${tierColor(r.misfire)}"></span>`;
    return `<tr>
      <td>${dot}Q${r.qid.slice(-3)}-${r.sub} ${shortTitle(r.title)}</td>
      <td>${r.type}</td><td>${r.n}</td>
      <td>${r.slow_share}</td><td>${r.cond_long}</td><td><b>${r.misfire}</b></td>
      <td>${r.med}</td><td>${r.p75}</td><td>${r.p90}</td>
      <td><span class="pill ${a}">${lab[a]}</span></td>
      <td><span class="pill ${b}">${lab[b]}</span></td>
      <td>${diff}</td></tr>`;
  }).join('');
  // KPI 平均误伤率
  const avg=(D.table.reduce((s,r)=>s+r.misfire,0)/D.table.length).toFixed(1);
  document.getElementById('kpiMisfire').textContent=avg+'%';
}

function drawAll(){drawMisfireBar();drawScatter2d();drawSecCurve();fillTable();}
window.addEventListener('load',drawAll);
let rt;window.addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(drawAll,150);});
