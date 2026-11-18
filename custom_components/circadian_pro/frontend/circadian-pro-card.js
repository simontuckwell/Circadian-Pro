/** Circadian Pro dashboard card: read-only astronomical graph and native controls. */
const TYPE = "circadian-pro-card";
const WIDTH = 360, LEFT = 19, RIGHT = 342, TOP = 12, BOTTOM = 79;
const MODES = {solar_elevation:"Solar Elevation", default:"Natural", linear:"Linear", tanh:"Sigmoid"};
const CSS = [
":host{display:block;color:var(--primary-text-color)}",
"ha-card{container-type:inline-size;overflow:hidden;border-radius:19px;box-shadow:var(--ha-card-box-shadow,0 2px 10px #0001)}",
".main{padding:20px 21px 16px}.head,.identity,.actions,.numbers,.bottom,.mode{display:flex;align-items:center}",
".head,.bottom{justify-content:space-between;gap:10px}.identity{gap:11px;min-width:0}",
".icon{display:grid;place-items:center;width:37px;height:37px;border-radius:12px;background:color-mix(in srgb,var(--primary-color,#2796bd) 10%,transparent);color:var(--primary-color,#2796bd);flex-shrink:0;transition:background .2s,color .2s,box-shadow .2s}",
".icon.lit{background:rgba(251,188,66,.20);color:#c28a25;box-shadow:inset 0 0 0 1px rgba(223,153,34,.16),0 0 10px rgba(244,176,54,.14)}",
".icon.lit ha-icon{filter:drop-shadow(0 0 2px rgba(238,169,43,.48))}",
".icon.dark{background:var(--secondary-background-color,#8882);color:var(--secondary-text-color);opacity:.75}",
".icon ha-icon{--mdc-icon-size:23px}.name{font-size:17px;font-weight:650;letter-spacing:-.3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}",
".subname{margin-top:1px;font-size:11px;color:var(--secondary-text-color)}.actions{gap:9px;flex-shrink:0}",
".pill{border-radius:99px;padding:5px 10px;font-size:11px;font-weight:700}",
".pill.automatic{color:#287e5c;background:rgba(39,167,107,.13)}",
".pill.manual{color:#a36d14;background:rgba(240,164,45,.16)}",
".pill.paused,.pill.unavailable{color:var(--secondary-text-color);background:var(--secondary-background-color,#8882)}",
".toggle{position:relative;width:39px;height:23px;border:0;border-radius:99px;cursor:pointer;background:#8885;padding:3px;flex-shrink:0;box-sizing:border-box;transition:background .16s}",
".toggle[aria-checked='true']{background:var(--primary-color,#259cbc)}",
".knob{display:block;width:17px;height:17px;background:#fff;border-radius:50%;box-shadow:0 1px 3px #0002;transition:transform .16s}",
".toggle[aria-checked='true'] .knob{transform:translateX(16px)}",
".toggle:disabled{opacity:.45;cursor:not-allowed}button:focus-visible{outline:2px solid var(--primary-color,#259cbc);outline-offset:3px}",
".numbers{gap:11px;margin-top:18px}.metric{flex:1;min-width:0;border-radius:13px;padding:12px 13px 11px;background:var(--secondary-background-color,#8881)}",
".metric-label{text-transform:uppercase;color:var(--secondary-text-color);font-size:10px;font-weight:700;letter-spacing:.5px}",
".metric-value{display:flex;gap:8px;align-items:center;margin-top:4px;font-size:27px;font-weight:650;letter-spacing:-1px;line-height:1.2}",
".unit{font-size:14px;font-weight:600;opacity:.7;letter-spacing:0;margin-left:-5px}",
".swatch{height:21px;width:21px;flex-shrink:0;display:inline-block;border-radius:6px;border:1px solid #0002;box-shadow:0 1px 3px #0001}",
".curve{margin-top:16px}.curve-heading{display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin:0 3px 5px}",
".curve-title{font-weight:620;font-size:12px}.curve-now{font-size:10px;color:var(--secondary-text-color);font-variant-numeric:tabular-nums}",
".solar-times{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:4px;margin:2px 0 0;color:var(--secondary-text-color);font-size:10px}",
".solar-times span:nth-child(2){text-align:center}.solar-times span:nth-child(3){text-align:right}.solar-times b{font-weight:500}",
"svg{width:100%;height:auto;display:block;overflow:visible}.axis-label{font-size:10px;fill:var(--secondary-text-color);font-family:inherit}",
".divider{border:0;height:1px;background:var(--divider-color,#8883);margin:11px 0 12px}",
".mode{gap:6px;font-size:11px;color:var(--secondary-text-color)}.mode ha-icon{--mdc-icon-size:18px}",
".resume{border:0;background:none;color:var(--primary-color,#259cbc);cursor:pointer;font:inherit;font-size:11px;font-weight:650;padding:4px}",
".resume:disabled{opacity:.4;cursor:wait}.note{font-size:11px;color:var(--secondary-text-color);line-height:1.5;padding:12px;text-align:center}",
".error{color:var(--error-color,#c53c3c);padding:7px 0 0;font-size:11px}",
"@container (max-width:400px){.main{padding:17px 15px 15px}.head{flex-wrap:wrap;row-gap:8px}.identity{flex:1 1 168px}.name{font-size:16px;line-height:1.25;white-space:normal;overflow:visible;text-overflow:clip;overflow-wrap:anywhere}.actions{gap:6px;margin-left:auto}.pill{padding:4px 8px}.numbers{gap:9px;margin-top:12px}.metric{padding:11px 10px}.metric-value{font-size:clamp(19px,6cqi,24px);gap:5px;white-space:nowrap}.unit{font-size:12px;margin-left:-3px}.swatch{width:18px;height:18px}.curve{margin-top:12px}}",
"@container (max-width:350px){.solar-times b{display:block}.solar-times{font-size:10px}}",
"@container (max-width:315px){.identity{flex-basis:100%}.actions{width:100%;justify-content:flex-end}.numbers{gap:7px}.metric{padding:10px 8px}.metric-value{font-size:20px;gap:4px}.swatch{width:16px;height:16px}.unit{font-size:11px}}",
"@container (max-width:270px){.numbers{flex-direction:column;align-items:stretch}.metric{flex:none}.metric-value{font-size:23px}}",
"@media(prefers-reduced-motion:reduce){.toggle,.knob,.icon{transition:none}}"
].join("");

