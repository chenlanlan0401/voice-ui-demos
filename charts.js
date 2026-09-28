// ===== 图表绘制 =====
function setupCanvas(cv){
  const dpr = window.devicePixelRatio||1;
  const cssW = cv.clientWidth, cssH = cv.height;
  cv.width = cssW*dpr; cv.height = cssH*dpr;
  const ctx = cv.getContext('2d');
  ctx.scale(dpr,dpr);
  return {ctx, W:cssW, H:cssH};
}
const COL = {hot:'#e17055', mid:'#6c5ce7', cool:'#00b894', box:'#a29bfe',
  boxLine:'#6c5ce7', whisk:'#b8bcc8', grid:'#eef0f4', ink:'#1a1a2e', sub:'#8890a0'};

function colorFor(median, maxMed){
  const r = median/maxMed;
  if(r>0.6) return COL.hot;
  if(r<0.28) return COL.cool;
  return COL.mid;
}

// ① 排行条形图（按中位数降序）
function drawBar(){
  const cv = document.getElementById('barChart');
  const {ctx,W,H} = setupCanvas(cv);
  const rows = [...DATA.summary].sort((a,b)=>b.median-a.median);
  const maxMed = Math.max(...rows.map(r=>r.median));
  const padL=150, padR=60, padT=10, padB=10;
  const plotW = W-padL-padR;
  const n = rows.length;
  const gap=6, barH=(H-padT-padB-(n-1)*gap)/n;
  ctx.clearRect(0,0,W,H);
  // 网格竖线
  ctx.strokeStyle=COL.grid; ctx.fillStyle=COL.sub; ctx.font='11px sans-serif';
  ctx.textAlign='center';
  for(let s=0;s<=60;s+=10){
    const x=padL + (s/maxMed)*plotW;
    if(x>W-padR+2) break;
    ctx.beginPath();ctx.moveTo(x,padT);ctx.lineTo(x,H-padB);ctx.stroke();
    ctx.fillText(s+'s',x,H-padB+0);
  }
  rows.forEach((r,i)=>{
    const y=padT+i*(barH+gap);
    const w=(r.median/maxMed)*plotW;
    const c=colorFor(r.median,maxMed);
    // 条
    ctx.fillStyle=c;
    roundRect(ctx,padL,y,w,barH,5); ctx.fill();
    // 题目标签
    ctx.fillStyle=COL.ink; ctx.font='12px sans-serif'; ctx.textAlign='right';
    ctx.textBaseline='middle';
    const label='Q'+r.id+' '+r.title.replace(/：.*/,'').slice(0,7);
    ctx.fillText(label,padL-10,y+barH/2);
    // 数值
    ctx.fillStyle='#fff'; ctx.textAlign='right'; ctx.font='bold 12px sans-serif';
    if(w>44) ctx.fillText(r.median+'s',padL+w-8,y+barH/2);
    else {ctx.fillStyle=c;ctx.textAlign='left';ctx.fillText(r.median+'s',padL+w+6,y+barH/2);}
  });
}

// ② 箱线图（P10-P25-中位-P75-P90，按中位降序）
function drawBox(){
  const cv=document.getElementById('boxChart');
  const {ctx,W,H}=setupCanvas(cv);
  const rows=[...DATA.summary].sort((a,b)=>b.median-a.median);
  const maxV=Math.max(...rows.map(r=>r.p90))*1.05;
  const padL=150,padR=30,padT=10,padB=24;
  const plotW=W-padL-padR;
  const n=rows.length, gap=8, rowH=(H-padT-padB-(n-1)*gap)/n;
  ctx.clearRect(0,0,W,H);
  const X=v=>padL+(v/maxV)*plotW;
  // 竖网格
  ctx.strokeStyle=COL.grid;ctx.fillStyle=COL.sub;ctx.font='11px sans-serif';ctx.textAlign='center';
  for(let s=0;s<=Math.ceil(maxV/20)*20;s+=20){
    const x=X(s); if(x>W-padR+2)break;
    ctx.beginPath();ctx.moveTo(x,padT);ctx.lineTo(x,H-padB);ctx.stroke();
    ctx.fillText(s+'s',x,H-padB+14);
  }
  rows.forEach((r,i)=>{
    const cy=padT+i*(rowH+gap)+rowH/2;
    const bh=Math.min(rowH*0.62,22);
    // 须线
    ctx.strokeStyle=COL.whisk;ctx.lineWidth=1.5;
    ctx.beginPath();ctx.moveTo(X(r.p10),cy);ctx.lineTo(X(r.p90),cy);ctx.stroke();
    ctx.beginPath();ctx.moveTo(X(r.p10),cy-6);ctx.lineTo(X(r.p10),cy+6);
    ctx.moveTo(X(r.p90),cy-6);ctx.lineTo(X(r.p90),cy+6);ctx.stroke();
    // 箱体
    ctx.fillStyle=COL.box; ctx.globalAlpha=.85;
    roundRect(ctx,X(r.p25),cy-bh/2,X(r.p75)-X(r.p25),bh,4);ctx.fill();
    ctx.globalAlpha=1;
    // 中位竖线
    ctx.strokeStyle=COL.boxLine;ctx.lineWidth=2.5;
    ctx.beginPath();ctx.moveTo(X(r.median),cy-bh/2);ctx.lineTo(X(r.median),cy+bh/2);ctx.stroke();
    // 标签
    ctx.fillStyle=COL.ink;ctx.font='12px sans-serif';ctx.textAlign='right';ctx.textBaseline='middle';
    ctx.fillText('Q'+r.id+' '+r.title.replace(/：.*/,'').slice(0,7),padL-10,cy);
  });
}

