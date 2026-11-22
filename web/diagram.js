"use strict";
window.drawProjectView = function(host,report) {
  const el=(tag,text)=>{const n=document.createElement(tag); if(text!=null)n.textContent=text; return n;};
  const title=text=>{const p=el("p",text);p.className="chart-title";host.append(p);};
  if(report.swatches){
    title("Text roles in their actual colors");
    report.swatches.slice(0,12).forEach(s=>{ const n=el("span",s.label);n.className="swatch";n.style.color=s.foreground;n.style.backgroundColor=s.background;host.append(n);});return;
  }
  if(report.atlas){
    title("Frame map · texture coordinates");
    const {width,height,frames}=report.atlas;
    const canvas=el("canvas");canvas.setAttribute("aria-label","Atlas layout; flagged frame names also appear in the findings table.");
    canvas.width=980;canvas.height=160;canvas.style.width="100%";canvas.style.height="auto";canvas.style.maxHeight="160px";host.append(canvas);
    const ctx=canvas.getContext("2d");const scale=Math.min(976/width,150/height);const ox=3,oy=3;
    ctx.fillStyle="#eef3eb";ctx.fillRect(ox,oy,width*scale,height*scale);
    const byName=new Map(report.rows.map(r=>[r.Frame,r.Finding]));
    frames.slice(0,300).forEach(f=>{const bad=byName.get(f.name)!=="Clear";ctx.strokeStyle=bad?"#b64c31":"#297063";ctx.fillStyle=bad?"#ea91645c":"#4fa49255";const x=ox+f.x*scale,y=oy+f.y*scale,w=f.w*scale,h=f.h*scale;ctx.fillRect(x,y,w,h);ctx.strokeRect(x,y,w,h);if(w>55&&h>16){ctx.fillStyle="#152523";ctx.font="12px sans-serif";ctx.fillText(f.name,x+4,y+14,w-8);}});
    return;
  }
  const config=["Unmet demand by day \u00b7 units", "Date", "Unmet demand"];const [caption,label,value]=config;let items;
  if(value){items=report.rows.map(r=>[label.split("|").map(k=>r[k]??"").join(" / "),Number(r[value])]).filter(a=>Number.isFinite(a[1]));}
  else{const counts=new Map();report.rows.forEach(r=>{const k=String(r[label]??"Unspecified");counts.set(k,(counts.get(k)||0)+1);});items=[...counts];}
  if(!items.length)return;
  items.sort((a,b)=>Math.abs(b[1])-Math.abs(a[1]));const max=Math.max(1,...items.map(a=>Math.abs(a[1])));
  title(caption+(items.length>5?" · top 5":""));
  items.slice(0,5).forEach(([label,n])=>{const row=el("div");row.className="bar-line";const name=el("span",label),track=el("div"),bar=el("div"),amount=el("b",n.toLocaleString("en-US",{maximumFractionDigits:3}));track.className="bar-track";bar.style.width=(100*Math.abs(n)/max)+"%";if(n<0)bar.style.backgroundColor="#94612c";track.append(bar);row.append(name,track,amount);host.append(row);});
};