export function escapeHtml(value) {
 return String(value ?? "").replace(/[&<>"']/g, ch=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
}
export function profileStatus(state, attrs={}) {
 if (state !== "on" && state !== "off") return "Unavailable";
 if (state === "off") return "Paused";
 const m=attrs.manual_control;
 return (Array.isArray(m) ? m.length>0 : Boolean(m)) ? "Manual" : "Automatic";
}
export function lightGroupStatus(lightEntityIds, states={}) {
 // The light group, not the adaptation switch, defines whether a room is lit.
 // If any member is on, the group is on; only an entirely off group is off.
 // Missing or unavailable states must not be mistaken for lights being off.
 if(!Array.isArray(lightEntityIds) || lightEntityIds.length===0)return "unknown";
 const statuses=lightEntityIds.map(id=>states?.[id]?.state);
 if(statuses.includes("on"))return "on";
 if(statuses.every(status=>status==="off"))return "off";
 return "unknown";
}
export function interpolatePoints(points, time) {
 if (!Array.isArray(points) || !points.length || !Number.isFinite(time)) return null;
 if (time <= points[0][0]) return points[0][1];
 if (time >= points[points.length-1][0]) return points[points.length-1][1];
 let lo=0,hi=points.length-1;
 while (hi-lo>1) { const mid=(hi+lo)>>1; if (points[mid][0]<=time) lo=mid; else hi=mid; }
 const a=points[lo],b=points[hi];
 return a[1]+(b[1]-a[1])*(time-a[0])/(b[0]-a[0]);
}
export function curveGeometry(curve, time) {
 if (!curve || !Array.isArray(curve.points) || curve.points.length<2) return null;
 const start=Number(curve.day_start),end=Number(curve.day_end);
 const low=Number(curve.min_brightness),high=Number(curve.max_brightness);
 if (![start,end,low,high].every(Number.isFinite) || end<=start || high<low) return null;
 const points=curve.points;
 if (!points.every((p,i)=>Array.isArray(p) && p.length===2 && p.every(Number.isFinite)
       && p[0]>=start && p[0]<=end && (i===0 || p[0]>points[i-1][0]))) return null;
 const x=t=>LEFT+(Math.max(start,Math.min(end,t))-start)/(end-start)*(RIGHT-LEFT);
 const y=v=>BOTTOM-(Math.max(low,Math.min(high,v))-low)/Math.max(1,high-low)*(BOTTOM-TOP);
 const path=points.map((p,i)=>(i?"L":"M")+x(p[0]).toFixed(2)+" "+y(p[1]).toFixed(2)).join(" ");
 const now=Math.max(start,Math.min(end,time));
 return {path,x,nowX:x(now),nowY:y(interpolatePoints(points,now))};
}
function clock(time,zone) {
 if(!Number.isFinite(time))return "—";
 try{return new Intl.DateTimeFormat(undefined,{timeZone:zone||undefined,hour:"2-digit",minute:"2-digit",hour12:false}).format(time*1000);}
 catch{return "—";}
}
function kelvinColour(value) {
 const t=Math.max(1000,Math.min(10000,Number(value)||3200))/100;
 const clamp=v=>Math.round(Math.max(0,Math.min(255,v)));
 const r=t<=66?255:329.698727446*Math.pow(t-60,-.1332047592);
 const g=t<=66?99.4708025861*Math.log(t)-161.1195681661:288.1221695283*Math.pow(t-60,-.0755148492);
 const b=t>=66?255:t<=19?0:138.5177312231*Math.log(t-10)-305.0447927307;
 return "rgb("+clamp(r)+","+clamp(g)+","+clamp(b)+")";
}
function profileName(state,config) {
 if(config.name)return config.name;
 return String(state?.attributes?.friendly_name||config.entity||"Circadian Pro")
  .replace(/\s+Circadian Pro$/i,"").replace(/^Circadian Pro\s+/i,"").trim();
}
export class CircadianProCard extends HTMLElement {
 constructor() {
  super();this.attachShadow({mode:"open"});this._curve=null;this._pending=null;
  this._offset=0;this._retryAfter=0;this._busy=false;this._error="";
 }
 setConfig(config) {
  if(typeof config?.entity!=="string" || !config.entity.startsWith("switch."))
   throw new Error("Choose a Circadian Pro profile switch.");
  if(config.entity!==this._config?.entity){this._curve=null;this._retryAfter=0;this._last=null;}
  this._config={...config};this._render();this._ensureCurve();
 }
 set hass(hass){this._hass=hass;this._render();this._ensureCurve();}
 connectedCallback(){
  if(!this._timer)this._timer=setInterval(()=>{this._render();this._ensureCurve();},60000);
  this._render();this._ensureCurve();
 }
 disconnectedCallback(){clearInterval(this._timer);this._timer=null;}
 getCardSize(){return 8;}
 // Avoid a fixed row count: HA Sections must allocate the card's actual
 // height, especially on phones where header and labels may wrap.
 getGridOptions(){return {columns:9,min_columns:6,rows:"auto"};}
 static getStubConfig(){return {entity:""};}
 static getConfigForm(){return {schema:[
  {name:"entity",required:true,selector:{entity:{domain:"switch",integration:"circadian_pro"}}},
  {name:"name",selector:{text:{}}},{name:"icon",selector:{icon:{}}}
 ]};}
 _now(){return (Date.now()+this._offset)/1000;}
 _ensureCurve(){
  const entity=this._config?.entity;
  if(!this.isConnected || !entity || !this._hass?.callWS || !this._hass.states?.[entity] || this._pending)return;
  if(this._curve?.entity===entity && this._now()>=this._curve.day_start && this._now()<this._curve.day_end)return;
  if(Date.now()<this._retryAfter)return;
  const request=this._hass.callWS({type:"circadian_pro/card/curve",entity_id:entity});
  this._pending=request;
  request.then(curve=>{
   if(this._config?.entity!==entity)return;
   if(!Number.isFinite(curve.day_start) || !Number.isFinite(curve.day_end) || curve.day_end<=curve.day_start)
    throw new Error("Invalid solar curve response");
   this._curve={...curve,entity};this._offset=curve.generated_at*1000-Date.now();
   this._error="";this._render();
  }).catch(err=>{
   if(this._config?.entity!==entity)return;
   this._error="Solar curve unavailable: "+(err.message||"please try again");
   this._retryAfter=Date.now()+120000;this._render();
  }).finally(()=>{if(this._pending===request)this._pending=null;});
 }
 async _toggle(){
  const entity=this._config?.entity,state=this._hass?.states?.[entity];
  if(this._busy || !["on","off"].includes(state?.state))return;
  this._busy=true;this._error="";this._render();
  try{await this._hass.callService("switch",state.state==="on"?"turn_off":"turn_on",{entity_id:entity});}
  catch(err){this._error="Unable to change adaptation: "+(err.message||"unknown error");}
  finally{this._busy=false;this._render();}
 }
 async _resume(){
  const entity=this._config?.entity,state=this._hass?.states?.[entity];
  if(this._busy || profileStatus(state?.state,state?.attributes)!=="Manual")return;
  this._busy=true;this._error="";this._render();
  try{await this._hass.callService("circadian_pro","set_manual_control",{entity_id:entity,manual_control:"false"});}
  catch(err){this._error="Unable to resume automatic control: "+(err.message||"unknown error");}
  finally{this._busy=false;this._render();}
 }
 _chart(curve,now){
  const g=curveGeometry(curve,now);
  if(!g)return '<div class="note">'+(curve?.mode && curve.mode!=="solar_elevation"?
   "Solar brightness graph available in Solar Elevation mode.":"Loading today’s solar curve…")+'</div>';
  const zone=curve.timezone;
  const label=time=>Number.isFinite(time)?
   '<line x1="'+g.x(time)+'" x2="'+g.x(time)+'" y1="9" y2="'+BOTTOM+'" stroke="var(--divider-color)" stroke-dasharray="2 4"/>':"";
  const id=this._svgId||(this._svgId="cpc"+Math.random().toString(36).slice(2));
  return '<svg viewBox="0 0 360 86" role="img" aria-label="Brightness solar curve from sunrise to sunset">'+
   '<defs><linearGradient id="'+id+'l"><stop offset="0%" stop-color="#db9952"/><stop offset="50%" stop-color="#f3d79e"/><stop offset="100%" stop-color="#db9952"/></linearGradient>'+
   '<linearGradient id="'+id+'a" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#efd18f" stop-opacity=".36"/><stop offset="100%" stop-color="#efd18f" stop-opacity=".03"/></linearGradient></defs>'+
   '<path d="'+g.path+' L'+RIGHT+' '+BOTTOM+' L'+LEFT+' '+BOTTOM+' Z" fill="url(#'+id+'a)"/>'+
   '<line x1="'+LEFT+'" x2="'+RIGHT+'" y1="'+BOTTOM+'" y2="'+BOTTOM+'" stroke="var(--divider-color)"/>'+
   label(curve.sunrise?.timestamp)+label(curve.solar_noon)+label(curve.sunset?.timestamp)+
   '<path d="'+g.path+'" fill="none" stroke="url(#'+id+'l)" stroke-width="3.4" stroke-linejoin="round" stroke-linecap="round"/>'+
   '<line x1="'+g.nowX+'" x2="'+g.nowX+'" y1="6" y2="'+BOTTOM+'" stroke="var(--primary-text-color)" opacity=".23" stroke-dasharray="3 4"/>'+
   '<circle cx="'+g.nowX+'" cy="'+g.nowY+'" r="6" fill="#e9ae48" stroke="var(--card-background-color,#fff)" stroke-width="2"/></svg>'+
   '<div class="solar-times"><span>Sunrise <b>'+clock(curve.sunrise?.timestamp,zone)+'</b></span>'+
   '<span>Noon <b>'+clock(curve.solar_noon,zone)+'</b></span>'+
   '<span>Sunset <b>'+clock(curve.sunset?.timestamp,zone)+'</b></span></div>';
 }
 _render(){
  if(!this._config || !this.shadowRoot)return;
  const entity=this._config.entity,state=this._hass?.states?.[entity],attrs=state?.attributes||{};
  const status=profileStatus(state?.state,attrs),on=state?.state==="on";
  let brightness=on && Number.isFinite(attrs.brightness_pct)?attrs.brightness_pct:
   Number.isFinite(attrs.last_target_brightness_pct)?attrs.last_target_brightness_pct:this._last?.brightness;
  let kelvin=on && Number.isFinite(attrs.color_temp_kelvin)?attrs.color_temp_kelvin:
   Number.isFinite(attrs.last_target_color_temp_kelvin)?attrs.last_target_color_temp_kelvin:this._last?.kelvin;
  if(on && Number.isFinite(brightness) && Number.isFinite(kelvin))this._last={brightness,kelvin};
  const curve=this._curve?.entity===entity?this._curve:null;
  const lightState=lightGroupStatus(curve?.light_entity_ids,this._hass?.states);
  const lightLabel=lightState==="on"?"Lights on":lightState==="off"?"Lights off":"Light status unavailable";
  const name=escapeHtml(profileName(state,this._config));
  const icon=escapeHtml(this._config.icon||
    (lightState==="on"?"mdi:lightbulb-group":"mdi:lightbulb-group-outline"));
  const brightnessText=Number.isFinite(brightness)?Math.round(brightness):"—";
  const kelvinText=Number.isFinite(kelvin)?Math.round(kelvin).toLocaleString():"—";
  const footer=attrs.sleep_active===true ||
   (curve?.sleep_entity_id && this._hass?.states?.[curve.sleep_entity_id]?.state==="on")?
   "Sleep mode":(MODES[curve?.mode]||"Circadian Pro");
  const now=this._now();
  this.shadowRoot.innerHTML=
   '<style>'+CSS+'</style><ha-card><div class="main">'+
    '<div class="head"><div class="identity"><div class="icon '+(lightState==="on"?"lit":lightState==="off"?"dark":"unknown")+
      '" role="img" aria-label="'+lightLabel+'" title="'+lightLabel+'"><ha-icon icon="'+icon+'"></ha-icon></div>'+
     '<div style="min-width:0"><div class="name">'+name+'</div><div class="subname">Circadian Pro</div></div></div>'+
     '<div class="actions"><span class="pill '+status.toLowerCase()+'">'+status+'</span>'+
     '<button class="toggle" type="button" role="switch" aria-checked="'+on+'" aria-label="'+(on?"Pause":"Resume")+' circadian adaptation" title="'+(on?"Pause":"Resume")+' adaptation"'+
      (!["on","off"].includes(state?.state)||this._busy?' disabled':'')+'><span class="knob"></span></button></div></div>'+
    '<div class="numbers"><div class="metric"><div class="metric-label">Target brightness</div><div class="metric-value">'+
     brightnessText+'<span class="unit">'+(Number.isFinite(brightness)?"%":"")+'</span></div></div>'+
     '<div class="metric"><div class="metric-label">Target colour</div><div class="metric-value">'+
     (Number.isFinite(kelvin)?'<i class="swatch" style="background:'+kelvinColour(kelvin)+'"></i>':"")+
     kelvinText+'<span class="unit">'+(Number.isFinite(kelvin)?"K":"")+'</span></div></div></div>'+
    '<div class="curve"><div class="curve-heading"><span class="curve-title">Solar progression</span>'+
     '<span class="curve-now">'+(curve?"Now · "+clock(now,curve.timezone):"")+'</span></div>'+
      this._chart(curve,now)+'</div><hr class="divider"/>'+
    '<div class="bottom"><span class="mode"><ha-icon icon="mdi:weather-sunny"></ha-icon>'+escapeHtml(footer)+'</span>'+
     (status==="Manual"?'<button class="resume" type="button"'+(this._busy?' disabled':'')+'>Resume automatic</button>':"")+'</div>'+
    (this._error?'<div class="error" role="alert">'+escapeHtml(this._error)+'</div>':"")+
   '</div></ha-card>';
  this.shadowRoot.querySelector(".toggle")?.addEventListener("click",()=>this._toggle());
  this.shadowRoot.querySelector(".resume")?.addEventListener("click",()=>this._resume());
 }
}
if(!customElements.get(TYPE))customElements.define(TYPE,CircadianProCard);
if(typeof window!=="undefined"){
 window.customCards=window.customCards||[];
 if(!window.customCards.some(c=>c.type===TYPE))window.customCards.push({
  type:TYPE,name:"Circadian Pro",preview:false,
  description:"Live solar progression, lighting targets and adaptation control.",
  documentationURL:"https://github.com/simontuckwell/Circadian-Pro",
  getEntitySuggestion:(hass,entityId)=>{
   if(!entityId.startsWith("switch.circadian_pro_") ||
    !Object.hasOwn(hass.states?.[entityId]?.attributes||{},"sun_position"))return null;
   return {config:{type:"custom:circadian-pro-card",entity:entityId}};
  }
 });
}