// ③ 散点图 思考时间 × 字数
function drawScatter(){
  const cv=document.getElementById('scatterChart');
  const {ctx,W,H}=setupCanvas(cv);
  const pts=DATA.scatter;
  const maxT=Math.max(...pts.map(p=>p.t))*1.02;
  const maxW=Math.max(...pts.map(p=>p.w))*1.05;
  const padL=48,padR=20,padT=14,padB=40;
  const plotW=W-padL-padR, plotH=H-padT-padB;
  const X=t=>padL+(t/maxT)*plotW;
  const Y=w=>padT+plotH-(w/maxW)*plotH;
  ctx.clearRect(0,0,W,H);
  // 网格
  ctx.strokeStyle=COL.grid;ctx.fillStyle=COL.sub;ctx.font='11px sans-serif';
  ctx.textAlign='center';ctx.textBaseline='top';
  for(let t=0;t<=Math.ceil(maxT/20)*20;t+=20){const x=X(t);if(x>W-padR)break;
    ctx.beginPath();ctx.moveTo(x,padT);ctx.lineTo(x,padT+plotH);ctx.stroke();
    ctx.fillText(t+'s',x,padT+plotH+8);}
  ctx.textAlign='right';ctx.textBaseline='middle';
  for(let w=0;w<=Math.ceil(maxW/40)*40;w+=40){const y=Y(w);if(y<padT)break;
    ctx.beginPath();ctx.moveTo(padL,y);ctx.lineTo(padL+plotW,y);ctx.stroke();
    ctx.fillText(w+'字',padL-6,y);}
  // 轴标题
  ctx.fillStyle=COL.sub;ctx.textAlign='center';ctx.textBaseline='top';
  ctx.font='12px sans-serif';
  ctx.fillText('思考时间（秒）→',padL+plotW/2,padT+plotH+22);
  // 点
  const maxMed=Math.max(...DATA.summary.map(r=>r.median));
  const medById={};DATA.summary.forEach(r=>medById[r.id]=r.median);
  pts.forEach(p=>{
    ctx.beginPath();
    ctx.fillStyle=colorFor(medById[p.q],maxMed);
    ctx.globalAlpha=.42;
    ctx.arc(X(p.t),Y(p.w),3.2,0,7);ctx.fill();
  });
  ctx.globalAlpha=1;
}

function roundRect(ctx,x,y,w,h,r){
  r=Math.min(r,h/2,w/2);
  ctx.beginPath();
  ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);
  ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);
  ctx.arcTo(x,y,x+w,y,r);ctx.closePath();
}

// ④ 明细表
function fillTable(){
  const tb=document.querySelector('#detailTable tbody');
  const rows=[...DATA.summary].sort((a,b)=>b.median-a.median);
  const maxMed=Math.max(...rows.map(r=>r.median));
  tb.innerHTML=rows.map(r=>{
    const ratio=r.median/maxMed;
    let cls='',pill='<span class="pill mid">中等</span>';
    if(ratio>0.6){cls='hot';pill='<span class="pill hot">费脑</span>';}
    else if(ratio<0.28){cls='cool';pill='<span class="pill cool">秒答</span>';}
    // 卡壳诊断：思考偏长 + 效率偏低
    let diag=pill;
    if(r.median>maxMed*0.4 && r.efficiency<0.9){
      diag='<span class="pill" style="background:#fff0d6;color:#b8860b">⚠ 疑似卡壳</span>';
      cls='';
    }
    return `<tr class="${cls}">
      <td>Q${r.id} ${r.title.replace(/：.*/,'')}</td>
      <td>${r.type}</td>
      <td><b>${r.median}s</b></td>
      <td>${r.iqr}s</td>
      <td>${r.median_words}</td>
      <td>${r.efficiency}</td>
      <td>${diag}</td></tr>`;
  }).join('');
}

function drawAll(){drawBar();drawBox();drawScatter();fillTable();}
window.addEventListener('load',drawAll);
let rt;window.addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(drawAll,150);});
