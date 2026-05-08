import { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, PieChart, Pie } from "recharts";
import "leaflet/dist/leaflet.css";

const API = "http://localhost:8000/api";

const FARMER_IMAGES = [
  "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1600&q=80",
  "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=1600&q=80",
  "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=1600&q=80",
  "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=1600&q=80",
  "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=1600&q=80",
];
const BUYER_IMAGES = [
  "https://images.unsplash.com/photo-1542838132-92c53300491e?w=1600&q=80",
  "https://images.unsplash.com/photo-1488459716781-31db52582fe9?w=1600&q=80",
  "https://images.unsplash.com/photo-1519996529931-28324d5a630e?w=1600&q=80",
  "https://images.unsplash.com/photo-1550989460-0adf9ea622e2?w=1600&q=80",
];
const LANGUAGES = [
  { code: "kn", label: "ಕನ್ನಡ", name: "Kannada", speech: "kn-IN" },
  { code: "hi", label: "हिन्दी", name: "Hindi", speech: "hi-IN" },
  { code: "te", label: "తెలుగు", name: "Telugu", speech: "te-IN" },
  { code: "ta", label: "தமிழ்", name: "Tamil", speech: "ta-IN" },
  { code: "mr", label: "मराठी", name: "Marathi", speech: "mr-IN" },
  { code: "en", label: "English", name: "English", speech: "en-IN" },
];
const CROPS = ["tomato","onion","potato","brinjal","cabbage","cauliflower","beans","carrot","chilli","garlic","ginger","maize","wheat","rice","banana","mango","grapes","pomegranate"];
const DISTRICTS = ["Belagavi","Dharwad","Mysuru","Bengaluru","Hubli","Davanagere","Tumkur","Hassan","Shivamogga","Mangaluru","Vijayapura","Kalaburagi","Ballari","Bidar","Raichur","Koppal","Gadag","Haveri","Chikkamagaluru","Mandya","Udupi","Kodagu"];
const BUYER_TYPES = [
  { value: "restaurant", label: "Restaurant / Hotel" },
  { value: "trader", label: "Wholesale Trader" },
  { value: "supermarket", label: "Supermarket / Retail" },
  { value: "processor", label: "Food Processor" },
  { value: "exporter", label: "Exporter" },
];
const APMC_PRICES_FRONT = {
  tomato:18,onion:22,potato:15,brinjal:20,cabbage:12,cauliflower:25,
  beans:35,carrot:28,chilli:45,garlic:80,ginger:60,maize:20,wheat:22,
  rice:28,banana:18,mango:35,grapes:55,pomegranate:70,
};

const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800;900&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{font-family:'DM Sans',sans-serif;background:#04080f;color:#e2e8f0;-webkit-font-smoothing:antialiased}
::-webkit-scrollbar{width:3px}::-webkit-scrollbar-track{background:#04080f}::-webkit-scrollbar-thumb{background:#1e3a5f;border-radius:2px}
input,select,button{font-family:'DM Sans',sans-serif}
input[type=date]::-webkit-calendar-picker-indicator{filter:invert(0.5)}
@keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.4}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.fadeUp{animation:fadeUp 0.5s ease forwards}
.pulse{animation:pulse 1.2s ease infinite}
.spin{animation:spin 0.7s linear infinite}

/* ── Deal Lock Overlay Animations ─────────────────────── */
@keyframes dl-overlay-in{from{opacity:0}to{opacity:1}}
@keyframes dl-radar-spin{to{transform:rotate(360deg)}}
@keyframes dl-sonar-ring{0%{transform:scale(0.3);opacity:0.8;border-width:3px}100%{transform:scale(2.5);opacity:0;border-width:1px}}
@keyframes dl-sonar-ring-2{0%{transform:scale(0.3);opacity:0.6;border-width:2px}100%{transform:scale(3);opacity:0;border-width:0.5px}}
@keyframes dl-pulse-glow{0%,100%{box-shadow:0 0 20px rgba(74,222,128,0.2),0 0 60px rgba(74,222,128,0.1)}50%{box-shadow:0 0 40px rgba(74,222,128,0.5),0 0 100px rgba(74,222,128,0.2)}}
@keyframes dl-text-pulse{0%,100%{opacity:1}50%{opacity:0.5}}
@keyframes dl-dash-march{to{stroke-dashoffset:-20}}
@keyframes dl-node-pop{0%{transform:scale(0);opacity:0}60%{transform:scale(1.15)}100%{transform:scale(1);opacity:1}}
@keyframes dl-line-draw{from{stroke-dasharray:0,1000}to{stroke-dasharray:1000,0}}
@keyframes dl-burst-ring{0%{transform:scale(0);opacity:1;border-width:6px}50%{opacity:0.6}100%{transform:scale(4);opacity:0;border-width:1px}}
@keyframes dl-burst-ring-2{0%{transform:scale(0);opacity:0.8;border-width:4px}50%{opacity:0.4}100%{transform:scale(5.5);opacity:0;border-width:0.5px}}
@keyframes dl-checkmark-draw{0%{stroke-dashoffset:60}100%{stroke-dashoffset:0}}
@keyframes dl-card-up{0%{opacity:0;transform:translateY(30px) scale(0.95)}100%{opacity:1;transform:translateY(0) scale(1)}}
@keyframes dl-shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}
@keyframes dl-confetti-fall{0%{transform:translateY(-10px) rotate(0deg);opacity:1}100%{transform:translateY(80px) rotate(720deg);opacity:0}}
@keyframes dl-scale-pop{0%{transform:scale(0.5);opacity:0}70%{transform:scale(1.1)}100%{transform:scale(1);opacity:1}}
@keyframes dl-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}

