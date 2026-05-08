import os

app_file = r"c:\Users\Lenovo\Desktop\KhetIQ\frontend\src\App.jsx"
with open(app_file, "r", encoding="utf-8") as f:
    content = f.read()

# Fix FarmerPortal
FARMER_PORTAL_SEARCH = """function FarmerPortal({ toast, bg, onBack }) {
  const [page, setPage] = useState("login");
  const [farmer, setFarmer] = useState(null);
  const [crops, setCrops] = useState([]);
  const [recommendation, setRecommendation] = useState(null);
  const [deals, setDeals] = useState([]);
  const [buyers, setBuyers] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [lang, setLang] = useState("kn");
  const [dealLockOverlay, setDealLockOverlay] = useState(null);

  const loadCrops = async (f) => { const r = await axios.get(`${API}/crops/farmer/${f.id}`); setCrops(r.data); };"""

FARMER_PORTAL_REPLACE = """function FarmerPortal({ toast, bg, onBack }) {
  const [page, setPage] = useState("login");
  const [farmer, setFarmer] = useState(null);
  const [crops, setCrops] = useState([]);
  const [recommendation, setRecommendation] = useState(null);
  const [deals, setDeals] = useState([]);
  const [buyers, setBuyers] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [lang, setLang] = useState("kn");
  const [dealLockOverlay, setDealLockOverlay] = useState(null);
  const [profileModal, setProfileModal] = useState(null);

  const loadCrops = async (f) => { const r = await axios.get(`${API}/crops/farmer/${f.id}`); setCrops(r.data); };"""

content = content.replace(FARMER_PORTAL_SEARCH, FARMER_PORTAL_REPLACE)

# Fix FarmerPortal Header
# Finding the malformed Header in FarmerPortal
F_HEADER_START = """  const Header = () => ("""
F_HEADER_END = """  );"""

# The Header is around lines 662-689
# Let's find the specific block and replace it with a clean one
F_HEADER_BAD = """  const Header = () => (
    <header style={{ background:"rgba(4,8,15,0.92)",backdropFilter:"blur(20px)",borderBottom:"1px solid rgba(34,197,94,0.08)",height:58,display:"flex",alignItems:"center",justifyContent:"space-between",padding:"0 28px",position:"sticky",top:0,zIndex:100 }}>
      <div style={{ display:"flex",alignItems:"center",gap:14 }}>
        
      {reviewModal && <ReviewModal data={reviewModal} onClose={()=>setReviewModal(null)} onSubmit={handleReviewSubmit} />}
      {profileModal && <ProfileCardModal type={profileModal.type} id={profileModal.id} name={profileModal.name} onClose={()=>setProfileModal(null)} />}
      
      {reviewModal && <ReviewModal data={reviewModal} onClose={()=>setReviewModal(null)} onSubmit={handleReviewSubmit} />}
      {profileModal && <ProfileCardModal type={profileModal.type} id={profileModal.id} name={profileModal.name} onClose={()=>setProfileModal(null)} />}
      <button onClick={onBack}

 style={{ background:"none",border:"none",color:"#475569",cursor:"pointer",fontSize:18,lineHeight:1,padding:"4px 6px" }}>←</button>
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
  );"""

F_HEADER_CLEAN = """  const Header = () => (
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
  );"""

content = content.replace(F_HEADER_BAD, F_HEADER_CLEAN)

# Fix FarmerPortal return block to include profileModal
F_RETURN_SEARCH = """        {page==="dashboard" && farmer && <FDashboard farmer={farmer} crops={crops} onAddCrop={addCrop} onAnalyze={analyze} analyzing={analyzing} lang={lang} />}
        {page==="analysis" && recommendation && <FAnalysis rec={recommendation} onBack={()=>setPage("dashboard")} onLockDeal={lockDeal} farmerLang={farmer?.language||"kn"} />}
        {page==="deals" && <FDeals deals={deals} buyers={buyers} onBack={()=>setPage("dashboard")} onRespond={respondToDeal} farmerId={farmer.id} />}
      </div>
    </div>"""

F_RETURN_REPLACE = """        {page==="dashboard" && farmer && <FDashboard farmer={farmer} crops={crops} onAddCrop={addCrop} onAnalyze={analyze} analyzing={analyzing} lang={lang} />}
        {page==="analysis" && recommendation && <FAnalysis rec={recommendation} onBack={()=>setPage("dashboard")} onLockDeal={lockDeal} farmerLang={farmer?.language||"kn"} />}
        {page==="deals" && <FDeals deals={deals} buyers={buyers} onBack={()=>setPage("dashboard")} onRespond={respondToDeal} farmerId={farmer.id} />}
        {profileModal && <ProfileCardModal type={profileModal.type} id={profileModal.id} name={profileModal.name} onClose={()=>setProfileModal(null)} />}
      </div>
    </div>"""

content = content.replace(F_RETURN_SEARCH, F_RETURN_REPLACE)


# Fix BuyerPortal
BUYER_PORTAL_SEARCH = """function BuyerPortal({ toast, bg, onBack }) {
  const [page, setPage] = useState("login");
  const [buyer, setBuyer] = useState(null);
  const [crops, setCrops] = useState([]);
  const [deals, setDeals] = useState([]);
  const [farmers, setFarmers] = useState([]);
  const [lang, setLang] = useState("en");
  const [offerModal, setOfferModal] = useState(null);"""

BUYER_PORTAL_REPLACE = """function BuyerPortal({ toast, bg, onBack }) {
  const [page, setPage] = useState("login");
  const [buyer, setBuyer] = useState(null);
  const [crops, setCrops] = useState([]);
  const [deals, setDeals] = useState([]);
  const [farmers, setFarmers] = useState([]);
  const [lang, setLang] = useState("en");
  const [offerModal, setOfferModal] = useState(null);
  const [profileModal, setProfileModal] = useState(null);"""

content = content.replace(BUYER_PORTAL_SEARCH, BUYER_PORTAL_REPLACE)

with open(app_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed portals")
