const HES_THR=7.0, SLOW_THR=25.0;  // 分界:无措7% / 慢答25%
const COL={wait:'#e17055',hint:'#f0a500',both:'#c0392b',none:'#00b894',ink:'#1a1a2e',sub:'#8890a0',grid:'#eef0f4'};

function classify(d){
  const slow=d.slow_share>=SLOW_THR, hes=d.hes_rate>=HES_THR;
  if(slow&&hes) return "both";
  if(slow&&!hes) return "wait";
  if(!slow&&hes) return "hint";
  return "none";
}
function shortT(t){return t.replace(/[，。？！,.?].*/,'').slice(0,7);}

function drawQuad(){
  const cv=document.getElementById('quad');
  const dpr=window.devicePixelRatio||1, W=cv.clientWidth, H=cv.height;
  cv.width=W*dpr; cv.height=H*dpr;
  const ctx=cv.getContext('2d'); ctx.scale(dpr,dpr);
  const padL=54,padR=24,padT=20,padB=44, pW=W-padL-padR, pH=H-padT-padB;
  const maxX=16, maxY=60;  // 无措率上限16, 慢答上限60
  const X=v=>padL+v/maxX*pW, Y=v=>padT+pH-v/maxY*pH;
  ctx.clearRect(0,0,W,H);

  // 象限底色
  const xt=X(HES_THR), yt=Y(SLOW_THR);
  ctx.globalAlpha=.06;
  ctx.fillStyle=COL.wait; ctx.fillRect(padL,padT,xt-padL,yt-padT);       // 左上=慢不无措=等待
  ctx.fillStyle=COL.both; ctx.fillRect(xt,padT,padL+pW-xt,yt-padT);      // 右上=都高
  ctx.fillStyle=COL.none; ctx.fillRect(padL,yt,xt-padL,padT+pH-yt);      // 左下=都低
  ctx.fillStyle=COL.hint; ctx.fillRect(xt,yt,padL+pW-xt,padT+pH-yt);     // 右下=无措
  ctx.globalAlpha=1;

  // 网格
  ctx.strokeStyle=COL.grid; ctx.fillStyle=COL.sub; ctx.font='11px sans-serif';
  ctx.textAlign='center'; ctx.textBaseline='top';
  for(let v=0;v<=maxX;v+=4){const x=X(v);ctx.beginPath();ctx.moveTo(x,padT);ctx.lineTo(x,padT+pH);ctx.stroke();ctx.fillText(v+'%',x,padT+pH+6);}
  ctx.textAlign='right'; ctx.textBaseline='middle';
  for(let v=0;v<=maxY;v+=10){const y=Y(v);ctx.beginPath();ctx.moveTo(padL,y);ctx.lineTo(padL+pW,y);ctx.stroke();ctx.fillText(v+'%',padL-5,y);}

  // 分界线
  ctx.strokeStyle='#c9a0a0'; ctx.setLineDash([5,4]); ctx.lineWidth=1.5;
  ctx.beginPath();ctx.moveTo(xt,padT);ctx.lineTo(xt,padT+pH);ctx.stroke();
  ctx.beginPath();ctx.moveTo(padL,yt);ctx.lineTo(padL+pW,yt);ctx.stroke();
  ctx.setLineDash([]);

  // 象限角标
  ctx.font='bold 12px sans-serif'; ctx.textBaseline='top';
  ctx.fillStyle=COL.wait; ctx.textAlign='left'; ctx.fillText('◤ 需要时间·不无措 → 等待',padL+6,padT+4);
  ctx.fillStyle=COL.both; ctx.textAlign='right'; ctx.fillText('又慢又无措 → 等待+提示 ◥',padL+pW-6,padT+4);
  ctx.fillStyle='#b8860b'; ctx.textAlign='right'; ctx.fillText('无措为主 → 提示 ◢',padL+pW-6,padT+pH-18);
  ctx.fillStyle='#00997a'; ctx.textAlign='left'; ctx.fillText('◣ 又快又顺 → 不动',padL+6,padT+pH-18);

  // 轴标题
  ctx.fillStyle=COL.sub; ctx.font='12px sans-serif'; ctx.textAlign='center'; ctx.textBaseline='top';
  ctx.fillText('无措率 → 越右越多人不知道说啥',padL+pW/2,padT+pH+22);
  ctx.save(); ctx.translate(14,padT+pH/2); ctx.rotate(-Math.PI/2);
  ctx.textAlign='center'; ctx.fillText('慢答占比 → 越上越多人需要时间',0,0); ctx.restore();

  // 点 + 标签(防重叠简单错位)
  const placed=[];
  Q.forEach(d=>{
    const x=X(d.hes_rate), y=Y(d.slow_share), c=COL[classify(d)];
    ctx.beginPath(); ctx.fillStyle=c; ctx.globalAlpha=.9; ctx.arc(x,y,6,0,7); ctx.fill(); ctx.globalAlpha=1;
    ctx.strokeStyle='#fff'; ctx.lineWidth=1.5; ctx.stroke();
    // 标签
    ctx.fillStyle=COL.ink; ctx.font='11px sans-serif'; ctx.textAlign='left'; ctx.textBaseline='middle';
    let ly=y; for(const p of placed){if(Math.abs(p.x-x)<70&&Math.abs(p.y-ly)<13)ly=p.y+13;}
    placed.push({x:x+8,y:ly});
    ctx.fillText(shortT(d.title),x+9,ly);
  });
}

function fillLists(){
  const g={wait:[],hint:[],both:[],none:[]};
  Q.forEach(d=>g[classify(d)].push(d));
  const order=["wait","both","hint","none"];
  const map={wait:"q-wait",hint:"q-hint",both:"q-both",none:"q-none"};
  for(const key in map){
    const el=document.getElementById(map[key]);
    const arr=g[key].sort((a,b)=>(b.slow_share+b.hes_rate)-(a.slow_share+a.hes_rate));
    if(!arr.length){el.innerHTML='<li class="empty">(本课无此类题)</li>';continue;}
    el.innerHTML=arr.map(d=>`<li><b>${shortT(d.title)}</b> <span class="metrics">慢答${d.slow_share}% · 无措${d.hes_rate}%</span></li>`).join('');
  }
  // 完整表
  const tb=document.querySelector('#fullTable tbody');
  const clsname={wait:'需要时间→等待',hint:'无措→提示',both:'都高→等待+提示',none:'又快又顺→不动'};
  const clscol={wait:'var(--wait)',hint:'#b8860b',both:'var(--both)',none:'#00997a'};
  tb.innerHTML=[...Q].sort((a,b)=>b.slow_share-a.slow_share).map(d=>{
    const c=classify(d);
    return `<tr><td>${d.k}</td><td>${d.title}</td><td>${d.slow_share}</td><td>${d.hes_rate}</td><td style="color:${clscol[c]};font-weight:700">${clsname[c]}</td></tr>`;
  }).join('');
}

function renderAll(){drawQuad();fillLists();}
window.addEventListener('load',renderAll);
let rt;window.addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(drawQuad,150);});