/* ── Negotiation Stepper ─────────────────────────── */
@keyframes step-fill{from{width:0}to{width:100%}}
@keyframes step-pop{0%{transform:scale(0.5);opacity:0}70%{transform:scale(1.15)}100%{transform:scale(1);opacity:1}}
@keyframes price-slide{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:translateX(0)}}
@keyframes optimistic-pulse{0%,100%{opacity:1}50%{opacity:0.6}}
`;

function useSlideshow(images, ms = 5000) {
  const [i, setI] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setI(x => (x + 1) % images.length), ms);
    return () => clearInterval(t);
  }, [images.length, ms]);
  return images[i];
}

const WORD_NUMBERS = {
  "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
  "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
  "शून्य": "0", "एक": "1", "दो": "2", "तीन": "3", "चार": "4",
  "पांच": "5", "छह": "6", "सात": "7", "आठ": "8", "नौ": "9",
  "ಸೊನ್ನೆ": "0", "ಒಂದು": "1", "ಎರಡು": "2", "ಮೂರು": "3", "ನಾಲ್ಕು": "4",
  "ಐದು": "5", "ಆರು": "6", "ಏಳು": "7", "ಎಂಟು": "8", "ಒಂಬತ್ತು": "9"
};

const parseVoiceDigits = (text) => {
  if (!text) return "";
  let s = text.toLowerCase();
  for (const [w, d] of Object.entries(WORD_NUMBERS)) {
    s = s.replaceAll(w, d);
  }
  return s.replace(/\D/g, "");
};

function useVoice() {
  const [listening, setListening] = useState(false);
  const ref = useRef(null);
  const listen = useCallback((speechCode, onResult) => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { alert("Voice input requires Chrome browser."); return; }
    const r = new SR();
    r.lang = speechCode; r.continuous = false; r.interimResults = false;
    r.onstart = () => setListening(true);
    r.onresult = (e) => { onResult(e.results[0][0].transcript); };
    r.onend = () => setListening(false);
    r.onerror = () => setListening(false);
    ref.current = r; r.start();
  }, []);
  const stop = () => { ref.current?.stop(); setListening(false); };
  return { listening, listen, stop };
}

const haversine = (lat1, lng1, lat2, lng2) => {
  const R = 6371, dLat = (lat2-lat1)*Math.PI/180, dLng = (lng2-lng1)*Math.PI/180;
  const a = Math.sin(dLat/2)**2 + Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.sin(dLng/2)**2;
  return +(R*2*Math.asin(Math.sqrt(a))).toFixed(1);
};
const riColor = (s) => s>=70?"#4ade80":s>=40?"#fbbf24":"#f87171";
const riskColor = (r) => r==="low"?"#4ade80":r==="medium"?"#fbbf24":"#f87171";

function Toast({ t }) {
  if (!t) return null;
  return <div style={{ position:"fixed",top:20,right:20,zIndex:9999,background:t.type==="error"?"rgba(120,20,20,0.97)":"rgba(15,70,35,0.97)",border:`1px solid ${t.type==="error"?"#ef4444":"#22c55e"}`,color:"#fff",padding:"14px 22px",borderRadius:12,fontSize:14,fontWeight:500,backdropFilter:"blur(24px)",boxShadow:"0 24px 64px rgba(0,0,0,0.6)",maxWidth:360,lineHeight:1.5 }}>{t.type==="error"?"⚠ ":"✓ "}{t.msg}</div>;
}
function Spinner() { return <span className="spin" style={{ display:"inline-block",width:16,height:16,border:"2px solid rgba(255,255,255,0.2)",borderTopColor:"#fff",borderRadius:"50%" }} />; }
function Badge({ color="#94a3b8", children }) { return <span style={{ background:color+"18",border:`1px solid ${color}35`,color,padding:"3px 11px",borderRadius:20,fontSize:12,fontWeight:600,whiteSpace:"nowrap" }}>{children}</span>; }
function LockedBadge() { return <span style={{ background:"rgba(34,197,94,0.12)",border:"1px solid rgba(34,197,94,0.4)",color:"#4ade80",padding:"4px 14px",borderRadius:20,fontSize:12,fontWeight:800,letterSpacing:"1.2px",whiteSpace:"nowrap",textTransform:"uppercase",boxShadow:"0 0 12px rgba(34,197,94,0.15)",display:"inline-flex",alignItems:"center",gap:5 }}>🔒 LOCKED</span>; }
function Card({ children, accent, onClick, style={} }) { return <div onClick={onClick} style={{ background:"rgba(255,255,255,0.025)",border:`1px solid ${accent?accent+"28":"rgba(255,255,255,0.07)"}`,borderRadius:16,padding:24,...style }}>{children}</div>; }
function Label({ children }) { return <label style={{ display:"block",color:"#64748b",fontSize:11,fontWeight:700,letterSpacing:"0.8px",textTransform:"uppercase",marginBottom:8 }}>{children}</label>; }

function TextInput({ label, value, onChange, placeholder, type="text", onVoice, onBlur }) {
  return (
    <div>
      {label && <Label>{label}</Label>}
      <div style={{ display:"flex",gap:8 }}>
        <input type={type} value={value} onChange={e=>onChange(e.target.value)} placeholder={placeholder}
          style={{ flex:1,background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.09)",color:"#e2e8f0",padding:"11px 15px",borderRadius:10,fontSize:15,outline:"none" }}
          onFocus={e=>e.target.style.borderColor="rgba(34,197,94,0.5)"}
          onBlur={e=>{e.target.style.borderColor="rgba(255,255,255,0.09)"; if(onBlur) onBlur(e);}} />
        {onVoice && (
          <button onClick={onVoice.onClick} style={{ padding:"11px 14px",background:onVoice.listening?"rgba(239,68,68,0.12)":"rgba(34,197,94,0.08)",border:`1px solid ${onVoice.listening?"rgba(239,68,68,0.3)":"rgba(34,197,94,0.25)"}`,color:onVoice.listening?"#f87171":"#4ade80",borderRadius:10,cursor:"pointer",fontSize:16,display:"flex",alignItems:"center" }}>
            <span className={onVoice.listening?"pulse":""}>{onVoice.listening?"⏹":"🎤"}</span>
          </button>
        )}
      </div>
    </div>
  );
}
function SelectInput({ label, value, onChange, options }) {
  return (
    <div>
      {label && <Label>{label}</Label>}
      <select value={value} onChange={e=>onChange(e.target.value)} style={{ width:"100%",background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.09)",color:"#e2e8f0",padding:"11px 15px",borderRadius:10,fontSize:15,outline:"none" }}>
        {options.map(o=><option key={o.value??o} value={o.value??o} style={{ background:"#0a1628" }}>{o.label??(o.charAt(0).toUpperCase()+o.slice(1))}</option>)}
      </select>
    </div>
  );
}
function Btn({ children, onClick, variant="green", disabled, full, style:s={} }) {
  const v = {
    green:{ background:"linear-gradient(135deg,#16a34a,#15803d)",color:"#fff",border:"none",boxShadow:"0 4px 18px rgba(22,163,74,0.28)" },
    blue:{ background:"linear-gradient(135deg,#1d4ed8,#1e40af)",color:"#fff",border:"none",boxShadow:"0 4px 18px rgba(29,78,216,0.28)" },
    ghost:{ background:"rgba(255,255,255,0.04)",color:"#94a3b8",border:"1px solid rgba(255,255,255,0.09)" },
    red:{ background:"rgba(239,68,68,0.1)",color:"#f87171",border:"1px solid rgba(239,68,68,0.25)" },
  };
  return <button onClick={onClick} disabled={disabled} style={{ ...v[variant],padding:"11px 22px",borderRadius:10,fontWeight:600,fontSize:14,cursor:disabled?"not-allowed":"pointer",opacity:disabled?0.5:1,width:full?"100%":undefined,display:"inline-flex",alignItems:"center",justifyContent:"center",gap:8,transition:"opacity 0.2s",...s }}>{children}</button>;
}

export default function App() {
  const [portal, setPortal] = useState(null);
  const [toast, setToast] = useState(null);
  const farmerBg = useSlideshow(FARMER_IMAGES);
  const buyerBg = useSlideshow(BUYER_IMAGES);
  const showToast = (msg, type="success") => { setToast({ msg, type }); setTimeout(()=>setToast(null), 3500); };
  return (
    <>
      <style>{CSS}</style>
      <Toast t={toast} />
      {!portal
        ? <Landing onSelect={setPortal} farmerBg={farmerBg} buyerBg={buyerBg} />
        : portal==="farmer"
          ? <FarmerPortal toast={showToast} bg={farmerBg} onBack={()=>setPortal(null)} />
          : <BuyerPortal toast={showToast} bg={buyerBg} onBack={()=>setPortal(null)} />
      }
    </>
  );
}

function Landing({ onSelect, farmerBg, buyerBg }) {
  const [hovered, setHovered] = useState(null);
  const bg = hovered==="farmer"?farmerBg:hovered==="buyer"?buyerBg:farmerBg;
  
  return (
    <div style={{ minHeight:"100vh",position:"relative",overflow:"hidden",display:"flex",alignItems:"center",justifyContent:"center" }}>
      {/* Dynamic Background */}
      <div style={{ position:"absolute",inset:0,backgroundImage:`url(${bg})`,backgroundSize:"cover",backgroundPosition:"center",filter:"brightness(0.12) blur(6px)",transition:"background-image 1.2s ease" }} />
      <div style={{ position:"absolute",inset:0,background:"linear-gradient(160deg,rgba(4,8,15,0.6) 0%,rgba(4,8,15,0.9) 100%)" }} />
      
      <div className="fadeUp" style={{ position:"relative",zIndex:1,width:"100%",maxWidth:1200,padding:"80px 24px",textAlign:"center" }}>
        
        {/* Hero Section */}
        <div style={{ marginBottom:64 }}>
          <div style={{ display:"inline-flex",alignItems:"center",gap:8,background:"rgba(74,222,128,0.1)",border:"1px solid rgba(74,222,128,0.3)",color:"#4ade80",padding:"6px 16px",borderRadius:100,fontSize:13,fontWeight:700,marginBottom:24,letterSpacing:"0.5px" }}>
             🌾 Built for Indian Farmers
          </div>
          <div style={{ fontFamily:"'Syne',sans-serif",fontSize:"clamp(36px,6vw,72px)",fontWeight:900,letterSpacing:"-3px",lineHeight:0.95,color:"#fff" }}>
            <div>Know Your Farm.</div>
            <div>Know Your Price.</div>
            <div style={{ color:"#4ade80" }}>Know Your Profit.</div>
          </div>
          <p style={{ color:"#94a3b8",fontSize:"clamp(16px,2vw,19px)",marginTop:32,maxWidth:800,margin:"32px auto 0",lineHeight:1.6 }}>
            India's first AI-powered agricultural supply chain — connecting Karnataka farmers directly to buyers, eliminating middlemen, maximizing profit.
          </p>
        </div>

        {/* Stats Bar */}
        <div style={{ display:"flex",justifyContent:"center",gap:"40px 60px",flexWrap:"wrap",marginBottom:64,padding:"32px 0",borderTop:"1px solid rgba(255,255,255,0.06)",borderBottom:"1px solid rgba(255,255,255,0.06)" }}>
          {[["40+", "Farmers Registered"], ["8", "Karnataka Districts"], ["15+", "Verified Buyers"], ["Gemini AI", "Intelligence Powered"]].map(([val, label]) => (
            <div key={label} style={{ textAlign:"center" }}>
              <div style={{ fontFamily:"'Syne',sans-serif",fontSize:32,fontWeight:900,color:"#4ade80",lineHeight:1 }}>{val}</div>
              <div style={{ color:"#64748b",fontSize:12,textTransform:"uppercase",letterSpacing:"1px",marginTop:8,fontWeight:600 }}>{label}</div>
            </div>
          ))}
        </div>

        {/* Feature Cards */}
        <div style={{ display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(320px,1fr))",gap:24,marginBottom:64 }}>
          {[
            { icon:"🧠", title:"AI Harvest Intelligence", sub:"Weather-aware crop analysis powered by Gemini AI", detail:"Tells you exactly when to harvest based on rain forecasts and market timing.", color:"#4ade80" },
            { icon:"📍", title:"GPS Buyer Matching", sub:"Find the best buyer near you, net profit calculated", detail:"Calculates real net profit after transport cost, not just gross mandi price.", color:"#38bdf8" },
            { icon:"🤝", title:"Fair Deal Negotiation", sub:"Bargain, lock, and track every deal transparently.", detail:"Counter-offer, accept, reject — full bargaining with deal history timeline.", color:"#818cf8" }
          ].map((f, i) => (
            <div key={i} style={{ background:"rgba(255,255,255,0.025)",backdropFilter:"blur(12px)",border:"1px solid rgba(255,255,255,0.08)",borderRadius:24,padding:"40px 32px",textAlign:"left",transition:"all 0.3s" }}>
              <div style={{ fontSize:40,marginBottom:20 }}>{f.icon}</div>
              <div style={{ fontFamily:"'Syne',sans-serif",fontSize:20,fontWeight:800,color:f.color,marginBottom:10 }}>{f.title}</div>
              <div style={{ color:"#e2e8f0",fontSize:15,lineHeight:1.5,marginBottom:12,fontWeight:500 }}>{f.sub}</div>
              <div style={{ color:"#64748b",fontSize:14,lineHeight:1.5,borderTop:"1px solid rgba(255,255,255,0.05)",paddingTop:12 }}>{f.detail}</div>
            </div>
          ))}
        </div>

        {/* How It Works Section */}
        <div style={{ marginBottom:80,padding:"40px 24px",background:"rgba(74,222,128,0.03)",borderRadius:32,border:"1px solid rgba(74,222,128,0.1)" }}>
          <div style={{ fontFamily:"'Syne',sans-serif",fontSize:22,fontWeight:800,color:"#e2e8f0",marginBottom:32 }}>How KhetIQ Works — In 4 Steps</div>
          <div style={{ display:"flex",justifyContent:"center",alignItems:"center",gap:20,flexWrap:"wrap" }}>
            {[
              "1️⃣ Register with GPS", "2️⃣ Add Your Crop", "3️⃣ Get AI Analysis", "4️⃣ Lock Best Deal"
            ].map((step, i) => (
              <div key={step} style={{ display:"flex", alignItems:"center", gap:20 }}>
                <div style={{ background:"rgba(255,255,255,0.04)",padding:"16px 24px",borderRadius:16,color:"#e2e8f0",fontWeight:600,fontSize:15 }}>{step}</div>
                {i < 3 && <span style={{ color:"#475569",fontSize:20 }}>→</span>}
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display:"flex",gap:24,flexWrap:"wrap",justifyContent:"center",marginBottom:64 }}>
          <div style={{ textAlign:"center" }}>
            <button 
              onMouseEnter={()=>setHovered("farmer")} onMouseLeave={()=>setHovered(null)}
              onClick={()=>onSelect("farmer")}
              style={{ background:"linear-gradient(135deg,#16a34a,#15803d)",color:"#fff",border:"none",padding:"24px 48px",borderRadius:20,fontSize:20,fontWeight:800,cursor:"pointer",fontFamily:"'Syne',sans-serif",boxShadow:"0 15px 35px rgba(22,163,74,0.3)",transition:"all 0.2s" }}
            >I'm a Farmer — Login / Register</button>
            <div style={{ color:"#64748b",fontSize:13,marginTop:14,fontWeight:500 }}>Register free, get AI advice instantly</div>
          </div>
          
          <div style={{ textAlign:"center" }}>
            <button 
              onMouseEnter={()=>setHovered("buyer")} onMouseLeave={()=>setHovered(null)}
              onClick={()=>onSelect("buyer")}
              style={{ background:"linear-gradient(135deg,#1d4ed8,#1e40af)",color:"#fff",border:"none",padding:"24px 48px",borderRadius:20,fontSize:20,fontWeight:800,cursor:"pointer",fontFamily:"'Syne',sans-serif",boxShadow:"0 15px 35px rgba(29,78,216,0.3)",transition:"all 0.2s" }}
            >I'm a Buyer — Login / Register</button>
            <div style={{ color:"#64748b",fontSize:13,marginTop:14,fontWeight:500 }}>Browse crops, make offers, grow your supply chain.</div>
          </div>
        </div>

        {/* Footer Text */}
        <div style={{ color:"#475569",fontSize:13,lineHeight:1.6,maxWidth:700,margin:"0 auto",fontWeight:500 }}>
          KhetIQ — Empowering Karnataka's 1.2 Crore farmers with AI intelligence | <br />
          Built with FastAPI, React, Google Gemini & Open-Meteo
        </div>
      </div>
    </div>
  );
}

// ── Deal Lock Overlay ──────────────────────────────────────────────────────────

function DealLockOverlay({ data, onDismiss }) {
  const [stage, setStage] = useState(1);
  const dismissTimerRef = useRef(null);

  useEffect(() => {
    const t1 = setTimeout(() => setStage(2), 2000);
    const t2 = setTimeout(() => setStage(3), 4200);
    const t3 = setTimeout(() => {
      onDismiss();
    }, 7200);
    dismissTimerRef.current = t3;
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); };
  }, []);

  const handleTap = () => {
    if (stage === 3) {
      if (dismissTimerRef.current) clearTimeout(dismissTimerRef.current);
      onDismiss();
    }
  };

  const confettiColors = ["#4ade80","#22d3ee","#fbbf24","#818cf8","#f472b6","#fb923c"];

  return (
    <div onClick={handleTap} style={{
      position:"fixed", inset:0, zIndex:9999,
      background:"rgba(4,8,15,0.96)",
      backdropFilter:"blur(30px)",
      display:"flex", alignItems:"center", justifyContent:"center",
      flexDirection:"column",
      animation:"dl-overlay-in 0.4s ease",
      cursor: stage===3 ? "pointer" : "default",
    }}>

      {/* ── Stage 1: Finding Buyer ────────────────── */}
      {stage === 1 && (
        <div style={{ display:"flex", flexDirection:"column", alignItems:"center", gap:32, animation:"dl-scale-pop 0.5s ease" }}>
          {/* Radar / Sonar Container */}
          <div style={{ position:"relative", width:160, height:160, display:"flex", alignItems:"center", justifyContent:"center" }}>
            {/* Sonar rings */}
            {[0,1,2].map(i => (
              <div key={i} style={{
                position:"absolute", width:80, height:80, borderRadius:"50%",
                border:"2px solid rgba(74,222,128,0.4)",
                animation:`dl-sonar-ring 2s ease-out ${i*0.6}s infinite`,
              }} />
            ))}
            {[0,1].map(i => (
              <div key={`s2-${i}`} style={{
                position:"absolute", width:80, height:80, borderRadius:"50%",
                border:"1.5px solid rgba(34,211,238,0.3)",
                animation:`dl-sonar-ring-2 2.4s ease-out ${i*0.8+0.3}s infinite`,
              }} />
            ))}
            {/* Center radar dot */}
            <div style={{
              width:56, height:56, borderRadius:"50%",
              background:"linear-gradient(135deg,#16a34a,#0891b2)",
              display:"flex", alignItems:"center", justifyContent:"center",
              animation:"dl-pulse-glow 1.5s ease infinite",
              boxShadow:"0 0 40px rgba(74,222,128,0.3)",
              zIndex:2,
            }}>
              {/* Radar sweep */}
              <div style={{
                width:48, height:48, borderRadius:"50%",
                background:"conic-gradient(from 0deg, transparent 0deg, rgba(74,222,128,0.4) 60deg, transparent 120deg)",
                animation:"dl-radar-spin 1.5s linear infinite",
              }} />
            </div>
            {/* Scanning dots */}
            {[0,1,2,3,4,5].map(i => (
              <div key={`dot-${i}`} style={{
                position:"absolute",
                width:6, height:6, borderRadius:"50%",
                background: i%2===0 ? "#4ade80" : "#22d3ee",
                opacity: 0.6,
                left: `${50 + 35*Math.cos(i*60*Math.PI/180)}%`,
                top: `${50 + 35*Math.sin(i*60*Math.PI/180)}%`,
                animation:`pulse 1s ease ${i*0.2}s infinite`,
              }} />
            ))}
          </div>
          <div style={{ textAlign:"center" }}>
            <div style={{
              fontFamily:"'Syne',sans-serif", fontSize:28, fontWeight:800,
              background:"linear-gradient(135deg,#4ade80,#22d3ee)",
              WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent",
              animation:"dl-text-pulse 1.2s ease infinite",
            }}>Finding Buyer…</div>
            <div style={{ color:"#475569", fontSize:14, marginTop:10 }}>Scanning nearby verified buyers</div>
          </div>
        </div>
      )}

      {/* ── Stage 2: Connecting ────────────────── */}
      {stage === 2 && (
        <div style={{ display:"flex", flexDirection:"column", alignItems:"center", gap:24, animation:"dl-scale-pop 0.4s ease" }}>
          <div style={{
            fontFamily:"'Syne',sans-serif", fontSize:22, fontWeight:700,
            color:"#22d3ee", marginBottom:8,
            animation:"dl-text-pulse 1s ease infinite",
          }}>Connecting…</div>
          {/* Two nodes with dashed line */}
          <div style={{ display:"flex", alignItems:"center", gap:0, position:"relative", width:360 }}>
            {/* Farmer Node */}
            <div style={{
              display:"flex", flexDirection:"column", alignItems:"center", gap:10,
              animation:"dl-node-pop 0.6s ease forwards",
              zIndex:2,
            }}>
              <div style={{
                width:72, height:72, borderRadius:"50%",
                background:"linear-gradient(135deg,#16a34a,#15803d)",
                display:"flex", alignItems:"center", justifyContent:"center",
                boxShadow:"0 0 24px rgba(74,222,128,0.3), 0 8px 32px rgba(0,0,0,0.4)",
                border:"3px solid rgba(74,222,128,0.3)",
              }}>
                <span style={{ fontSize:28 }}>🌾</span>
              </div>
              <div style={{
                fontFamily:"'Syne',sans-serif", fontSize:14, fontWeight:700,
                color:"#4ade80", textTransform:"capitalize", textAlign:"center", maxWidth:100,
              }}>{data.cropName}</div>
            </div>

            {/* Animated SVG Connection Line */}
            <svg width="200" height="60" viewBox="0 0 200 60" style={{ margin:"0 -6px", marginTop:-20 }}>
              {/* Dashed marching line */}
              <line x1="10" y1="30" x2="190" y2="30"
                stroke="url(#dl-line-grad)" strokeWidth="2.5"
                strokeDasharray="8,6"
                style={{ animation:"dl-dash-march 0.6s linear infinite" }}
              />
              {/* Glow line underneath */}
              <line x1="10" y1="30" x2="190" y2="30"
                stroke="rgba(34,211,238,0.15)" strokeWidth="8"
                strokeDasharray="8,6"
                style={{ animation:"dl-dash-march 0.6s linear infinite", filter:"blur(3px)" }}
              />
              {/* Moving dot */}
              <circle r="5" fill="#22d3ee" style={{ filter:"drop-shadow(0 0 6px rgba(34,211,238,0.6))" }}>
                <animateMotion dur="1.5s" repeatCount="indefinite" path="M10,30 L190,30" />
              </circle>
              <circle r="3" fill="#4ade80" style={{ filter:"drop-shadow(0 0 4px rgba(74,222,128,0.6))" }}>
                <animateMotion dur="1.5s" repeatCount="indefinite" begin="0.5s" path="M10,30 L190,30" />
              </circle>
              <defs>
                <linearGradient id="dl-line-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#4ade80" />
                  <stop offset="50%" stopColor="#22d3ee" />
                  <stop offset="100%" stopColor="#818cf8" />
                </linearGradient>
              </defs>
            </svg>

            {/* Buyer Node */}
            <div style={{
              display:"flex", flexDirection:"column", alignItems:"center", gap:10,
              animation:"dl-node-pop 0.6s ease 0.3s forwards",
              opacity:0, zIndex:2,
            }}>
              <div style={{
                width:72, height:72, borderRadius:"50%",
                background:"linear-gradient(135deg,#0891b2,#6366f1)",
                display:"flex", alignItems:"center", justifyContent:"center",
                boxShadow:"0 0 24px rgba(56,189,248,0.3), 0 8px 32px rgba(0,0,0,0.4)",
                border:"3px solid rgba(56,189,248,0.3)",
              }}>
                <span style={{ fontSize:28 }}>🏪</span>
              </div>
              <div style={{
                fontFamily:"'Syne',sans-serif", fontSize:14, fontWeight:700,
                color:"#38bdf8", textAlign:"center", maxWidth:100,
              }}>{data.buyerName}</div>
            </div>
          </div>
        </div>
      )}

      {/* ── Stage 3: Deal Locked! ────────────────── */}
      {stage === 3 && (
        <div style={{ display:"flex", flexDirection:"column", alignItems:"center", gap:24, position:"relative" }}>
          {/* Confetti particles */}
          {Array.from({length:18}).map((_,i) => (
            <div key={`conf-${i}`} style={{
              position:"absolute",
              width: 6 + Math.random()*6,
              height: 6 + Math.random()*6,
              borderRadius: Math.random()>0.5 ? "50%" : "2px",
              background: confettiColors[i % confettiColors.length],
              left: `${10 + Math.random()*80}%`,
              top: `${-10 + Math.random()*20}%`,
              animation:`dl-confetti-fall ${1.5+Math.random()*1.5}s ease ${Math.random()*0.5}s forwards`,
              opacity:0.8,
            }} />
          ))}

          {/* Green burst rings */}
          <div style={{ position:"relative", width:120, height:120, display:"flex", alignItems:"center", justifyContent:"center" }}>
            <div style={{
              position:"absolute", width:60, height:60, borderRadius:"50%",
              border:"4px solid rgba(74,222,128,0.5)",
              animation:"dl-burst-ring 1s ease-out forwards",
            }} />
            <div style={{
              position:"absolute", width:60, height:60, borderRadius:"50%",
              border:"3px solid rgba(34,211,238,0.4)",
              animation:"dl-burst-ring-2 1.2s ease-out 0.15s forwards",
            }} />
            {/* Checkmark circle */}
            <div style={{
              width:80, height:80, borderRadius:"50%",
              background:"linear-gradient(135deg,#16a34a,#15803d)",
              display:"flex", alignItems:"center", justifyContent:"center",
              boxShadow:"0 0 50px rgba(74,222,128,0.4), 0 0 100px rgba(74,222,128,0.15)",
              animation:"dl-scale-pop 0.5s ease",
              zIndex:2,
            }}>
              <svg width="36" height="36" viewBox="0 0 36 36">
                <path d="M8 18 L15 25 L28 11" fill="none" stroke="#fff" strokeWidth="3.5"
                  strokeLinecap="round" strokeLinejoin="round"
                  strokeDasharray="60" strokeDashoffset="60"
                  style={{ animation:"dl-checkmark-draw 0.6s ease 0.3s forwards" }}
                />
              </svg>
            </div>
          </div>

          {/* Deal Locked Text */}
          <div style={{
            fontFamily:"'Syne',sans-serif", fontSize:36, fontWeight:900,
            background:"linear-gradient(135deg,#4ade80 0%,#22d3ee 50%,#818cf8 100%)",
            WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent",
            animation:"dl-scale-pop 0.4s ease 0.2s both",
            letterSpacing:"-1px",
          }}>Deal Locked! ✅</div>

          {/* Deal Summary Card */}
          <div style={{
            background:"rgba(255,255,255,0.03)",
            border:"1px solid rgba(74,222,128,0.2)",
            borderRadius:20, padding:"28px 36px",
            width:"100%", maxWidth:400,
            animation:"dl-card-up 0.6s ease 0.4s both",
            position:"relative", overflow:"hidden",
          }}>
            {/* Shimmer effect */}
            <div style={{
              position:"absolute", inset:0,
              background:"linear-gradient(90deg,transparent 0%,rgba(74,222,128,0.03) 50%,transparent 100%)",
              backgroundSize:"200% 100%",
              animation:"dl-shimmer 2s ease infinite",
              pointerEvents:"none",
            }} />
            {/* Top accent line */}
            <div style={{
              position:"absolute", top:0, left:0, right:0, height:3,
              background:"linear-gradient(90deg,#16a34a,#0891b2,#6366f1)",
              borderRadius:"20px 20px 0 0",
            }} />

            <div style={{
              display:"grid", gridTemplateColumns:"1fr 1fr", gap:"18px 24px",
              position:"relative", zIndex:1,
            }}>
              {[
                ["Crop", data.cropName, "capitalize"],
                ["Buyer", data.buyerName, "normal"],
                ["Quantity", `${data.quantity} kg`, "normal"],
                ["Price", `₹${data.pricePerKg}/kg`, "normal"],
                ["Total Value", `₹${data.totalValue?.toLocaleString()}`, "normal"],
                ["Expected Pickup", data.expectedPickup, "normal"],
              ].map(([label, value, transform], i) => (
                <div key={label} style={{ animation:`dl-scale-pop 0.3s ease ${0.5 + i*0.08}s both` }}>
                  <div style={{
                    color:"#475569", fontSize:11, letterSpacing:"0.8px",
                    textTransform:"uppercase", marginBottom:4,
                  }}>{label}</div>
                  <div style={{
                    fontWeight:700, fontSize:16, color:
                      label==="Total Value" ? "#4ade80" :
                      label==="Price" ? "#fbbf24" :
                      label==="Buyer" ? "#38bdf8" : "#e2e8f0",
                    textTransform: transform,
                    fontFamily: label==="Total Value" ? "'Syne',sans-serif" : "inherit",
                  }}>{value}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Tap to dismiss hint */}
          <div style={{
            color:"#475569", fontSize:13, marginTop:8,
            animation:"dl-scale-pop 0.3s ease 1s both",
          }}>Tap anywhere to dismiss</div>
        </div>
      )}
    </div>
  );
}

// ── Farmer Portal ─────────────────────────────────────────────────────────────

function FarmerPortal({ toast, bg, onBack }) {
  const [page, setPage] = useState("login");
  const [farmer, setFarmer] = useState(null);
  const [crops, setCrops] = useState([]);
  const [recommendation, setRecommendation] = useState(null);
  const [deals, setDeals] = useState([]);
  const [buyers, setBuyers] = useState([]);
  const [analyzingId, setAnalyzingId] = useState(null);
  const [lang, setLang] = useState("kn");
  const [dealLockOverlay, setDealLockOverlay] = useState(null);
  const [profileModal, setProfileModal] = useState(null);
  const [reviewModal, setReviewModal] = useState(null);

  const loadCrops = async (f) => { const r = await axios.get(`${API}/crops/farmer/${f.id}`); setCrops(r.data); };

  const login = async (phone) => {
    if (phone.length!==10) { toast("Enter valid 10-digit phone","error"); return; }
    try {
      const r = await axios.get(`${API}/farmers/`);
      const f = r.data.find(x=>x.phone===phone);
      if (!f) { toast("Not registered. Please register first.","error"); return; }
      setFarmer(f); setLang(f.language||"kn");
      await loadCrops(f); toast(`Welcome back, ${f.name}!`); setPage("dashboard");
    } catch { toast("Login failed","error"); }
  };

  const register = async (form) => {
    if (!form.name.trim()) { toast("Name required","error"); return; }
    if (form.phone.length!==10) { toast("Enter valid 10-digit phone","error"); return; }
    if (!form.location_lat) { toast("Capture your location first","error"); return; }
    try {
      const r = await axios.post(`${API}/farmers/`, { ...form, language:lang });
      setFarmer(r.data); setLang(lang);
      toast("Registration successful! Welcome to KhetIQ."); setPage("dashboard");
    } catch (e) {
      const status = e.response?.status;
      const detail = e.response?.data?.detail || "";
      if (status === 409) toast("This phone number is already registered. Please log in instead.", "error");
      else toast(detail || "Registration failed", "error");
    }
  };

  const addCrop = async (form) => {
    if (!form.quantity_kg) { toast("Enter quantity","error"); return; }
    try {
      await axios.post(`${API}/crops/`, { ...form, farmer_id:farmer.id, quantity_kg:parseFloat(form.quantity_kg), field_size_acres:parseFloat(form.field_size_acres)||null });
      await loadCrops(farmer); toast("Crop added!"); return true;
    } catch { toast("Failed to add crop","error"); return false; }
  };

  const analyze = async (cropId) => {
    setAnalyzingId(cropId);
    try {
      const r = await axios.post(`${API}/recommendations/analyze/${cropId}?lang=${lang}`);
      setRecommendation(r.data); setPage("analysis");
    } catch { toast("Analysis failed. Check backend is running.","error"); }
    setAnalyzingId(null);
  };

  const lockDeal = async () => {
    if (!recommendation?.best_buyer) return;
    try {
      const expectedDate = new Date(Date.now()+7*86400000).toISOString().split("T")[0];
      await axios.post(`${API}/deals/`, {
        farmer_id:farmer.id, buyer_id:recommendation.best_buyer.buyer_id,
        crop_type:recommendation.crop, quantity_kg:recommendation.quantity_kg,
        agreed_price_per_kg:recommendation.apmc_price_per_kg,
        transport_cost:recommendation.best_buyer.transport_cost,
        expected_delivery_date:expectedDate,
        initiated_by:"farmer", deal_status:"offer",
      });
      // Trigger the Deal Lock overlay animation
      setDealLockOverlay({
        cropName: recommendation.crop,
        buyerName: recommendation.best_buyer.name,
        quantity: recommendation.quantity_kg,
        pricePerKg: recommendation.apmc_price_per_kg,
        totalValue: recommendation.apmc_price_per_kg * recommendation.quantity_kg,
        expectedPickup: expectedDate,
      });
    } catch (e) { toast("Failed: " + JSON.stringify(e.response?.data?.detail || e.message), "error"); }
  };

  const loadDeals = async () => {
    try {
      const [r, b] = await Promise.all([
        axios.get(`${API}/deals/farmer/${farmer.id}`),
        axios.get(`${API}/buyers/`)
      ]);
      setDeals(r.data); setBuyers(b.data); setPage("deals");
    } catch { toast("Failed to load deals","error"); }
  };

  const respondToDeal = async (dealId, status, counterPrice) => {
    try {
      if (status === "accepted") {
        await axios.patch(`${API}/deals/${dealId}/accept`);
      } else if (status === "rejected") {
        await axios.patch(`${API}/deals/${dealId}/reject`);
      } else if (status === "bargaining" && counterPrice) {
        await axios.patch(`${API}/deals/${dealId}/counter`, { counter_price: counterPrice });
      } else {
        await axios.patch(`${API}/deals/${dealId}/status`, { deal_status: status, counter_price_per_kg: counterPrice || null });
      }
      toast(status==="accepted"?"Deal accepted! 🎉":status==="rejected"?"Deal rejected.":"Counter-offer sent!");
      const r = await axios.get(`${API}/deals/farmer/${farmer.id}`);
      setDeals(r.data);
    } catch { toast("Action failed","error"); }
  };

  const handleReviewSubmit = async (reviewData) => {
    try {
      await axios.post(`${API}/reviews/`, {
        deal_id: reviewData.dealId, reviewer_type: "farmer", reviewer_id: farmer.id,
        reviewee_type: "buyer", reviewee_id: reviewData.revieweeId,
        rating: reviewData.rating, comment: reviewData.comment
      });
      setReviewModal(null);
      toast("Review submitted! Thank you.");
    } catch (e) { toast("Failed to submit review", "error"); }
  };

  const Header = () => (
    <header style={{ background:"rgba(4,8,15,0.92)",backdropFilter:"blur(20px)",borderBottom:"1px solid rgba(34,197,94,0.08)",height:58,display:"flex",alignItems:"center",justifyContent:"space-between",padding:"0 28px",position:"sticky",top:0,zIndex:100 }}>
      <div style={{ display:"flex",alignItems:"center",gap:14 }}>
        <button onClick={onBack} style={{ background:"none",border:"none",color:"#475569",cursor:"pointer",fontSize:18,lineHeight:1,padding:"4px 6px" }}>←</button>
        <span style={{ fontFamily:"'Syne',sans-serif",fontWeight:900,fontSize:20,background:"linear-gradient(90deg,#4ade80,#22d3ee)",WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent" }}>KhetIQ</span>
        <Badge color="#4ade80">Farmer</Badge>
      </div>
      <div style={{ display:"flex",alignItems:"center",gap:10 }}>
        {farmer && <>
          <button onClick={()=>{ loadCrops(farmer); setPage("dashboard"); }} style={{ background:"none",border:"none",color:page==="dashboard"?"#4ade80":"#64748b",cursor:"pointer",fontSize:14,fontWeight:500 }}>Dashboard</button>
          <button onClick={loadDeals} style={{ background:"none",border:"none",color:page==="deals"?"#4ade80":"#64748b",cursor:"pointer",fontSize:14,fontWeight:500 }}>My Deals</button>
          <div style={{ width:30,height:30,borderRadius:"50%",background:"linear-gradient(135deg,#16a34a,#0e7490)",display:"flex",alignItems:"center",justifyContent:"center",fontWeight:800,fontSize:13 }}>{farmer.name[0]}</div>
        </>}
        <select value={lang} onChange={e=>setLang(e.target.value)} style={{ background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.08)",color:"#64748b",padding:"5px 10px",borderRadius:8,fontSize:13 }}>
          {LANGUAGES.map(l=><option key={l.code} value={l.code} style={{ background:"#0a1628" }}>{l.label}</option>)}
        </select>
        {farmer && <button onClick={()=>{ setFarmer(null); setCrops([]); setDeals([]); setBuyers([]); setPage("login"); onBack(); }} style={{ background:"none",border:"1px solid rgba(255,255,255,0.1)",color:"#64748b",cursor:"pointer",fontSize:13,padding:"5px 12px",borderRadius:8,display:"flex",alignItems:"center",gap:5,transition:"all 0.2s" }} onMouseEnter={e=>{e.currentTarget.style.borderColor="rgba(248,113,113,0.4)";e.currentTarget.style.color="#f87171";}} onMouseLeave={e=>{e.currentTarget.style.borderColor="rgba(255,255,255,0.1)";e.currentTarget.style.color="#64748b";}}>🚪 Logout</button>}
      </div>
    </header>
  );

  return (
    <div style={{ minHeight:"100vh",background:"#04080f" }}>
      <Header />
      {dealLockOverlay && (
        <DealLockOverlay
          data={dealLockOverlay}
          onDismiss={() => {
            setDealLockOverlay(null);
            toast("Deal locked! Track it in My Deals.");
          }}
        />
      )}
      <div className="fadeUp" style={{ maxWidth:880,margin:"0 auto",padding:"32px 20px" }}>
        {page==="login" && <FLogin onLogin={login} onRegister={()=>setPage("register")} bg={bg} lang={lang} />}
        {page==="register" && <FRegister onRegister={register} onBack={()=>setPage("login")} lang={lang} setLang={setLang} />}
        {page==="dashboard" && farmer && <FDashboard farmer={farmer} crops={crops} onAddCrop={addCrop} onAnalyze={analyze} analyzingId={analyzingId} lang={lang} />}
        {page==="analysis" && recommendation && <FAnalysis rec={recommendation} onBack={()=>setPage("dashboard")} onLockDeal={lockDeal} farmerLang={farmer?.language||"kn"} />}
        {page==="deals" && <FDeals deals={deals} buyers={buyers} onBack={()=>setPage("dashboard")} onRespond={respondToDeal} farmerId={farmer.id} onReviewOpen={setReviewModal} />}
      </div>
      {profileModal && <ProfileCardModal type={profileModal.type} id={profileModal.id} name={profileModal.name} onClose={()=>setProfileModal(null)} />}
      {reviewModal && <ReviewModal data={reviewModal} onClose={()=>setReviewModal(null)} onSubmit={handleReviewSubmit} />}
    </div>
  );
}

function FLogin({ onLogin, onRegister, bg, lang }) {
  const [phone, setPhone] = useState("");
  const { listening, listen, stop } = useVoice();
  const speechCode = LANGUAGES.find(l=>l.code===lang)?.speech||"kn-IN";
  return (
    <div style={{ minHeight:"calc(100vh - 58px)",display:"flex",alignItems:"center",justifyContent:"center",position:"relative",margin:"-32px -20px",padding:24 }}>
      <div style={{ position:"absolute",inset:0,backgroundImage:`url(${bg})`,backgroundSize:"cover",backgroundPosition:"center",filter:"brightness(0.12)" }} />
      <div style={{ position:"relative",zIndex:1,width:"100%",maxWidth:420 }}>
        <Card style={{ padding:40 }}>
          <div style={{ fontFamily:"'Syne',sans-serif",fontSize:26,fontWeight:800,marginBottom:6 }}>Farmer Login</div>
          <div style={{ color:"#475569",fontSize:14,marginBottom:32 }}>Enter your registered phone number</div>
          <div style={{ display:"grid",gap:18 }}>
            <TextInput label="Phone Number" value={phone} onChange={setPhone} placeholder="9876543210" type="tel"
              onVoice={{ listening, onClick:()=>listening?stop():listen(speechCode,v=>setPhone(parseVoiceDigits(v).slice(0,10))) }} />
            <Btn onClick={()=>onLogin(phone)} full>Login →</Btn>
            <div style={{ background:"rgba(34,197,94,0.05)", border:"1px solid rgba(34,197,94,0.15)", borderRadius:10, padding:12, marginTop:8 }}>
              <div style={{ color:"#4ade80", fontSize:11, fontWeight:700, textTransform:"uppercase", letterSpacing:"1px", marginBottom:4 }}>Demo Farmers</div>
              <div style={{ color:"#94a3b8", fontSize:12 }}>Try: 9900000000, 9900000001, 9900000021</div>
            </div>
            <div style={{ textAlign:"center",color:"#475569",fontSize:14 }}>
              New farmer? <span onClick={onRegister} style={{ color:"#4ade80",cursor:"pointer",fontWeight:600 }}>Register here</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

function FRegister({ onRegister, onBack, lang, setLang }) {
  const [form, setForm] = useState({ name:"",phone:"",district:"Belagavi",state:"Karnataka",language:"kn",location_lat:null,location_lng:null });
  const [gps, setGps] = useState("idle");
  const [gpsError, setGpsError] = useState("");
  const [activeVoice, setActiveVoice] = useState(null);
  const [phoneError, setPhoneError] = useState("");
  const [phoneChecking, setPhoneChecking] = useState(false);
  const { listening, listen, stop } = useVoice();
  const speechCode = LANGUAGES.find(l=>l.code===lang)?.speech||"kn-IN";
  const F = (k) => (v) => { setForm(f=>({ ...f,[k]:v })); if(k==="phone") setPhoneError(""); };

  const voiceFor = (field, handler) => ({
    listening: activeVoice===field,
    onClick: () => {
      if (activeVoice===field) { stop(); setActiveVoice(null); }
      else { if (listening) stop(); setActiveVoice(field); listen(speechCode,(v)=>{ handler(v); setActiveVoice(null); }); }
    },
  });

  const checkPhone = async (phone) => {
    if (phone.length !== 10) { setPhoneError(phone.length > 0 ? "Enter a valid 10-digit number" : ""); return; }
    setPhoneChecking(true);
    try {
      const r = await axios.get(`${API}/farmers/check-phone?number=${phone}`);
      if (r.data.exists) setPhoneError("duplicate");
      else setPhoneError("");
    } catch { /* silent */ }
    setPhoneChecking(false);
  };

  const captureGPS = () => {
    setGps("loading");
    setGpsError(null);
    navigator.geolocation.getCurrentPosition(
      p=>{ setForm(f=>({ ...f,location_lat:p.coords.latitude,location_lng:p.coords.longitude })); setGps("done"); },
      (err)=>{ 
        setGps("idle");
        if (err.code === 1) setGpsError(<span>Location access was denied. Please enable location in your browser settings <span style={{fontSize:14}}>⚙️</span> to find the best nearby buyers.</span>);
        else if (err.code === 2) setGpsError("Unable to detect your location. Please check your GPS or network.");
        else if (err.code === 3) setGpsError("Location request timed out. Please try again.");
        else setGpsError("An unknown error occurred while getting location.");
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const canSubmit = form.name.trim() && form.phone.length===10 && !phoneError && !phoneChecking && form.location_lat;

  return (
    <div style={{ maxWidth:540,margin:"0 auto" }}>
      <button onClick={onBack} style={{ background:"none",border:"none",color:"#475569",cursor:"pointer",fontSize:14,marginBottom:24,display:"flex",alignItems:"center",gap:6 }}>← Back to Login</button>
      <Card>
        <div style={{ fontFamily:"'Syne',sans-serif",fontSize:26,fontWeight:800,marginBottom:6 }}>Register as Farmer</div>
        <div style={{ color:"#475569",fontSize:14,marginBottom:32 }}>Join KhetIQ — speak or type your details</div>
        <div style={{ display:"grid",gap:18 }}>
          <TextInput label="Full Name" value={form.name} onChange={F("name")} placeholder="Raju Patil" onVoice={voiceFor("name",F("name"))} />
          <div>
            <TextInput label="Phone Number" value={form.phone} onChange={F("phone")} placeholder="9876543210" type="tel"
              onVoice={voiceFor("phone",v=>F("phone")(parseVoiceDigits(v).slice(0,10)))}
              onBlur={()=>checkPhone(form.phone)} />
            {phoneChecking && <div style={{ fontSize:12,color:"#64748b",marginTop:6,display:"flex",alignItems:"center",gap:6 }}><Spinner /> Checking…</div>}
            {phoneError==="duplicate" && (
              <div style={{ fontSize:13,color:"#f87171",marginTop:8,padding:"10px 14px",background:"rgba(248,113,113,0.08)",border:"1px solid rgba(248,113,113,0.25)",borderRadius:10,display:"flex",alignItems:"center",gap:8 }}>
                <span>⚠️ This number is already registered.</span>
                <button onClick={onBack} style={{ background:"none",border:"none",color:"#38bdf8",cursor:"pointer",fontSize:13,fontWeight:700,textDecoration:"underline",padding:0 }}>Log in instead →</button>
              </div>
            )}
            {phoneError && phoneError!=="duplicate" && (
              <div style={{ fontSize:12,color:"#fb923c",marginTop:6 }}>{phoneError}</div>
            )}
          </div>
          <SelectInput label="District" value={form.district} onChange={F("district")} options={DISTRICTS} />
          <SelectInput label="Preferred Language" value={lang} onChange={v=>{ setLang(v); F("language")(v); }} options={LANGUAGES.map(l=>({ value:l.code,label:`${l.label} — ${l.name}` }))} />
          <div>
            <Label>Location (GPS)</Label>
            <Btn onClick={captureGPS} variant={gps==="done"?"green":"ghost"} full>
              {gps==="loading"?<><Spinner /> Detecting...</>:gps==="done"?`Captured: ${form.location_lat?.toFixed(4)}, ${form.location_lng?.toFixed(4)}`:"Capture My GPS Location"}
            </Btn>
            {gpsError && <div style={{ color:"#f87171",fontSize:13,marginTop:8,background:"rgba(248,113,113,0.08)",padding:"10px",borderRadius:8,border:"1px solid rgba(248,113,113,0.2)" }}>⚠️ {gpsError}</div>}
            {!gpsError && <div style={{ color:"#475569",fontSize:12,marginTop:6 }}>Your exact location helps find the nearest buyers and calculate accurate transport costs.</div>}
          </div>
          <Btn onClick={()=>onRegister({ ...form,language:lang })} full style={{ padding:14,fontSize:15,opacity:canSubmit?1:0.45,pointerEvents:canSubmit?"auto":"none",transition:"opacity 0.2s" }}>Register & Get Started →</Btn>
        </div>
      </Card>
    </div>
  );
}

function FDashboard({ farmer, crops, onAddCrop, onAnalyze, analyzingId, lang }) {
  const [form, setForm] = useState({ crop_type:"tomato",quantity_kg:"",field_size_acres:"",sowing_date:"",expected_harvest_date:"" });
  const [adding, setAdding] = useState(false);
  const { listening, listen, stop } = useVoice();
  const speechCode = LANGUAGES.find(l=>l.code===lang)?.speech||"kn-IN";
  const F = (k) => (v) => setForm(f=>({ ...f,[k]:v }));
  const submit = async () => { const ok = await onAddCrop(form); if (ok) setForm({ crop_type:"tomato",quantity_kg:"",field_size_acres:"",sowing_date:"",expected_harvest_date:"" }); };

  return (
    <div>
      <div style={{ marginBottom:36 }}>
        <div style={{ color:"#475569",fontSize:13,marginBottom:4 }}>Welcome back,</div>
        <div style={{ fontFamily:"'Syne',sans-serif",fontSize:38,fontWeight:900,letterSpacing:"-1.5px",lineHeight:1 }}>{farmer.name}</div>
        <div style={{ color:"#475569",fontSize:14,marginTop:8,display:"flex",gap:10,flexWrap:"wrap",alignItems:"center" }}>
          <span>📍 {farmer.district}, {farmer.state}</span>
          <Badge color="#4ade80">{LANGUAGES.find(l=>l.code===farmer.language)?.name||"Kannada"}</Badge>
        </div>
      </div>
      <Card accent="#4ade80" style={{ marginBottom:28 }}>
        <button onClick={()=>setAdding(x=>!x)} style={{ background:"none",border:"none",color:"#4ade80",fontWeight:700,fontSize:16,cursor:"pointer",display:"flex",alignItems:"center",gap:8,fontFamily:"'Syne',sans-serif" }}>
          {adding?"− Close":"+ Add New Crop"}
        </button>
        {adding && (
          <div style={{ marginTop:20,display:"grid",gap:16 }}>
            <div style={{ display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(180px,1fr))",gap:16 }}>
              <SelectInput label="Crop Type" value={form.crop_type} onChange={F("crop_type")} options={CROPS} />
              <div>
                <Label>Quantity (kg)</Label>
                <div style={{ display:"flex",gap:8 }}>
                  <input type="number" value={form.quantity_kg} onChange={e=>F("quantity_kg")(e.target.value)} placeholder="500"
                    style={{ flex:1,background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.09)",color:"#e2e8f0",padding:"11px 14px",borderRadius:10,fontSize:14,outline:"none" }} />
                  <button onClick={()=>listening?stop():listen(speechCode,v=>F("quantity_kg")(parseVoiceDigits(v)))}
                    style={{ padding:"11px 13px",background:listening?"rgba(239,68,68,0.1)":"rgba(34,197,94,0.08)",border:`1px solid ${listening?"rgba(239,68,68,0.3)":"rgba(34,197,94,0.25)"}`,color:listening?"#f87171":"#4ade80",borderRadius:10,cursor:"pointer" }}>
                    <span className={listening?"pulse":""}>{listening?"⏹":"🎤"}</span>
                  </button>
                </div>
              </div>
              <div>
                <Label>Field Size (acres)</Label>
                <input type="number" value={form.field_size_acres} onChange={e=>F("field_size_acres")(e.target.value)} placeholder="2.5"
                  style={{ width:"100%",background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.09)",color:"#e2e8f0",padding:"11px 14px",borderRadius:10,fontSize:14,outline:"none" }} />
              </div>
              <div>
                <Label>Expected Harvest Date</Label>
                <input type="date" value={form.expected_harvest_date} onChange={e=>F("expected_harvest_date")(e.target.value)}
                  style={{ width:"100%",background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.09)",color:"#e2e8f0",padding:"11px 14px",borderRadius:10,fontSize:14,outline:"none",colorScheme:"dark" }} />
              </div>
            </div>
            <Btn onClick={submit}>Add Crop</Btn>
          </div>
        )}
      </Card>
      <div style={{ fontFamily:"'Syne',sans-serif",fontWeight:700,fontSize:18,marginBottom:16,color:"#e2e8f0" }}>Your Crops</div>
      {crops.length===0
        ? <div style={{ textAlign:"center",padding:60,color:"#475569",border:"1px dashed rgba(255,255,255,0.07)",borderRadius:16 }}>No crops yet. Add your first crop above.</div>
        : <div style={{ display:"grid",gridTemplateColumns:"repeat(auto-fill,minmax(250px,1fr))",gap:14 }}>
          {crops.map(c=>(
            <Card key={c.id} style={{ position:"relative",overflow:"hidden" }}>
              <div style={{ position:"absolute",top:0,left:0,right:0,height:2,background:"linear-gradient(90deg,#16a34a,#0891b2)" }} />
              <div style={{ fontFamily:"'Syne',sans-serif",fontWeight:800,fontSize:20,textTransform:"capitalize",marginBottom:12 }}>{c.crop_type}</div>
              <div style={{ display:"grid",gridTemplateColumns:"1fr 1fr",gap:8,marginBottom:16 }}>
                {[["Quantity",`${c.quantity_kg} kg`],["Field",`${c.field_size_acres??"—"} ac`],["Harvest",c.expected_harvest_date??"Not set"],["Status","Active"]].map(([k,v])=>(
                  <div key={k}><div style={{ color:"#475569",fontSize:11,textTransform:"uppercase",letterSpacing:"0.5px" }}>{k}</div><div style={{ fontWeight:600,fontSize:14,marginTop:2 }}>{v}</div></div>
                ))}
              </div>
              <Btn onClick={()=>onAnalyze(c.id)} disabled={analyzingId !== null} variant="blue" full>
                {analyzingId === c.id ? <><Spinner /> Analyzing...</> : "Run AI Analysis"}
              </Btn>
            </Card>
          ))}
        </div>
      }
    </div>
  );
}

function FAnalysis({ rec, onBack, onLockDeal, farmerLang }) {
  return (
    <div>
      <div style={{ display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:28,flexWrap:"wrap",gap:12 }}>
        <div>
          <button onClick={onBack} style={{ background:"none",border:"none",color:"#475569",cursor:"pointer",fontSize:14,marginBottom:8,display:"flex",alignItems:"center",gap:6 }}>← Dashboard</button>
          <div style={{ fontFamily:"'Syne',sans-serif",fontSize:30,fontWeight:900,letterSpacing:"-1px" }}>AI Analysis</div>
          <div style={{ color:"#475569",fontSize:14,marginTop:4,textTransform:"capitalize" }}>{rec.crop} • {rec.quantity_kg}kg • {rec.farmer}</div>
        </div>
        <Btn onClick={onLockDeal}>Lock Deal with Best Buyer</Btn>
      </div>
      <div style={{ display:"grid",gridTemplateColumns:"1fr 1fr",gap:14,marginBottom:14 }}>
        <Card accent={riColor(rec.resilience_index)}>
          <div style={{ color:"#475569",fontSize:11,letterSpacing:"1px",textTransform:"uppercase",marginBottom:12 }}>Resilience Index</div>
          <div style={{ fontFamily:"'Syne',sans-serif",fontSize:68,fontWeight:900,lineHeight:1,color:riColor(rec.resilience_index),letterSpacing:"-3px" }}>{rec.resilience_index}</div>
          <div style={{ background:"rgba(255,255,255,0.05)",borderRadius:3,height:5,margin:"12px 0" }}>
            <div style={{ background:riColor(rec.resilience_index),height:"100%",borderRadius:3,width:`${rec.resilience_index}%`,transition:"width 1s ease" }} />
          </div>
          <div style={{ display:"flex",justifyContent:"space-between" }}>
            <Badge color={riskColor(rec.risk_level)}>{rec.risk_level} risk</Badge>
            <span style={{ color:"#475569",fontSize:13 }}>{rec.harvest_urgency==="urgent"?"⚠ Urgent harvest":"✓ Normal timing"}</span>
          </div>
          {rec.urgency_reason && <div style={{ marginTop:10,color:"#fbbf24",fontSize:13,background:"rgba(251,191,36,0.07)",padding:"8px 12px",borderRadius:8 }}>{rec.urgency_reason}</div>}
        </Card>
        <div style={{ display:"flex",flexDirection:"column",gap:14 }}>
          <Card style={{ flex:1 }}>
            <div style={{ color:"#475569",fontSize:11,letterSpacing:"1px",textTransform:"uppercase",marginBottom:8 }}>Live Weather</div>
            <div style={{ fontSize:14,color:"#94a3b8",lineHeight:1.6 }}>{rec.weather}</div>
          </Card>
          <Card style={{ flex:1 }}>
            <div style={{ color:"#475569",fontSize:11,letterSpacing:"1px",textTransform:"uppercase",marginBottom:8 }}>APMC Market Price</div>
            <div style={{ fontFamily:"'Syne',sans-serif",fontSize:34,fontWeight:900,color:"#fbbf24" }}>₹{rec.apmc_price_per_kg}<span style={{ fontSize:15,color:"#475569",fontWeight:400 }}>/kg</span></div>
          </Card>
        </div>
      </div>
      {rec.best_buyer && (
        <Card accent="#4ade80" style={{ marginBottom:14 }}>
          <div style={{ color:"#4ade80",fontSize:11,letterSpacing:"1px",textTransform:"uppercase",marginBottom:14 }}>Recommended Buyer</div>
          <div style={{ display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:16 }}>
            <div>
              <div style={{ fontFamily:"'Syne',sans-serif",fontSize:24,fontWeight:800,marginBottom:10 }}>{rec.best_buyer.name}</div>
              <div style={{ display:"flex",gap:8,flexWrap:"wrap" }}>
                <Badge color="#64748b">{rec.best_buyer.type}</Badge>
                <Badge color="#64748b">{rec.best_buyer.district}</Badge>
                <Badge color="#64748b">{rec.best_buyer.distance_km.toFixed(1)} km away</Badge>
                <Badge color="#64748b">₹{rec.best_buyer.transport_cost.toFixed(0)} transport</Badge>
              </div>
            </div>
            <div style={{ textAlign:"right" }}>
              <div style={{ color:"#475569",fontSize:11,textTransform:"uppercase",letterSpacing:"1px" }}>Net Profit</div>
              <div style={{ fontFamily:"'Syne',sans-serif",fontSize:44,fontWeight:900,color:"#4ade80",lineHeight:1.1 }}>₹{rec.net_profit_estimate.toLocaleString()}</div>
            </div>
          </div>
        </Card>
      )}
      <Card accent="#818cf8" style={{ marginBottom:14 }}>
        <div style={{ color:"#a5b4fc",fontSize:11,letterSpacing:"1px",textTransform:"uppercase",marginBottom:12 }}>
          Gemini AI Reasoning — {LANGUAGES.find(l=>l.code===farmerLang)?.name||"Kannada"}
        </div>
        <div style={{ fontSize:16,lineHeight:1.8,color:"#c7d2fe" }}>{rec.reasoning}</div>
        <div style={{ marginTop:12,paddingTop:12,borderTop:"1px solid rgba(129,140,248,0.12)",color:"#6366f1",fontSize:14,fontStyle:"italic" }}>{rec.price_tip}</div>
      </Card>
      <Card>
        <div style={{ color:"#475569",fontSize:11,letterSpacing:"1px",textTransform:"uppercase",marginBottom:18 }}>All Buyers — Profit Comparison</div>
        {[...rec.all_buyers].sort((a,b)=>b.net_profit-a.net_profit).map((b,i)=>{
          const maxP = Math.max(...rec.all_buyers.map(x=>x.net_profit));
          return (
            <div key={b.buyer_id} style={{ display:"flex",alignItems:"center",gap:14,padding:"13px 0",borderBottom:i<rec.all_buyers.length-1?"1px solid rgba(255,255,255,0.04)":"none" }}>
              <div style={{ width:28,height:28,borderRadius:"50%",background:i===0?"rgba(74,222,128,0.12)":"rgba(255,255,255,0.04)",border:`1px solid ${i===0?"rgba(74,222,128,0.35)":"rgba(255,255,255,0.08)"}`,display:"flex",alignItems:"center",justifyContent:"center",fontWeight:700,fontSize:13,color:i===0?"#4ade80":"#475569",flexShrink:0 }}>{i+1}</div>
              <div style={{ flex:1 }}>
                <div style={{ fontWeight:i===0?600:400,fontSize:15,color:i===0?"#e2e8f0":"#94a3b8" }}>{b.name}</div>
                <div style={{ color:"#475569",fontSize:13 }}>{b.district} • {b.distance_km.toFixed(0)}km • ₹{b.transport_cost.toFixed(0)} transport</div>
              </div>
              <div style={{ textAlign:"right" }}>
                <div style={{ fontWeight:700,fontSize:17,color:i===0?"#4ade80":"#64748b" }}>₹{b.net_profit.toLocaleString()}</div>
                <div style={{ background:"rgba(255,255,255,0.04)",borderRadius:2,height:3,marginTop:5,width:72 }}>
                  <div style={{ background:i===0?"#4ade80":"#1e3a5f",height:"100%",borderRadius:2,width:`${(b.net_profit/maxP)*100}%` }} />
                </div>
              </div>
            </div>
          );
        })}
      </Card>
    </div>
  );
}


// ── Reviews & Profiles ────────────────────────────────────────────────────────

function ReviewModal({ data, onClose, onSubmit }) {
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    if (rating === 0) return;
    setSubmitting(true);
    await onSubmit({ ...data, rating, comment });
    setSubmitting(false);
  };

  return (
    <div style={{position:"fixed",inset:0,background:"rgba(0,0,0,0.8)",backdropFilter:"blur(10px)",zIndex:300,display:"flex",alignItems:"center",justifyContent:"center",padding:20}}>
      <div className="fadeUp" style={{background:"#0a1628",border:"1px solid rgba(255,255,255,0.1)",borderRadius:20,padding:32,width:"100%",maxWidth:400}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:24}}>
          <div style={{fontFamily:"'Syne',sans-serif",fontSize:22,fontWeight:800}}>Leave Review</div>
          <button onClick={onClose} style={{background:"none",border:"none",color:"#475569",cursor:"pointer",fontSize:24,lineHeight:1}}>×</button>
        </div>
        <div style={{display:"flex",gap:8,justifyContent:"center",marginBottom:24}}>
          {[1,2,3,4,5].map(star => (
            <span key={star}
              onMouseEnter={()=>setHoverRating(star)} onMouseLeave={()=>setHoverRating(0)}
              onClick={()=>setRating(star)}
              style={{fontSize:36,cursor:"pointer",color:(hoverRating||rating)>=star?"#fbbf24":"#334155",transition:"color 0.2s"}}
            >★</span>
          ))}
        </div>
        <div style={{marginBottom:24}}>
          <Label>Comments (Optional, max 200 chars)</Label>
          <textarea maxLength={200} value={comment} onChange={e=>setComment(e.target.value)}
            style={{width:"100%",height:80,background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.09)",color:"#e2e8f0",padding:"12px",borderRadius:10,fontSize:14,outline:"none",resize:"none"}} />
        </div>
        <Btn onClick={handleSubmit} disabled={rating===0||submitting} full variant="green">
          {submitting ? "Submitting..." : "Submit Review"}
        </Btn>
      </div>
    </div>
  );
}

function ProfileCardModal({ type, id, name, onClose }) {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    axios.get(`http://localhost:8000/api/reviews/${type}/${id}`).then(r => setData(r.data)).catch(()=>{});
  }, [type, id]);

  return (
    <div style={{position:"fixed",inset:0,background:"rgba(0,0,0,0.8)",backdropFilter:"blur(10px)",zIndex:300,display:"flex",alignItems:"center",justifyContent:"center",padding:20}}>
      <div className="fadeUp" style={{background:"#0a1628",border:"1px solid rgba(255,255,255,0.1)",borderRadius:20,padding:32,width:"100%",maxWidth:400}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:20}}>
          <div>
            <div style={{fontFamily:"'Syne',sans-serif",fontSize:24,fontWeight:800}}>{name}</div>
            {data && (
              <div style={{display:"flex",alignItems:"center",gap:8,marginTop:6}}>
                <span style={{color:"#fbbf24",fontSize:18}}>★</span>
                <span style={{fontWeight:700,fontSize:16}}>{data.average_rating}</span>
                <span style={{color:"#64748b",fontSize:14}}>({data.review_count} reviews)</span>
              </div>
            )}
          </div>
          <button onClick={onClose} style={{background:"none",border:"none",color:"#475569",cursor:"pointer",fontSize:24,lineHeight:1}}>×</button>
        </div>
        {!data ? <div style={{textAlign:"center",padding:40}}><Spinner/></div> : (
          <div>
            <div style={{color:"#64748b",fontSize:12,textTransform:"uppercase",letterSpacing:"1px",marginBottom:12}}>Recent Reviews</div>
            {data.recent_reviews.length === 0 ? <div style={{color:"#475569",fontSize:14}}>No reviews yet.</div> : (
              <div style={{display:"grid",gap:12}}>
                {data.recent_reviews.map(r => (
                  <div key={r.id} style={{background:"rgba(255,255,255,0.03)",padding:12,borderRadius:10}}>
                    <div style={{color:"#fbbf24",fontSize:14,marginBottom:4}}>{"★".repeat(r.rating)}{"☆".repeat(5-r.rating)}</div>
                    {r.comment && <div style={{fontSize:13,color:"#cbd5e1"}}>{r.comment}</div>}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Shared Negotiation Components ────────────────────────────────────────────


function NegotiationTimeline({ deal }) {
  const steps = [
    { label:"Original Offer", status: "done", price: deal.agreed_price_per_kg },
    { label:"Counter Offer", status: deal.counter_price_per_kg ? "done" : deal.deal_status==="offer" ? "pending" : "skip", price: deal.counter_price_per_kg },
    { label:"Final Status", status: ["accepted","rejected","locked"].includes(deal.deal_status) ? "done" : "pending" },
  ];
  const statusLabel = deal.deal_status==="accepted"||deal.deal_status==="locked" ? "ACCEPTED" : deal.deal_status==="rejected" ? "REJECTED" : deal.deal_status==="bargaining" ? "NEGOTIATING" : "PENDING";
  const statusClr = deal.deal_status==="accepted"||deal.deal_status==="locked" ? "#4ade80" : deal.deal_status==="rejected" ? "#f87171" : deal.deal_status==="bargaining" ? "#fbbf24" : "#64748b";

  return (
    <div style={{ marginBottom:18 }}>
      <div style={{ fontSize:12, color:"#64748b", textTransform:"uppercase", letterSpacing:"1px", marginBottom:14, fontWeight:700 }}>Deal Timeline</div>
      <div style={{ display:"flex", alignItems:"flex-start", gap:0 }}>
        {steps.map((s,i) => (
          <div key={i} style={{ flex:1, display:"flex", flexDirection:"column", alignItems:"center", position:"relative" }}>
            {/* connector line */}
            {i>0 && <div style={{ position:"absolute", top:12, right:"50%", width:"100%", height:2, background:"rgba(255,255,255,0.06)", zIndex:0 }}>
              <div style={{ height:"100%", borderRadius:2, background: s.status==="done" ? "linear-gradient(90deg,#16a34a,#0891b2)" : "transparent", animation: s.status==="done" ? "step-fill 0.5s ease forwards" : "none" }} />
            </div>}
            {/* dot */}
            <div style={{
              width:26, height:26, borderRadius:"50%", zIndex:1, display:"flex", alignItems:"center", justifyContent:"center",
              background: s.status==="done" ? "linear-gradient(135deg,#16a34a,#0891b2)" : "rgba(255,255,255,0.06)",
              border: s.status==="done" ? "none" : "2px solid rgba(255,255,255,0.12)",
              animation: s.status==="done" ? "step-pop 0.4s ease" : "none",
              boxShadow: s.status==="done" ? "0 0 12px rgba(74,222,128,0.25)" : "none",
              fontSize:12, color:"#fff", fontWeight:700,
            }}>
              {s.status==="done" ? "✓" : i+1}
            </div>
            {/* label */}
            <div style={{ fontSize:11, color: s.status==="done" ? "#e2e8f0" : "#475569", fontWeight:600, marginTop:8, textAlign:"center", lineHeight:1.3 }}>{s.label}</div>
            {/* price under step 1 & 2 */}
            {s.price && <div style={{ fontSize:13, fontWeight:700, color: i===0?"#fbbf24":"#fb923c", marginTop:4, animation:"price-slide 0.3s ease" }}>₹{s.price}/kg</div>}
            {/* final status label */}
            {i===2 && s.status==="done" && <div style={{ fontSize:12, fontWeight:800, color:statusClr, marginTop:4, letterSpacing:"0.5px" }}>{statusLabel}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}

function PriceCompare({ original, counter }) {
  if (!counter) return null;
  const diff = counter - original;
  const pct = ((diff/original)*100).toFixed(1);
  const up = diff > 0;
  return (
    <div style={{ display:"flex", gap:16, alignItems:"center", padding:"14px 18px", background:"rgba(255,255,255,0.025)", border:"1px solid rgba(255,255,255,0.07)", borderRadius:12, marginBottom:14, animation:"price-slide 0.3s ease" }}>
      <div style={{ flex:1, textAlign:"center" }}>
        <div style={{ color:"#475569", fontSize:10, textTransform:"uppercase", letterSpacing:"0.8px", marginBottom:4 }}>Original</div>
        <div style={{ fontFamily:"'Syne',sans-serif", fontSize:22, fontWeight:800, color:"#fbbf24" }}>₹{original}<span style={{fontSize:13,fontWeight:400,color:"#64748b"}}>/kg</span></div>
      </div>
      <div style={{ color:"#475569", fontSize:22 }}>→</div>
      <div style={{ flex:1, textAlign:"center" }}>
        <div style={{ color:"#475569", fontSize:10, textTransform:"uppercase", letterSpacing:"0.8px", marginBottom:4 }}>Counter</div>
        <div style={{ fontFamily:"'Syne',sans-serif", fontSize:22, fontWeight:800, color:"#fb923c" }}>₹{counter}<span style={{fontSize:13,fontWeight:400,color:"#64748b"}}>/kg</span></div>
      </div>
      <div style={{ padding:"4px 10px", borderRadius:8, fontSize:12, fontWeight:700, background: up?"rgba(74,222,128,0.1)":"rgba(248,113,113,0.1)", color: up?"#4ade80":"#f87171", border:`1px solid ${up?"rgba(74,222,128,0.25)":"rgba(248,113,113,0.25)"}` }}>
        {up?"↑":"↓"} {Math.abs(pct)}%
      </div>
    </div>
  );
}

function FDeals({ deals, buyers, onBack, onRespond, farmerId, onProfileOpen, onReviewOpen }) {
  const [counterInputs, setCounterInputs] = useState({});
  const [showCounter, setShowCounter] = useState({});
  const [expanded, setExpanded] = useState({});
  const [optimistic, setOptimistic] = useState({}); // {dealId: "accepted"|"rejected"|"bargaining"}

  const handleComplete = async (dealId) => {
    try {
      await axios.patch(`${API}/deals/${dealId}/complete`, { user_type: "farmer" });
      setOptimistic(p => ({...p, [dealId]: "completed"}));
    } catch (e) { alert("Failed to mark as completed"); }
  };

  const handleReviewSubmit = async (reviewData) => {
    try {
      await axios.post(`${API}/reviews/`, {
        deal_id: reviewData.dealId, reviewer_type: "farmer", reviewer_id: farmerId,
        reviewee_type: "buyer", reviewee_id: reviewData.revieweeId,
        rating: reviewData.rating, comment: reviewData.comment
      });
      // Try to show success (if toast is available, but we might just close for now)
      setReviewModal(null);
    } catch (e) { alert("Failed to submit review"); }
  };


  const statusColor = (s) => s==="accepted"?"#4ade80":s==="rejected"?"#f87171":s==="bargaining"?"#fbbf24":s==="locked"?"#4ade80":"#64748b";
  const displayStatus = (d) => optimistic[d.id] || d.deal_status;
  const statusLabel = (s) => s==="accepted"||s==="locked" ? "ACCEPTED" : s==="rejected" ? "REJECTED" : s==="bargaining" ? "NEGOTIATING" : "PENDING";

  const handleRespond = (dealId, status, counterPrice) => {
    setOptimistic(p => ({...p, [dealId]: status}));
    onRespond(dealId, status, counterPrice);
    setShowCounter(p => ({...p, [dealId]: false}));
  };

  const incomingOffers = deals.filter(d => d.initiated_by === "buyer" && ["offer","bargaining"].includes(d.deal_status));
  const myOffers = deals.filter(d => d.initiated_by === "farmer" && d.deal_status === "offer");
  const closedDeals = deals.filter(d => ["accepted","rejected","locked"].includes(d.deal_status));
  const negotiating = deals.filter(d => d.deal_status === "bargaining" && d.initiated_by === "farmer");

  const DealCard = ({ d, showActions }) => {
    const buyerName = buyers?.find(b => b.id === d.buyer_id)?.name || "Buyer";
    const isExpanded = expanded[d.id];
    const ds = displayStatus(d);
    const isOptimistic = !!optimistic[d.id];
    const isLate = (ds === "accepted" || ds === "locked") && d.expected_delivery_date && new Date(d.expected_delivery_date) < new Date(Date.now() - 2 * 86400000);
    const effectiveStatus = ds === "completed" ? "COMPLETED" : isLate ? "LATE" : (ds === "accepted" || ds === "locked") ? "PENDING" : ds==="rejected" ? "REJECTED" : ds==="bargaining" ? "NEGOTIATING" : "PENDING";
    const statusColor = effectiveStatus==="COMPLETED"?"#4ade80":effectiveStatus==="LATE"?"#f87171":effectiveStatus==="PENDING"?"#fbbf24":ds==="rejected"?"#f87171":ds==="bargaining"?"#fbbf24":"#64748b";
    
    const topGrad = effectiveStatus==="COMPLETED"?"linear-gradient(90deg,#16a34a,#15803d)":
                    effectiveStatus==="LATE"?"linear-gradient(90deg,#dc2626,#991b1b)":
                    ds==="rejected"?"linear-gradient(90deg,#dc2626,#991b1b)":
                    (ds==="accepted" || ds==="locked")?"linear-gradient(90deg,#d97706,#b45309)":
                    ds==="bargaining"?"linear-gradient(90deg,#d97706,#b45309)":
                    "linear-gradient(90deg,#1d4ed8,#4338ca)";

    return (
    <Card key={d.id} style={{ position:"relative",overflow:"hidden", cursor:"pointer", transition:"all 0.3s", ...(isOptimistic?{animation:"optimistic-pulse 1s ease 2"}:{}) }}
      onClick={(e)=>{ if(e.target.tagName!=="BUTTON"&&e.target.tagName!=="INPUT") setExpanded(p=>({...p,[d.id]:!p[d.id]})); }}>
      <div style={{ position:"absolute",top:0,left:0,right:0,height:3, background: topGrad, transition:"background 0.4s" }} />
      <div style={{ display:"flex",justifyContent:"space-between",flexWrap:"wrap",gap:12 }}>
        <div style={{ flex:1 }}>
          <div style={{ fontFamily:"'Syne',sans-serif",fontWeight:800,fontSize:20,textTransform:"capitalize",marginBottom:6 }}>
            {d.crop_type} <span style={{fontSize:15, fontWeight:600, color:"#38bdf8", marginLeft:8}}>with {buyerName}</span>
          </div>
          <div style={{ color:"#94a3b8",fontSize:14 }}>
            {d.quantity_kg}kg &bull; <span style={{color:"#fbbf24",fontWeight:600}}>₹{d.agreed_price_per_kg}/kg</span> &bull; Delivery: {d.expected_delivery_date}
          </div>
          <div style={{ color:"#475569",fontSize:13,marginTop:4 }}>Net to farmer: ₹{Math.round((d.agreed_price_per_kg*d.quantity_kg)-d.transport_cost).toLocaleString()}</div>
        </div>
        <div style={{ display:"flex",gap:8,alignItems:"flex-start",flexDirection:"column" }}>
          {<span style={{ background:statusColor+"18", border:`1px solid ${statusColor}35`, color:statusColor, padding:"4px 14px", borderRadius:20, fontSize:12, fontWeight:800, letterSpacing:"1px", textTransform:"uppercase" }}>{effectiveStatus}</span>}
          {d.initiated_by==="buyer" && <Badge color="#38bdf8">Buyer offer</Badge>}
          {d.initiated_by==="farmer" && <Badge color="#4ade80">My offer</Badge>}
          <span style={{color:"#64748b", fontSize:12, marginTop:4}}>{isExpanded ? "▲ Collapse" : "▼ Expand"}</span>
        </div>
      </div>

      {isExpanded && (
        <div style={{ marginTop:16, paddingTop:16, borderTop:"1px solid rgba(255,255,255,0.06)", animation:"fadeUp 0.3s ease" }}>
          <NegotiationTimeline deal={{...d, deal_status: ds}} />
          {d.counter_price_per_kg && <PriceCompare original={d.agreed_price_per_kg} counter={d.counter_price_per_kg} />}

          {showActions && ds==="offer" && (
            <div>
              {showCounter[d.id] ? (
                <div style={{ display:"flex",gap:8,flexWrap:"wrap",alignItems:"center" }}>
                  <input type="number" placeholder="Your price ₹/kg"
                    value={counterInputs[d.id]||""}
                    onChange={e=>setCounterInputs(prev=>({...prev,[d.id]:e.target.value}))}
                    style={{ flex:1,minWidth:120,background:"rgba(255,255,255,0.06)",border:"1px solid rgba(251,146,60,0.4)",color:"#e2e8f0",padding:"10px 14px",borderRadius:10,fontSize:14,outline:"none" }} />
                  <Btn variant="ghost" onClick={()=>setShowCounter(p=>({...p,[d.id]:false}))} style={{padding:"10px 14px"}}>Cancel</Btn>
                  <Btn variant="blue" onClick={()=>handleRespond(d.id,"bargaining",parseFloat(counterInputs[d.id]))} style={{padding:"10px 14px"}}>Send Counter</Btn>
                </div>
              ) : (
                <div style={{ display:"flex",gap:8,flexWrap:"wrap" }}>
                  <Btn variant="green" onClick={()=>handleRespond(d.id,"accepted",null)} style={{padding:"9px 20px",fontSize:13}}>✓ Accept Offer</Btn>
                  <Btn variant="ghost" onClick={()=>setShowCounter(p=>({...p,[d.id]:true}))} style={{padding:"9px 20px",fontSize:13,color:"#fb923c",border:"1px solid rgba(251,146,60,0.35)"}}>⇄ Counter-Offer</Btn>
                  <Btn variant="red" onClick={()=>handleRespond(d.id,"rejected",null)} style={{padding:"9px 20px",fontSize:13}}>✗ Reject</Btn>
                </div>
              )}
            </div>
          )}


          {(ds==="accepted" || ds==="locked" || ds==="completed") && (
            <div style={{marginTop:12, display:"flex", gap:8}}>
              {ds !== "completed" && (
                <Btn variant="green" disabled={d.farmer_confirmed} onClick={(e)=>{ e.stopPropagation(); handleComplete(d.id); }}>
                  {d.farmer_confirmed ? "Waiting for Buyer..." : "Mark as Completed"}
                </Btn>
              )}
              {ds === "completed" && (
                <Btn variant="ghost" onClick={(e)=>{ e.stopPropagation(); onReviewOpen({ dealId: d.id, revieweeId: d.buyer_id }); }}>Leave Review</Btn>
              )}
            </div>
          )}
          {/* Farmer sees counter from buyer-initiated bargaining */}
          {showActions && ds==="bargaining" && d.counter_price_per_kg && (
            <div style={{ display:"flex",gap:8,flexWrap:"wrap" }}>
              <Btn variant="green" onClick={()=>handleRespond(d.id,"accepted",null)} style={{padding:"9px 20px",fontSize:13}}>✓ Accept ₹{d.counter_price_per_kg}/kg</Btn>
              <Btn variant="red" onClick={()=>handleRespond(d.id,"rejected",null)} style={{padding:"9px 20px",fontSize:13}}>✗ Reject</Btn>
            </div>
          )}
        </div>
      )}
    </Card>
    );
  };

  return (
    <div>
      <button onClick={onBack} style={{ background:"none",border:"none",color:"#475569",cursor:"pointer",fontSize:14,marginBottom:24,display:"flex",alignItems:"center",gap:6 }}>← Dashboard</button>
      <div style={{ fontFamily:"'Syne',sans-serif",fontSize:30,fontWeight:900,marginBottom:28 }}>My Deals</div>

      {incomingOffers.length>0 && (
        <div style={{ marginBottom:32 }}>
          <div style={{ display:"flex",alignItems:"center",gap:10,marginBottom:14 }}>
            <div style={{ fontFamily:"'Syne',sans-serif",fontWeight:700,fontSize:18,color:"#fbbf24" }}>📩 Incoming Offers</div>
            <span style={{ background:"rgba(251,191,36,0.15)",border:"1px solid rgba(251,191,36,0.4)",color:"#fbbf24",borderRadius:20,padding:"2px 10px",fontSize:12,fontWeight:700 }}>{incomingOffers.length}</span>
          </div>
          <div style={{ display:"grid",gap:12 }}>{incomingOffers.map(d=><DealCard key={d.id} d={d} showActions={true} />)}</div>
        </div>
      )}

      {negotiating.length>0 && (
        <div style={{ marginBottom:32 }}>
          <div style={{ fontFamily:"'Syne',sans-serif",fontWeight:700,fontSize:18,color:"#fbbf24",marginBottom:14 }}>⇄ In Negotiation</div>
          <div style={{ display:"grid",gap:12 }}>{negotiating.map(d=><DealCard key={d.id} d={d} showActions={false} />)}</div>
        </div>
      )}

      {myOffers.length>0 && (
        <div style={{ marginBottom:32 }}>
          <div style={{ fontFamily:"'Syne',sans-serif",fontWeight:700,fontSize:18,color:"#4ade80",marginBottom:14 }}>📤 My Offers Sent</div>
          <div style={{ display:"grid",gap:12 }}>{myOffers.map(d=><DealCard key={d.id} d={d} showActions={false} />)}</div>
        </div>
      )}

      {closedDeals.length>0 && (
        <div style={{ marginBottom:32 }}>
          <div style={{ fontFamily:"'Syne',sans-serif",fontWeight:700,fontSize:18,color:"#94a3b8",marginBottom:14 }}>📋 Closed Deals</div>
          <div style={{ display:"grid",gap:12 }}>{closedDeals.map(d=><DealCard key={d.id} d={d} showActions={false} />)}</div>
        </div>
      )}

      {deals.length===0 && (
        <div style={{ textAlign:"center",padding:80,color:"#475569",border:"1px dashed rgba(255,255,255,0.07)",borderRadius:16 }}>
          No deals yet. Run AI analysis to send an offer, or wait for buyers to contact you.
        </div>
      )}
    </div>
  );
}

// ── Buyer Portal ──────────────────────────────────────────────────────────────

function BuyerPortal({ toast, bg, onBack }) {
  const [page, setPage] = useState("login");
  const [buyer, setBuyer] = useState(null);
  const [crops, setCrops] = useState([]);
  const [deals, setDeals] = useState([]);
  const [farmers, setFarmers] = useState([]);
  const [lang, setLang] = useState("en");
  const [offerModal, setOfferModal] = useState(null);
  const [profileModal, setProfileModal] = useState(null);
  const [reviewModal, setReviewModal] = useState(null);

  const loadMarket = async () => {
    try {
      const r = await axios.get(`${API}/crops/`);
      setCrops(r.data);
    } catch { toast("Failed to load market","error"); }
  };

  const login = async (phone) => {
    if (phone.length!==10) { toast("Enter valid 10-digit phone","error"); return; }
    try {
      const r = await axios.get(`${API}/buyers/`);
      const b = r.data.find(x=>x.phone===phone);
      if (!b) { toast("Not registered. Please register.","error"); return; }
      setBuyer(b); await loadMarket(); toast(`Welcome back, ${b.name}!`); setPage("market");
    } catch { toast("Login failed","error"); }
  };

  const register = async (form) => {
    if (!form.name.trim()||form.phone.length!==10) { toast("Name and valid phone required","error"); return; }
    try {
      const r = await axios.post(`${API}/buyers/`, form);
      setBuyer(r.data); await loadMarket(); toast("Registration successful!"); setPage("market");
    } catch (e) {
      const status = e.response?.status;
      const detail = e.response?.data?.detail || "";
      if (status === 409) toast("This phone number is already registered. Please log in instead.", "error");
      else toast(detail || "Registration failed", "error");
    }
  };

  const makeOffer = async (crop, farmer, pricePerKg, qty) => {
    if (!buyer) return;
    const distKm = (buyer?.location_lat && farmer?.location_lat) ? haversine(buyer.location_lat,buyer.location_lng,farmer.location_lat,farmer.location_lng) : 50;
    const transportCost = Math.round(distKm*(qty>500?10:12));
    try {
      await axios.post(`${API}/deals/`, {
        farmer_id:farmer.id, buyer_id:buyer.id, crop_type:crop.crop_type, quantity_kg:qty,
        agreed_price_per_kg:pricePerKg, transport_cost:transportCost,
        expected_delivery_date:new Date(Date.now()+5*86400000).toISOString().split("T")[0],
      });
      toast(`Offer sent to ${farmer.name}! ₹${pricePerKg}/kg for ${qty}kg`);
      setOfferModal(null);
    } catch (e) { toast("Failed: " + JSON.stringify(e.response?.data?.detail || e.message), "error"); }
  };

  const loadDeals = async () => {
    try {
      const [r, f] = await Promise.all([
        axios.get(`${API}/deals/buyer/${buyer.id}`),
        axios.get(`${API}/farmers/`)
      ]);
      setDeals(r.data); setFarmers(f.data); setPage("deals");
    } catch { toast("Failed to load deals","error"); }
  };

  const handleReviewSubmit = async (reviewData) => {
    try {
      await axios.post(`${API}/reviews/`, {
        deal_id: reviewData.dealId, reviewer_type: "buyer", reviewer_id: buyer.id,
        reviewee_type: "farmer", reviewee_id: reviewData.revieweeId,
        rating: reviewData.rating, comment: reviewData.comment
      });
      setReviewModal(null);
      toast("Review submitted! Thank you.");
    } catch (e) { toast("Failed to submit review", "error"); }
  };

  const acceptCounter = async (dealId, counterPrice) => {
    try {
      await axios.patch(`${API}/deals/${dealId}/accept`);
      toast("Deal accepted! 🎉");
      const r = await axios.get(`${API}/deals/buyer/${buyer.id}`).catch(()=>({ data:[] }));
      setDeals(r.data);
    } catch { toast("Failed to accept deal","error"); }
  };

  const counterOffer = async (dealId, price) => {
    try {
      await axios.patch(`${API}/deals/${dealId}/counter`, { counter_price: price });
      toast(`Counter-offer of ₹${price}/kg sent!`);
      const r = await axios.get(`${API}/deals/buyer/${buyer.id}`).catch(()=>({ data:[] }));
      setDeals(r.data);
    } catch { toast("Failed to send counter-offer","error"); }
  };

  const rejectDeal = async (dealId) => {
    try {
      await axios.patch(`${API}/deals/${dealId}/reject`);
      toast("Deal rejected.");
      const r = await axios.get(`${API}/deals/buyer/${buyer.id}`).catch(()=>({ data:[] }));
      setDeals(r.data);
    } catch { toast("Failed to reject deal","error"); }
  };


  const Header = () => (
    <header style={{ background:"rgba(4,8,15,0.92)",backdropFilter:"blur(20px)",borderBottom:"1px solid rgba(56,189,248,0.08)",height:58,display:"flex",alignItems:"center",justifyContent:"space-between",padding:"0 28px",position:"sticky",top:0,zIndex:100 }}>
      <div style={{ display:"flex",alignItems:"center",gap:14 }}>
        <button onClick={onBack} style={{ background:"none",border:"none",color:"#475569",cursor:"pointer",fontSize:18,lineHeight:1,padding:"4px 6px" }}>←</button>
        <span style={{ fontFamily:"'Syne',sans-serif",fontWeight:900,fontSize:20,background:"linear-gradient(90deg,#38bdf8,#818cf8)",WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent" }}>KhetIQ</span>
        <Badge color="#38bdf8">Buyer</Badge>
      </div>
      <div style={{ display:"flex",alignItems:"center",gap:10 }}>
        {buyer && <>
          <button onClick={()=>{ loadMarket(); setPage("market"); }} style={{ background:"none",border:"none",color:page==="market"?"#38bdf8":"#64748b",cursor:"pointer",fontSize:14,fontWeight:500 }}>Marketplace</button>
          <button onClick={loadDeals} style={{ background:"none",border:"none",color:page==="deals"?"#38bdf8":"#64748b",cursor:"pointer",fontSize:14,fontWeight:500 }}>My Deals</button>
          <button onClick={()=>setPage("analytics")} style={{ background:"none",border:"none",color:page==="analytics"?"#38bdf8":"#64748b",cursor:"pointer",fontSize:14,fontWeight:500 }}>📊 Analytics</button>
          <div style={{ width:30,height:30,borderRadius:"50%",background:"linear-gradient(135deg,#0891b2,#6366f1)",display:"flex",alignItems:"center",justifyContent:"center",fontWeight:800,fontSize:13 }}>{buyer.name[0]}</div>
        </>}
        <select value={lang} onChange={e=>setLang(e.target.value)} style={{ background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.08)",color:"#64748b",padding:"5px 10px",borderRadius:8,fontSize:13 }}>
          {LANGUAGES.map(l=><option key={l.code} value={l.code} style={{ background:"#0a1628" }}>{l.label}</option>)}
        </select>
        {buyer && <button onClick={()=>{ setBuyer(null); setCrops([]); setDeals([]); setFarmers([]); setPage("login"); onBack(); }} style={{ background:"none",border:"1px solid rgba(255,255,255,0.1)",color:"#64748b",cursor:"pointer",fontSize:13,padding:"5px 12px",borderRadius:8,display:"flex",alignItems:"center",gap:5,transition:"all 0.2s" }} onMouseEnter={e=>{e.currentTarget.style.borderColor="rgba(248,113,113,0.4)";e.currentTarget.style.color="#f87171";}} onMouseLeave={e=>{e.currentTarget.style.borderColor="rgba(255,255,255,0.1)";e.currentTarget.style.color="#64748b";}}>🚪 Logout</button>}
      </div>
    </header>
  );

  return (
    <div style={{ minHeight:"100vh",background:"#04080f" }}>
      <Header />
      {offerModal && <OfferModal crop={offerModal.crop} farmer={offerModal.farmer} buyer={buyer} onConfirm={makeOffer} onClose={()=>setOfferModal(null)} />}
      <div className="fadeUp" style={{ maxWidth: page==="analytics"?1200:880, margin:"0 auto",padding:"32px 20px",transition:"max-width 0.3s" }}>
        {page==="login" && <BLogin onLogin={login} onRegister={()=>setPage("register")} bg={bg} lang={lang} />}
        {page==="register" && <BRegister onRegister={register} onBack={()=>setPage("login")} lang={lang} setLang={setLang} />}
        {page==="market" && buyer && <BMarket buyer={buyer} crops={crops} onOffer={(crop,farmer)=>setOfferModal({ crop,farmer })} onProfileOpen={setProfileModal} />}
        {page==="deals" && <BDeals deals={deals} farmers={farmers} onBack={()=>setPage("market")} onAcceptCounter={acceptCounter} onCounterOffer={counterOffer} onRejectDeal={rejectDeal} buyerId={buyer.id} onReviewOpen={setReviewModal} />}
        {page==="analytics" && <AnalyticsDashboard />}
      </div>
      {profileModal && <ProfileCardModal type={profileModal.type} id={profileModal.id} name={profileModal.name} onClose={()=>setProfileModal(null)} />}
      {reviewModal && <ReviewModal data={reviewModal} onClose={()=>setReviewModal(null)} onSubmit={handleReviewSubmit} />}
    </div>
  );
}

function OfferModal({ crop, farmer, buyer, onConfirm, onClose }) {
  const distKm = (buyer?.location_lat&&farmer?.location_lat) ? haversine(buyer.location_lat,buyer.location_lng,farmer.location_lat,farmer.location_lng) : 50;
  const apmc = APMC_PRICES_FRONT[crop.crop_type]||20;
  const [price, setPrice] = useState(String(apmc));
  const [qty, setQty] = useState(String(Math.min(crop.quantity_kg,500)));
  const [submitting, setSubmitting] = useState(false);
  const pNum = parseFloat(price)||0, qNum = parseFloat(qty)||0;
  const transportEst = parseFloat((distKm*(qNum>500?10:12)).toFixed(0));
  const gross = pNum*qNum, farmerNet = gross-transportEst;

  const handleConfirm = async () => {
    if (pNum<=0||qNum<=0) return;
    if (qNum>crop.quantity_kg) { alert(`Max available: ${crop.quantity_kg} kg`); return; }
    setSubmitting(true); await onConfirm(crop,farmer,pNum,qNum); setSubmitting(false);
  };

  return (
    <div style={{ position:"fixed",inset:0,background:"rgba(0,0,0,0.78)",backdropFilter:"blur(10px)",zIndex:200,display:"flex",alignItems:"center",justifyContent:"center",padding:20 }}>
      <div className="fadeUp" style={{ background:"#0a1628",border:"1px solid rgba(56,189,248,0.22)",borderRadius:20,padding:32,width:"100%",maxWidth:460 }}>
        <div style={{ display:"flex",justifyContent:"space-between",alignItems:"flex-start",marginBottom:24 }}>
          <div>
            <div style={{ fontFamily:"'Syne',sans-serif",fontSize:22,fontWeight:800,textTransform:"capitalize" }}>Make Offer — {crop.crop_type}</div>
            <div style={{ color:"#475569",fontSize:13,marginTop:4 }}>{farmer.name} • {farmer.district} • {distKm.toFixed(0)} km away</div>
          </div>
          <button onClick={onClose} style={{ background:"none",border:"none",color:"#475569",cursor:"pointer",fontSize:24,lineHeight:1,padding:"0 4px" }}>×</button>
        </div>
        <div style={{ display:"grid",gap:16 }}>
          <div>
            <Label>Your Offer Price (₹/kg)</Label>
            <div style={{ position:"relative" }}>
              <input type="number" value={price} onChange={e=>setPrice(e.target.value)} min="1" step="0.5"
                style={{ width:"100%",background:"rgba(255,255,255,0.04)",border:"1px solid rgba(56,189,248,0.3)",color:"#e2e8f0",padding:"12px 15px",borderRadius:10,fontSize:15,outline:"none",boxSizing:"border-box" }} />
              <div style={{ position:"absolute",right:12,top:"50%",transform:"translateY(-50%)",color:"#475569",fontSize:12,pointerEvents:"none" }}>APMC ₹{apmc}/kg</div>
            </div>
          </div>
          <div>
            <Label>Quantity (kg)</Label>
            <input type="number" value={qty} onChange={e=>setQty(e.target.value)} min="1" max={crop.quantity_kg}
              style={{ width:"100%",background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.09)",color:"#e2e8f0",padding:"12px 15px",borderRadius:10,fontSize:15,outline:"none",boxSizing:"border-box" }} />
            <div style={{ color:"#475569",fontSize:12,marginTop:4 }}>Available: {crop.quantity_kg} kg</div>
          </div>
          <div style={{ background:"rgba(56,189,248,0.05)",border:"1px solid rgba(56,189,248,0.12)",borderRadius:12,padding:16 }}>
            <div style={{ color:"#64748b",fontSize:11,textTransform:"uppercase",letterSpacing:"1px",marginBottom:12 }}>Deal Preview</div>
            <div style={{ display:"grid",gridTemplateColumns:"1fr 1fr",gap:10 }}>
              {[["Gross Value",`₹${gross?gross.toLocaleString():"—"}`],["Est. Transport",`₹${transportEst||"—"}`],["Farmer Net",`₹${farmerNet?farmerNet.toLocaleString():"—"}`],["Distance",`${distKm.toFixed(0)} km`]].map(([k,v])=>(
                <div key={k}><div style={{ color:"#475569",fontSize:11 }}>{k}</div><div style={{ fontWeight:600,fontSize:15,color:"#e2e8f0",marginTop:2 }}>{v}</div></div>
              ))}
            </div>
          </div>
          <div style={{ display:"grid",gridTemplateColumns:"1fr 1fr",gap:10 }}>
            <Btn onClick={onClose} variant="ghost">Cancel</Btn>
            <Btn onClick={handleConfirm} variant="blue" disabled={submitting||pNum<=0||qNum<=0}>
              {submitting?<><Spinner /> Sending...</>:"Send Offer →"}
            </Btn>
          </div>
        </div>
      </div>
    </div>
  );
}

function BLogin({ onLogin, onRegister, bg, lang }) {
  const [phone, setPhone] = useState("");
  const { listening, listen, stop } = useVoice();
  const speechCode = LANGUAGES.find(l=>l.code===lang)?.speech||"en-IN";
  return (
    <div style={{ minHeight:"calc(100vh - 58px)",display:"flex",alignItems:"center",justifyContent:"center",position:"relative",margin:"-32px -20px",padding:24 }}>
      <div style={{ position:"absolute",inset:0,backgroundImage:`url(${bg})`,backgroundSize:"cover",backgroundPosition:"center",filter:"brightness(0.12)" }} />
      <div style={{ position:"relative",zIndex:1,width:"100%",maxWidth:420 }}>
        <Card style={{ padding:40 }}>
          <div style={{ fontFamily:"'Syne',sans-serif",fontSize:26,fontWeight:800,marginBottom:6 }}>Buyer Login</div>
          <div style={{ color:"#475569",fontSize:14,marginBottom:32 }}>Enter your registered phone number</div>
          <div style={{ display:"grid",gap:18 }}>
            <TextInput label="Phone Number" value={phone} onChange={setPhone} placeholder="9900778899" type="tel"
              onVoice={{ listening, onClick:()=>listening?stop():listen(speechCode,v=>setPhone(parseVoiceDigits(v).slice(0,10))) }} />
            <Btn onClick={()=>onLogin(phone)} full>Login →</Btn>
            <div style={{ background:"rgba(56,189,248,0.05)", border:"1px solid rgba(56,189,248,0.15)", borderRadius:10, padding:12, marginTop:8 }}>
              <div style={{ color:"#38bdf8", fontSize:11, fontWeight:700, textTransform:"uppercase", letterSpacing:"1px", marginBottom:4 }}>Demo Buyers</div>
              <div style={{ color:"#94a3b8", fontSize:12 }}>Try: 9900000040, 9900000041, 9900000042</div>
            </div>
            <div style={{ textAlign:"center",color:"#475569",fontSize:14 }}>
              New buyer? <span onClick={onRegister} style={{ color:"#38bdf8",cursor:"pointer",fontWeight:600 }}>Register here</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

function BRegister({ onRegister, onBack, lang, setLang }) {
  const [form, setForm] = useState({ name:"",phone:"",type:"restaurant",district:"Belagavi",location_lat:15.8651,location_lng:74.5089 });
  const [gps, setGps] = useState("idle");
  const [gpsError, setGpsError] = useState(null);
  const [activeVoice, setActiveVoice] = useState(null);
  const [phoneError, setPhoneError] = useState("");
  const [phoneChecking, setPhoneChecking] = useState(false);
  const { listening, listen, stop } = useVoice();
  const speechCode = LANGUAGES.find(l=>l.code===lang)?.speech||"en-IN";
  const F = (k) => (v) => { setForm(f=>({ ...f,[k]:v })); if(k==="phone") setPhoneError(""); };
  const voiceFor = (field, handler) => ({
    listening:activeVoice===field,
    onClick:()=>{ if (activeVoice===field){ stop(); setActiveVoice(null); } else { if(listening)stop(); setActiveVoice(field); listen(speechCode,(v)=>{ handler(v); setActiveVoice(null); }); } },
  });

  const checkPhone = async (phone) => {
    if (phone.length !== 10) { setPhoneError(phone.length > 0 ? "Enter a valid 10-digit number" : ""); return; }
    setPhoneChecking(true);
    try {
      const r = await axios.get(`${API}/buyers/check-phone?number=${phone}`);
      if (r.data.exists) setPhoneError("duplicate");
      else setPhoneError("");
    } catch { /* silent */ }
    setPhoneChecking(false);
  };

  const captureGPS = () => {
    setGps("loading");
    setGpsError(null);
    navigator.geolocation.getCurrentPosition(
      p=>{ setForm(f=>({ ...f,location_lat:p.coords.latitude,location_lng:p.coords.longitude })); setGps("done"); },
      (err)=>{
        setGps("idle");
        if (err.code === 1) setGpsError(<span>Location access was denied. Please enable location in your browser settings <span style={{fontSize:14}}>⚙️</span> to find the best nearby buyers.</span>);
        else if (err.code === 2) setGpsError("Unable to detect your location. Please check your GPS or network.");
        else if (err.code === 3) setGpsError("Location request timed out. Please try again.");
        else setGpsError("An unknown error occurred while getting location.");
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const canSubmit = form.name.trim() && form.phone.length===10 && !phoneError && !phoneChecking;

  return (
    <div style={{ maxWidth:540,margin:"0 auto" }}>
      <button onClick={onBack} style={{ background:"none",border:"none",color:"#475569",cursor:"pointer",fontSize:14,marginBottom:24,display:"flex",alignItems:"center",gap:6 }}>← Back to Login</button>
      <Card>
        <div style={{ fontFamily:"'Syne',sans-serif",fontSize:26,fontWeight:800,marginBottom:6 }}>Register as Buyer</div>
        <div style={{ color:"#475569",fontSize:14,marginBottom:32 }}>Join KhetIQ and source directly from farmers</div>
        <div style={{ display:"grid",gap:18 }}>
          <TextInput label="Business Name" value={form.name} onChange={F("name")} placeholder="Hotel Nisarga Kitchen" onVoice={voiceFor("name",F("name"))} />
          <div>
            <TextInput label="Phone Number" value={form.phone} onChange={F("phone")} placeholder="9900778899" type="tel"
              onVoice={voiceFor("phone",v=>F("phone")(parseVoiceDigits(v).slice(0,10)))}
              onBlur={()=>checkPhone(form.phone)} />
            {phoneChecking && <div style={{ fontSize:12,color:"#64748b",marginTop:6,display:"flex",alignItems:"center",gap:6 }}><Spinner /> Checking…</div>}
            {phoneError==="duplicate" && (
              <div style={{ fontSize:13,color:"#f87171",marginTop:8,padding:"10px 14px",background:"rgba(248,113,113,0.08)",border:"1px solid rgba(248,113,113,0.25)",borderRadius:10,display:"flex",alignItems:"center",gap:8 }}>
                <span>⚠️ This number is already registered.</span>
                <button onClick={onBack} style={{ background:"none",border:"none",color:"#38bdf8",cursor:"pointer",fontSize:13,fontWeight:700,textDecoration:"underline",padding:0 }}>Log in instead →</button>
              </div>
            )}
            {phoneError && phoneError!=="duplicate" && (
              <div style={{ fontSize:12,color:"#fb923c",marginTop:6 }}>{phoneError}</div>
            )}
          </div>
          <SelectInput label="Business Type" value={form.type} onChange={F("type")} options={BUYER_TYPES} />
          <SelectInput label="District" value={form.district} onChange={F("district")} options={DISTRICTS} />
          <SelectInput label="Preferred Language" value={lang} onChange={v=>setLang(v)} options={LANGUAGES.map(l=>({ value:l.code,label:`${l.label} — ${l.name}` }))} />
          <div>
            <Label>Location (GPS)</Label>
            <Btn onClick={captureGPS} variant={gps==="done"?"green":"ghost"} full>
              {gps==="loading"?<><Spinner /> Detecting...</>:gps==="done"?`Captured: ${form.location_lat?.toFixed(4)}, ${form.location_lng?.toFixed(4)}`:"Capture My GPS Location"}
            </Btn>
            {gpsError && <div style={{ color:"#f87171",fontSize:13,marginTop:8,background:"rgba(248,113,113,0.08)",padding:"10px",borderRadius:8,border:"1px solid rgba(248,113,113,0.2)" }}>⚠️ {gpsError}</div>}
          </div>
          <Btn onClick={()=>onRegister(form)} full style={{ padding:14,fontSize:15,opacity:canSubmit?1:0.45,pointerEvents:canSubmit?"auto":"none",transition:"opacity 0.2s" }}>Register & Browse Farmers →</Btn>
        </div>
      </Card>
    </div>
  );
}

function BMarket({ buyer, crops, onOffer, onProfileOpen }) {
  const [search, setSearch] = useState("");
  const [filterCrop, setFilterCrop] = useState("all");
  const [filterDist, setFilterDist] = useState("all");

  const dist = (c) => (!c.farmer?.location_lat) ? 999 : haversine(buyer.location_lat,buyer.location_lng,c.farmer.location_lat,c.farmer.location_lng);
  const availableCrops = [...new Set(crops.map(c=>c.crop_type))].sort();
  const availableDistricts = [...new Set(crops.map(c=>c.farmer?.district).filter(Boolean))].sort();
  const filtered = [...crops]
    .filter(c=>filterCrop==="all"||c.crop_type===filterCrop)
    .filter(c=>filterDist==="all"||c.farmer?.district===filterDist)
    .filter(c=>{ const q=search.toLowerCase(); return !q||c.crop_type.includes(q)||(c.farmer?.name||"").toLowerCase().includes(q); })
    .sort((a,b)=>dist(a)-dist(b));

  return (
    <div>
      <div style={{ marginBottom:24 }}>
        <div style={{ color:"#475569",fontSize:13,marginBottom:4 }}>Marketplace —</div>
        <div style={{ fontFamily:"'Syne',sans-serif",fontSize:36,fontWeight:900,letterSpacing:"-1.5px" }}>{buyer.name}</div>
        <div style={{ color:"#475569",fontSize:14,marginTop:8,display:"flex",gap:10,flexWrap:"wrap" }}>
          <Badge color="#38bdf8">{buyer.type}</Badge>
          <span>📍 {buyer.district}</span>
          <span style={{ color:"#475569" }}>Showing {filtered.length} of {crops.length} crops</span>
        </div>
      </div>
      <div style={{ display:"flex",gap:10,marginBottom:20,flexWrap:"wrap" }}>
        <input value={search} onChange={e=>setSearch(e.target.value)} placeholder="🔍 Search crop or farmer..."
          style={{ flex:1,minWidth:180,background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.09)",color:"#e2e8f0",padding:"9px 14px",borderRadius:10,fontSize:14,outline:"none" }}
          onFocus={e=>e.target.style.borderColor="rgba(56,189,248,0.4)"} onBlur={e=>e.target.style.borderColor="rgba(255,255,255,0.09)"} />
        <select value={filterCrop} onChange={e=>setFilterCrop(e.target.value)} style={{ background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.09)",color:"#e2e8f0",padding:"9px 14px",borderRadius:10,fontSize:14,outline:"none" }}>
          <option value="all" style={{ background:"#0a1628" }}>All Crops</option>
          {availableCrops.map(c=><option key={c} value={c} style={{ background:"#0a1628" }}>{c.charAt(0).toUpperCase()+c.slice(1)}</option>)}
        </select>
        <select value={filterDist} onChange={e=>setFilterDist(e.target.value)} style={{ background:"rgba(255,255,255,0.04)",border:"1px solid rgba(255,255,255,0.09)",color:"#e2e8f0",padding:"9px 14px",borderRadius:10,fontSize:14,outline:"none" }}>
          <option value="all" style={{ background:"#0a1628" }}>All Districts</option>
          {availableDistricts.map(d=><option key={d} value={d} style={{ background:"#0a1628" }}>{d}</option>)}
        </select>
      </div>
      {filtered.length===0
        ? <div style={{ textAlign:"center",padding:80,color:"#475569",border:"1px dashed rgba(255,255,255,0.07)",borderRadius:16 }}>
            {crops.length===0?"No crops available. Farmers will appear here once they register.":"No crops match your filters. Try clearing the search."}
          </div>
        : <div style={{ display:"grid",gap:12 }}>
          {filtered.map(c=>{ const d=dist(c); const apmc=APMC_PRICES_FRONT[c.crop_type]||20; return (
            <Card key={c.id} style={{ position:"relative",overflow:"hidden" }}>
              <div style={{ position:"absolute",top:0,left:0,right:0,height:2,background:"linear-gradient(90deg,#0891b2,#6366f1)" }} />
              <div style={{ display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:14 }}>
                <div style={{ display:"flex",gap:16,alignItems:"flex-start" }}>
                  <div style={{ width:50,height:50,borderRadius:12,background:"linear-gradient(135deg,#0e7490,#1e40af)",display:"flex",alignItems:"center",justifyContent:"center",fontFamily:"'Syne',sans-serif",fontWeight:900,fontSize:16,textTransform:"uppercase",flexShrink:0 }}>{c.crop_type.slice(0,2).toUpperCase()}</div>
                  <div>
                    <div style={{ fontFamily:"'Syne',sans-serif",fontWeight:800,fontSize:20,textTransform:"capitalize",marginBottom:4 }}>{c.crop_type}</div>
                    <div style={{ color:"#94a3b8",fontSize:14 }}>Farmer: <span style={{cursor:"pointer",textDecoration:"underline",color:"#38bdf8"}} onClick={(e)=>{e.stopPropagation(); onProfileOpen&&onProfileOpen({type:"farmer",id:c.farmer.id,name:c.farmer.name})}}>{c.farmer?.name}</span> • {c.farmer?.district}</div>
                    <div style={{ display:"flex",gap:8,marginTop:8,flexWrap:"wrap" }}>
                      <Badge color="#64748b">{c.quantity_kg} kg</Badge>
                      <Badge color="#fbbf24">₹{apmc}/kg APMC</Badge>
                      <Badge color="#64748b">Harvest: {c.expected_harvest_date??"Soon"}</Badge>
                      <Badge color={d<50?"#4ade80":d<150?"#fbbf24":"#94a3b8"}>{d<900?`${d.toFixed(0)} km`:"Calculating..."}</Badge>
                    </div>
                  </div>
                </div>
                <Btn onClick={()=>onOffer(c,c.farmer)} variant="blue">Make Offer</Btn>
              </div>
            </Card>
          ); })}
        </div>
      }
    </div>
  );
}

// ── Analytics Dashboard ──────────────────────────────────────────────────────

function AnalyticsDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  const fetchData = async (d) => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/analytics/dashboard?days=${d}`);
      setData(r.data);
    } catch (e) {
      console.error("Analytics fetch failed:", e);
    }
    setLoading(false);
  };

  useEffect(() => { fetchData(days); }, [days]);

  const APMC_PRICES = {
    tomato:18,onion:22,potato:15,brinjal:20,cabbage:12,cauliflower:25,
    beans:35,carrot:28,chilli:45,garlic:80,ginger:60,maize:20,wheat:22,
    rice:28,banana:18,mango:35,grapes:55,pomegranate:70,
  };

  if (loading) return (
    <div style={{ textAlign:"center",padding:100 }}>
      <Spinner />
      <div style={{ color:"#475569",marginTop:16,fontSize:14 }}>Loading analytics…</div>
    </div>
  );

  if (!data) return (
    <div style={{ textAlign:"center",padding:100,color:"#475569" }}>
      Failed to load analytics. Is the backend running?
    </div>
  );

  const { geo_data, supply_demand, intelligence, summary } = data;
  const maxQty = Math.max(...geo_data.map(f => f.total_quantity_kg), 1);

  const chartTooltipStyle = {
    backgroundColor:"rgba(10,22,40,0.95)",border:"1px solid rgba(56,189,248,0.2)",
    borderRadius:12,color:"#e2e8f0",fontSize:13,
  };

  return (
    <div>
      {/* Header */}
      <div style={{ display:"flex",justifyContent:"space-between",alignItems:"flex-end",marginBottom:28,flexWrap:"wrap",gap:16 }}>
        <div>
          <div style={{ fontFamily:"'Syne',sans-serif",fontSize:34,fontWeight:900,letterSpacing:"-1.5px",
            background:"linear-gradient(135deg,#38bdf8,#818cf8)",WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent" }}>
            Analytics Dashboard
          </div>
          <div style={{ color:"#475569",fontSize:14,marginTop:6 }}>
            {summary.total_farmers} farmers • {summary.total_buyers} buyers • {summary.total_deals} deals ({summary.total_accepted} accepted)
          </div>
        </div>
        {/* Date Range Filter */}
        <div style={{ display:"flex",gap:6 }}>
          {[7,30,90].map(d => (
            <button key={d} onClick={() => setDays(d)} style={{
              padding:"8px 18px",borderRadius:10,fontSize:13,fontWeight:700,cursor:"pointer",
              border: days===d ? "1px solid rgba(56,189,248,0.5)" : "1px solid rgba(255,255,255,0.08)",
              background: days===d ? "rgba(56,189,248,0.12)" : "rgba(255,255,255,0.03)",
              color: days===d ? "#38bdf8" : "#64748b",
              transition:"all 0.2s",
            }}>{d}d</button>
          ))}
        </div>
      </div>

      {/* Summary Stats Row */}
      <div style={{ display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(150px,1fr))",gap:12,marginBottom:24 }}>
        {[
          ["Total Farmers","🌾",summary.total_farmers,"#4ade80"],
          ["Total Buyers","🏪",summary.total_buyers,"#38bdf8"],
          ["Total Deals","📋",summary.total_deals,"#fbbf24"],
          ["Accepted","✅",summary.total_accepted,"#4ade80"],
        ].map(([label,icon,val,color]) => (
          <div key={label} style={{ background:"rgba(255,255,255,0.025)",border:"1px solid rgba(255,255,255,0.07)",borderRadius:14,padding:"18px 20px",textAlign:"center" }}>
            <div style={{ fontSize:24,marginBottom:6 }}>{icon}</div>
            <div style={{ fontFamily:"'Syne',sans-serif",fontSize:28,fontWeight:900,color }}>{val}</div>
            <div style={{ color:"#475569",fontSize:11,textTransform:"uppercase",letterSpacing:"0.8px",marginTop:4 }}>{label}</div>
          </div>
        ))}
        {/* Fulfillment Rate Donut */}
        <div style={{ background:"rgba(255,255,255,0.025)",border:"1px solid rgba(255,255,255,0.07)",borderRadius:14,padding:"18px 20px",textAlign:"center",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center" }}>
          <div style={{ width: 80, height: 80 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={[{value: summary.fulfillment_rate}, {value: 100 - summary.fulfillment_rate}]} cx="50%" cy="50%" innerRadius={28} outerRadius={36} dataKey="value" stroke="none">
                  <Cell fill="#4ade80" />
                  <Cell fill="rgba(255,255,255,0.08)" />
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div style={{ fontFamily:"'Syne',sans-serif",fontSize:22,fontWeight:900,color:"#4ade80",marginTop:-46,marginBottom:18 }}>{summary.fulfillment_rate}%</div>
          <div style={{ color:"#475569",fontSize:11,textTransform:"uppercase",letterSpacing:"0.8px" }}>Fulfillment Rate</div>
        </div>
      </div>

      {/* ── Panel 1: Geographic Heatmap ──────────────── */}
      <Card accent="#38bdf8" style={{ marginBottom:20,overflow:"hidden" }}>
        <div style={{ color:"#38bdf8",fontSize:12,fontWeight:700,letterSpacing:"1px",textTransform:"uppercase",marginBottom:14 }}>
          📍 Farmer Distribution — Geographic Heatmap
        </div>
        <div style={{ borderRadius:12,overflow:"hidden",height:380,position:"relative" }}>
          {geo_data.length > 0 ? (
            <MapContainer
              center={[15.3, 75.7]}
              zoom={7}
              style={{ height:"100%",width:"100%",borderRadius:12 }}
              scrollWheelZoom={true}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {geo_data.filter(f => f.lat && f.lng).map(f => {
                const radius = Math.max(6, Math.min(30, (f.total_quantity_kg / maxQty) * 30));
                return (
                  <CircleMarker key={f.id} center={[f.lat, f.lng]} radius={radius}
                    pathOptions={{
                      fillColor:"#4ade80", color:"#16a34a", weight:2,
                      fillOpacity:0.5 + (f.total_quantity_kg / maxQty) * 0.4,
                    }}>
                    <Popup>
                      <div style={{ fontFamily:"'DM Sans',sans-serif",minWidth:160 }}>
                        <div style={{ fontWeight:700,fontSize:15,marginBottom:6 }}>{f.name}</div>
                        <div style={{ fontSize:12,color:"#666",marginBottom:4 }}>📍 {f.district}</div>
                        <div style={{ fontSize:12,color:"#666",marginBottom:8 }}>Total: {f.total_quantity_kg.toLocaleString()} kg</div>
                        {f.crops.map((c,i) => (
                          <div key={i} style={{ fontSize:12,padding:"2px 0",borderTop:i>0?"1px solid #eee":"none" }}>
                            <span style={{ textTransform:"capitalize",fontWeight:600 }}>{c.crop_type}</span>: {c.quantity_kg} kg
                          </div>
                        ))}
                      </div>
                    </Popup>
                  </CircleMarker>
                );
              })}
            </MapContainer>
          ) : (
            <div style={{ height:"100%",display:"flex",alignItems:"center",justifyContent:"center",color:"#475569",background:"rgba(255,255,255,0.02)",borderRadius:12 }}>
              No farmer location data available
            </div>
          )}
        </div>
        <div style={{ display:"flex",gap:16,marginTop:12,flexWrap:"wrap" }}>
          <div style={{ display:"flex",alignItems:"center",gap:6,fontSize:12,color:"#64748b" }}>
            <div style={{ width:10,height:10,borderRadius:"50%",background:"#4ade80",opacity:0.5 }} /> Small volume
          </div>
          <div style={{ display:"flex",alignItems:"center",gap:6,fontSize:12,color:"#64748b" }}>
            <div style={{ width:18,height:18,borderRadius:"50%",background:"#4ade80",opacity:0.8 }} /> Large volume
          </div>
          <div style={{ fontSize:12,color:"#475569",marginLeft:"auto" }}>Click markers for farmer details</div>
        </div>
      </Card>

      {/* ── Panel 2: Supply vs Demand ──────────────── */}
      <Card accent="#818cf8" style={{ marginBottom:20 }}>
        <div style={{ color:"#a5b4fc",fontSize:12,fontWeight:700,letterSpacing:"1px",textTransform:"uppercase",marginBottom:18 }}>
          📊 Crop Supply vs Demand
        </div>
        {supply_demand.length > 0 ? (
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={supply_demand} margin={{ top:5,right:20,left:10,bottom:40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="crop" angle={-35} textAnchor="end" tick={{ fill:"#64748b",fontSize:11 }}
                axisLine={{ stroke:"rgba(255,255,255,0.08)" }} tickLine={false} height={60}
                tickFormatter={v => v.charAt(0).toUpperCase()+v.slice(1)} />
              <YAxis tick={{ fill:"#64748b",fontSize:11 }} axisLine={{ stroke:"rgba(255,255,255,0.08)" }}
                tickLine={false} tickFormatter={v => v>=1000?`${(v/1000).toFixed(0)}k`:v} />
              <Tooltip contentStyle={chartTooltipStyle} cursor={{ fill:"rgba(255,255,255,0.03)" }}
                formatter={(val,name) => [`${val.toLocaleString()} kg`, name==="supply"?"Supply (listed)":"Demand (offers)"]}
                labelFormatter={v => v.charAt(0).toUpperCase()+v.slice(1)} />
              <Legend wrapperStyle={{ fontSize:12,color:"#94a3b8" }}
                formatter={v => v==="supply"?"Supply (listed by farmers)":"Demand (buyer offers)"} />
              <Bar dataKey="supply" radius={[4,4,0,0]} maxBarSize={32}>
                {supply_demand.map((entry,i) => (
                  <Cell key={i} fill="#4ade80" fillOpacity={0.7} />
                ))}
              </Bar>
              <Bar dataKey="demand" radius={[4,4,0,0]} maxBarSize={32}>
                {supply_demand.map((entry,i) => (
                  <Cell key={i} fill={entry.demand_exceeds?"#fb923c":"#38bdf8"} fillOpacity={0.7} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div style={{ textAlign:"center",padding:60,color:"#475569" }}>No crop data available for this period</div>
        )}
        <div style={{ display:"flex",gap:16,marginTop:8,flexWrap:"wrap",fontSize:12 }}>
          <div style={{ display:"flex",alignItems:"center",gap:6,color:"#64748b" }}>
            <div style={{ width:12,height:12,borderRadius:3,background:"#4ade80",opacity:0.7 }} /> Supply
          </div>
          <div style={{ display:"flex",alignItems:"center",gap:6,color:"#64748b" }}>
            <div style={{ width:12,height:12,borderRadius:3,background:"#38bdf8",opacity:0.7 }} /> Demand
          </div>
          <div style={{ display:"flex",alignItems:"center",gap:6,color:"#64748b" }}>
            <div style={{ width:12,height:12,borderRadius:3,background:"#fb923c",opacity:0.7 }} /> Demand &gt; Supply
          </div>
        </div>
      </Card>

      {/* ── Panel 3: Market Intelligence ──────────────── */}
      <div style={{ marginBottom:32 }}>
        <div style={{ fontFamily:"'Syne',sans-serif",fontWeight:700,fontSize:20,marginBottom:16,
          background:"linear-gradient(90deg,#fbbf24,#fb923c)",WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent" }}>
          ⭐ Top Rated Community
        </div>
        <div style={{ display:"grid",gridTemplateColumns:"1fr 1fr",gap:16 }}>
          <Card accent="#fbbf24">
            <div style={{ color:"#475569",fontSize:12,textTransform:"uppercase",letterSpacing:"1px",marginBottom:12,fontWeight:700 }}>Top Rated Farmers</div>
            <div style={{ display:"grid",gap:10 }}>
              {data.top_rated?.farmers.map((f,i) => (
                <div key={f.id} style={{ display:"flex",justifyContent:"space-between",alignItems:"center",background:"rgba(255,255,255,0.03)",padding:10,borderRadius:8 }}>
                  <div style={{ fontWeight:600,fontSize:14 }}>{i+1}. {f.name}</div>
                  <div style={{ display:"flex",alignItems:"center",gap:6 }}><span style={{color:"#fbbf24"}}>★</span>{f.avg_rating} <span style={{color:"#64748b",fontSize:12}}>({f.review_count})</span></div>
                </div>
              ))}
            </div>
          </Card>
          <Card accent="#fbbf24">
            <div style={{ color:"#475569",fontSize:12,textTransform:"uppercase",letterSpacing:"1px",marginBottom:12,fontWeight:700 }}>Top Rated Buyers</div>
            <div style={{ display:"grid",gap:10 }}>
              {data.top_rated?.buyers.map((b,i) => (
                <div key={b.id} style={{ display:"flex",justifyContent:"space-between",alignItems:"center",background:"rgba(255,255,255,0.03)",padding:10,borderRadius:8 }}>
                  <div style={{ fontWeight:600,fontSize:14 }}>{i+1}. {b.name}</div>
                  <div style={{ display:"flex",alignItems:"center",gap:6 }}><span style={{color:"#fbbf24"}}>★</span>{b.avg_rating} <span style={{color:"#64748b",fontSize:12}}>({b.review_count})</span></div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
      <div style={{ marginBottom:8 }}>
        <div style={{ fontFamily:"'Syne',sans-serif",fontWeight:700,fontSize:20,marginBottom:16,
          background:"linear-gradient(90deg,#fbbf24,#fb923c)",WebkitBackgroundClip:"text",WebkitTextFillColor:"transparent" }}>
          🧠 Market Intelligence
        </div>
        <div style={{ display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(220px,1fr))",gap:14 }}>
          {/* Most Active Crop */}
          <Card accent="#4ade80" style={{ position:"relative",overflow:"hidden" }}>
            <div style={{ position:"absolute",top:0,left:0,right:0,height:3,background:"linear-gradient(90deg,#16a34a,#0891b2)" }} />
            <div style={{ color:"#475569",fontSize:10,textTransform:"uppercase",letterSpacing:"1px",marginBottom:10,fontWeight:700 }}>Most Active Crop</div>
            <div style={{ fontFamily:"'Syne',sans-serif",fontSize:28,fontWeight:900,color:"#4ade80",textTransform:"capitalize" }}>
              {intelligence.most_active_crop}
            </div>
            <div style={{ color:"#64748b",fontSize:13,marginTop:6 }}>{intelligence.most_active_crop_deals} deals this period</div>
          </Card>

          {/* Top District */}
          <Card accent="#38bdf8" style={{ position:"relative",overflow:"hidden" }}>
            <div style={{ position:"absolute",top:0,left:0,right:0,height:3,background:"linear-gradient(90deg,#0891b2,#6366f1)" }} />
            <div style={{ color:"#475569",fontSize:10,textTransform:"uppercase",letterSpacing:"1px",marginBottom:10,fontWeight:700 }}>Top District</div>
            <div style={{ fontFamily:"'Syne',sans-serif",fontSize:28,fontWeight:900,color:"#38bdf8" }}>
              {intelligence.top_district}
            </div>
            <div style={{ color:"#64748b",fontSize:13,marginTop:6 }}>{intelligence.top_district_farmers} registered farmers</div>
          </Card>

          {/* Top Buyer */}
          <Card accent="#818cf8" style={{ position:"relative",overflow:"hidden" }}>
            <div style={{ position:"absolute",top:0,left:0,right:0,height:3,background:"linear-gradient(90deg,#6366f1,#a855f7)" }} />
            <div style={{ color:"#475569",fontSize:10,textTransform:"uppercase",letterSpacing:"1px",marginBottom:10,fontWeight:700 }}>Top Buyer by Volume</div>
            <div style={{ fontFamily:"'Syne',sans-serif",fontSize:22,fontWeight:900,color:"#818cf8" }}>
              {intelligence.top_buyer_name}
            </div>
            <div style={{ color:"#64748b",fontSize:13,marginTop:6 }}>₹{intelligence.top_buyer_value.toLocaleString()} total</div>
          </Card>

          {/* Avg Price Gap */}
          <Card accent="#fbbf24" style={{ position:"relative",overflow:"hidden" }}>
            <div style={{ position:"absolute",top:0,left:0,right:0,height:3,background:"linear-gradient(90deg,#d97706,#ea580c)" }} />
            <div style={{ color:"#475569",fontSize:10,textTransform:"uppercase",letterSpacing:"1px",marginBottom:10,fontWeight:700 }}>Avg Price Gap vs APMC</div>
            <div style={{ fontFamily:"'Syne',sans-serif",fontSize:28,fontWeight:900,color:intelligence.avg_price_gap>=0?"#4ade80":"#f87171" }}>
              {intelligence.avg_price_gap>=0?"+":""}₹{intelligence.avg_price_gap}
              <span style={{ fontSize:14,fontWeight:400,color:"#64748b" }}>/kg</span>
            </div>
            <div style={{ color:"#64748b",fontSize:13,marginTop:6 }}>
              {intelligence.avg_price_gap>=0?"Farmers earning above mandi":"Below mandi average"}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function BDeals({ deals, farmers, onBack, onAcceptCounter, onCounterOffer, onRejectDeal, buyerId, onProfileOpen, onReviewOpen }) {
  const [expanded, setExpanded] = useState({});
  const [counterInputs, setCounterInputs] = useState({});
  const [showCounter, setShowCounter] = useState({});
  const [optimistic, setOptimistic] = useState({});

  const handleComplete = async (dealId) => {
    try {
      await axios.patch(`${API}/deals/${dealId}/complete`, { user_type: "buyer" });
      setOptimistic(p => ({...p, [dealId]: "completed"}));
    } catch (e) { alert("Failed to mark as completed"); }
  };

  const handleReviewSubmit = async (reviewData) => {
    try {
      await axios.post(`${API}/reviews/`, {
        deal_id: reviewData.dealId, reviewer_type: "buyer", reviewer_id: buyerId,
        reviewee_type: "farmer", reviewee_id: reviewData.revieweeId,
        rating: reviewData.rating, comment: reviewData.comment
      });
      setReviewModal(null);
    } catch (e) { alert("Failed to submit review"); }
  };


  const statusColor = (s) => s==="accepted"?"#4ade80":s==="rejected"?"#f87171":s==="bargaining"?"#fb923c":s==="locked"?"#4ade80":"#64748b";
  const displayStatus = (d) => optimistic[d.id] || d.deal_status;
  const statusLabel = (s) => s==="accepted"||s==="locked" ? "ACCEPTED" : s==="rejected" ? "REJECTED" : s==="bargaining" ? "NEGOTIATING" : "PENDING";

  const pending = deals.filter(d=>d.deal_status==="offer"||d.deal_status==="bargaining");
  const closed  = deals.filter(d=>!["offer","bargaining"].includes(d.deal_status));

  const handleAccept = (dealId, counterPrice) => {
    setOptimistic(p => ({...p, [dealId]: "accepted"}));
    onAcceptCounter(dealId, counterPrice);
  };
  const handleReject = (dealId) => {
    setOptimistic(p => ({...p, [dealId]: "rejected"}));
    if (onRejectDeal) onRejectDeal(dealId);
  };
  const handleCounter = (dealId, price) => {
    setOptimistic(p => ({...p, [dealId]: "bargaining"}));
    if (onCounterOffer) onCounterOffer(dealId, price);
    setShowCounter(p => ({...p, [dealId]: false}));
  };

  const DealItem = ({ d }) => {
    const farmerName = farmers?.find(f => f.id === d.farmer_id)?.name || "Farmer";
    const isExpanded = expanded[d.id];
    const ds = displayStatus(d);
    const isOptimistic = !!optimistic[d.id];
    const isLate = (ds === "accepted" || ds === "locked") && d.expected_delivery_date && new Date(d.expected_delivery_date) < new Date(Date.now() - 2 * 86400000);
    const effectiveStatus = ds === "completed" ? "COMPLETED" : isLate ? "LATE" : (ds === "accepted" || ds === "locked") ? "PENDING" : ds==="rejected" ? "REJECTED" : ds==="bargaining" ? "NEGOTIATING" : "PENDING";
    const statusColor = effectiveStatus==="COMPLETED"?"#4ade80":effectiveStatus==="LATE"?"#f87171":effectiveStatus==="PENDING"?"#fbbf24":ds==="rejected"?"#f87171":ds==="bargaining"?"#fbbf24":"#64748b";
    
    const topGrad = effectiveStatus==="COMPLETED"?"linear-gradient(90deg,#16a34a,#15803d)":
                    effectiveStatus==="LATE"?"linear-gradient(90deg,#dc2626,#991b1b)":
                    ds==="rejected"?"linear-gradient(90deg,#dc2626,#991b1b)":
                    (ds==="accepted" || ds==="locked")?"linear-gradient(90deg,#d97706,#ea580c)":
                    ds==="bargaining"?"linear-gradient(90deg,#d97706,#ea580c)":
                    "linear-gradient(90deg,#1d4ed8,#4338ca)";

    return (
    <Card key={d.id} style={{position:"relative",overflow:"hidden", cursor:"pointer", transition:"all 0.3s", ...(isOptimistic?{animation:"optimistic-pulse 1s ease 2"}:{})}}
      onClick={()=>setExpanded(p=>({...p,[d.id]:!p[d.id]}))}>
      <div style={{position:"absolute",top:0,left:0,right:0,height:3, background:topGrad, transition:"background 0.4s"}} />
      <div style={{display:"flex",justifyContent:"space-between",flexWrap:"wrap",gap:12}}>
        <div style={{flex:1}}>
          <div style={{fontFamily:"'Syne',sans-serif",fontWeight:800,fontSize:20,textTransform:"capitalize"}}>
            {d.crop_type} <span style={{fontSize:15, fontWeight:600, color:"#38bdf8", marginLeft:8}}>from {farmerName}</span>
          </div>
          <div style={{color:"#94a3b8",fontSize:14,marginTop:4}}>
            {d.quantity_kg}kg &bull; <span style={{color:"#fbbf24",fontWeight:600}}>₹{d.agreed_price_per_kg}/kg</span>
          </div>
          <div style={{color:"#475569",fontSize:13,marginTop:4}}>Gross: ₹{Math.round(d.agreed_price_per_kg*d.quantity_kg).toLocaleString()} • Transport: ₹{Math.round(d.transport_cost)??"—"} • Delivery: {d.expected_delivery_date}</div>
        </div>
        <div style={{display:"flex",flexDirection:"column",gap:8,alignItems:"flex-end"}}>
          {<span style={{ background:statusColor+"18", border:`1px solid ${statusColor}35`, color:statusColor, padding:"4px 14px", borderRadius:20, fontSize:12, fontWeight:800, letterSpacing:"1px", textTransform:"uppercase" }}>{effectiveStatus}</span>}
          <span style={{color:"#64748b", fontSize:12, marginTop:4}}>{isExpanded ? "▲ Collapse" : "▼ Expand"}</span>
        </div>
      </div>

      {isExpanded && (
        <div style={{ marginTop:16, paddingTop:16, borderTop:"1px solid rgba(255,255,255,0.06)", animation:"fadeUp 0.3s ease" }}>
          <NegotiationTimeline deal={{...d, deal_status: ds}} />
          {d.counter_price_per_kg && <PriceCompare original={d.agreed_price_per_kg} counter={d.counter_price_per_kg} />}


          {(ds==="accepted" || ds==="locked" || ds==="completed") && (
            <div style={{marginTop:12, display:"flex", gap:8}}>
              {ds !== "completed" && (
                <Btn variant="green" disabled={d.buyer_confirmed} onClick={(e)=>{ e.stopPropagation(); handleComplete(d.id); }}>
                  {d.buyer_confirmed ? "Waiting for Farmer..." : "Mark as Completed"}
                </Btn>
              )}
              {ds === "completed" && (
                <Btn variant="ghost" onClick={(e)=>{ e.stopPropagation(); onReviewOpen({ dealId: d.id, revieweeId: d.farmer_id }); }}>Leave Review</Btn>
              )}
            </div>
          )}
          {/* Buyer: accept farmer's counter-offer */}
          {ds==="bargaining" && d.counter_price_per_kg && (
            <div style={{display:"flex",gap:8,flexWrap:"wrap"}}>
              <Btn variant="green" onClick={()=>handleAccept(d.id, d.counter_price_per_kg)} style={{padding:"9px 20px",fontSize:13}}>
                ✓ Accept ₹{d.counter_price_per_kg}/kg
              </Btn>
              <Btn variant="red" onClick={()=>handleReject(d.id)} style={{padding:"9px 20px",fontSize:13}}>✗ Reject</Btn>
            </div>
          )}

          {/* Buyer: send counter-offer on pending deals */}
          {ds==="offer" && (
            <div>
              {showCounter[d.id] ? (
                <div style={{display:"flex",gap:8,flexWrap:"wrap",alignItems:"center"}}>
                  <input type="number" placeholder="Your counter ₹/kg"
                    value={counterInputs[d.id]||""}
                    onClick={e=>e.stopPropagation()}
                    onChange={e=>setCounterInputs(prev=>({...prev,[d.id]:e.target.value}))}
                    style={{ flex:1,minWidth:120,background:"rgba(255,255,255,0.06)",border:"1px solid rgba(56,189,248,0.4)",color:"#e2e8f0",padding:"10px 14px",borderRadius:10,fontSize:14,outline:"none" }} />
                  <Btn variant="ghost" onClick={()=>setShowCounter(p=>({...p,[d.id]:false}))} style={{padding:"10px 14px"}}>Cancel</Btn>
                  <Btn variant="blue" onClick={()=>handleCounter(d.id,parseFloat(counterInputs[d.id]))} style={{padding:"10px 14px"}}>Send Counter</Btn>
                </div>
              ) : (
                <div style={{display:"flex",gap:8,flexWrap:"wrap"}}>
                  <Btn variant="green" onClick={()=>handleAccept(d.id, d.agreed_price_per_kg)} style={{padding:"9px 20px",fontSize:13}}>✓ Accept Offer</Btn>
                  <Btn variant="ghost" onClick={()=>setShowCounter(p=>({...p,[d.id]:true}))} style={{padding:"9px 20px",fontSize:13,color:"#38bdf8",border:"1px solid rgba(56,189,248,0.35)"}}>⇄ Counter-Offer</Btn>
                  <Btn variant="red" onClick={()=>handleReject(d.id)} style={{padding:"9px 20px",fontSize:13}}>✗ Reject</Btn>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </Card>
    );
  };

  return (
    <div>
      <button onClick={onBack} style={{background:"none",border:"none",color:"#475569",cursor:"pointer",fontSize:14,marginBottom:24,display:"flex",alignItems:"center",gap:6}}>← Marketplace</button>
      <div style={{fontFamily:"'Syne',sans-serif",fontSize:30,fontWeight:900,marginBottom:28}}>My Deals</div>
      {pending.length>0 && (
        <div style={{marginBottom:32}}>
          <div style={{fontFamily:"'Syne',sans-serif",fontWeight:700,fontSize:18,color:"#38bdf8",marginBottom:14}}>📋 Active Offers</div>
          <div style={{display:"grid",gap:12}}>{pending.map(d=><DealItem key={d.id} d={d} />)}</div>
        </div>
      )}
      {closed.length>0 && (
        <div style={{marginBottom:32}}>
          <div style={{fontFamily:"'Syne',sans-serif",fontWeight:700,fontSize:18,color:"#94a3b8",marginBottom:14}}>✅ Closed Deals</div>
          <div style={{display:"grid",gap:12}}>{closed.map(d=><DealItem key={d.id} d={d} />)}</div>
        </div>
      )}
      {deals.length===0 && (
        <div style={{textAlign:"center",padding:80,color:"#475569",border:"1px dashed rgba(255,255,255,0.07)",borderRadius:16}}>
          No deals yet. Browse the marketplace and make an offer.
        </div>
      )}
    </div>
  );
}

