path = r'c:\Users\Lenovo\Desktop\KhetIQ\frontend\src\App.jsx'
content = open(path, 'r', encoding='utf-8').read()

# ── 1. Add acceptCounter to BuyerPortal (after loadDeals) ──
old_load_deals_buyer = """  const loadDeals = async () => {
    const r = await axios.get(`${API}/deals/buyer/${buyer.id}`).catch(()=>({ data:[] }));
    setDeals(r.data); setPage("deals");
  };"""

new_load_deals_buyer = """  const loadDeals = async () => {
    const r = await axios.get(`${API}/deals/buyer/${buyer.id}`).catch(()=>({ data:[] }));
    setDeals(r.data); setPage("deals");
  };

  const acceptCounter = async (dealId, counterPrice) => {
    try {
      await axios.patch(`${API}/deals/${dealId}/status`, {
        deal_status: "accepted",
        counter_price_per_kg: counterPrice,
      });
      toast("Counter-offer accepted! Deal locked.");
      const r = await axios.get(`${API}/deals/buyer/${buyer.id}`).catch(()=>({ data:[] }));
      setDeals(r.data);
    } catch { toast("Failed to accept counter-offer","error"); }
  };"""

if old_load_deals_buyer in content:
    content = content.replace(old_load_deals_buyer, new_load_deals_buyer, 1)
    print("Patch 1: acceptCounter added")
else:
    print("WARN: loadDeals buyer not found")

# ── 2. Wire acceptCounter into BDeals render ──
old_bdeals_render = '{page==="deals" && <BDeals deals={deals} onBack={()=>setPage("market")} />}'
new_bdeals_render = '{page==="deals" && <BDeals deals={deals} onBack={()=>setPage("market")} onAcceptCounter={acceptCounter} />}'
if old_bdeals_render in content:
    content = content.replace(old_bdeals_render, new_bdeals_render, 1)
    print("Patch 2: BDeals onAcceptCounter wired")
else:
    print("WARN: BDeals render line not found, trying with escaped chars")

# ── 3. Replace BDeals with version showing counter-offer + Accept Counter button ──
new_bdeals = '''function BDeals({ deals, onBack, onAcceptCounter }) {
  const statusColor = (s) => s==="accepted"?"#4ade80":s==="rejected"?"#f87171":s==="bargaining"?"#fb923c":s==="locked"?"#818cf8":"#64748b";
  const pending = deals.filter(d=>d.deal_status==="offer"||d.deal_status==="bargaining");
  const closed  = deals.filter(d=>!["offer","bargaining"].includes(d.deal_status));
  const Section = ({title, color, items}) => items.length===0?null:(
    <div style={{marginBottom:32}}>
      <div style={{fontFamily:"\'Syne\',sans-serif",fontWeight:700,fontSize:18,color,marginBottom:14}}>{title}</div>
      <div style={{display:"grid",gap:12}}>
        {items.map(d=>(
          <Card key={d.id} style={{position:"relative",overflow:"hidden"}}>
            <div style={{position:"absolute",top:0,left:0,right:0,height:2,
              background:d.deal_status==="accepted"?"linear-gradient(90deg,#16a34a,#15803d)":
                         d.deal_status==="rejected"?"linear-gradient(90deg,#dc2626,#991b1b)":
                         d.deal_status==="bargaining"?"linear-gradient(90deg,#d97706,#ea580c)":
                         "linear-gradient(90deg,#1d4ed8,#4338ca)"}} />
            <div style={{display:"flex",justifyContent:"space-between",flexWrap:"wrap",gap:12}}>
              <div style={{flex:1}}>
                <div style={{fontFamily:"\'Syne\',sans-serif",fontWeight:800,fontSize:20,textTransform:"capitalize"}}>{d.crop_type}</div>
                <div style={{color:"#94a3b8",fontSize:14,marginTop:4}}>
                  {d.quantity_kg}kg &bull; <span style={{color:"#fbbf24",fontWeight:600}}>₹{d.agreed_price_per_kg}/kg (your offer)</span>
                </div>
                {d.counter_price_per_kg && (
                  <div style={{marginTop:8,padding:"8px 12px",background:"rgba(251,146,60,0.08)",border:"1px solid rgba(251,146,60,0.3)",borderRadius:9}}>
                    <span style={{color:"#fb923c",fontWeight:700,fontSize:14}}>🔄 Farmer counter-offer: ₹{d.counter_price_per_kg}/kg</span>
                    <span style={{color:"#64748b",fontSize:13,marginLeft:8}}>
                      (was ₹{d.agreed_price_per_kg}/kg)
                    </span>
                  </div>
                )}
                <div style={{color:"#475569",fontSize:13,marginTop:4}}>Gross: ₹{(d.agreed_price_per_kg*d.quantity_kg).toLocaleString()} • Transport: ₹{d.transport_cost?.toFixed(0)??"—"} • Delivery: {d.expected_delivery_date}</div>
              </div>
              <div style={{display:"flex",flexDirection:"column",gap:8,alignItems:"flex-end"}}>
                <Badge color={statusColor(d.deal_status)}>{d.deal_status}</Badge>
                <Badge color={d.payment_status==="completed"?"#4ade80":"#94a3b8"}>{d.payment_status}</Badge>
              </div>
            </div>
            {d.deal_status==="bargaining" && d.counter_price_per_kg && onAcceptCounter && (
              <div style={{marginTop:14,display:"flex",gap:8,flexWrap:"wrap"}}>
                <Btn variant="green" onClick={()=>onAcceptCounter(d.id, d.counter_price_per_kg)} style={{padding:"8px 18px",fontSize:13}}>
                  ✓ Accept ₹{d.counter_price_per_kg}/kg
                </Btn>
                <span style={{color:"#475569",fontSize:13,alignSelf:"center"}}>or go back to marketplace to make a new offer</span>
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
  return (
    <div>
      <button onClick={onBack} style={{background:"none",border:"none",color:"#475569",cursor:"pointer",fontSize:14,marginBottom:24,display:"flex",alignItems:"center",gap:6}}>← Marketplace</button>
      <div style={{fontFamily:"\'Syne\',sans-serif",fontSize:30,fontWeight:900,marginBottom:28}}>My Deals</div>
      <Section title="📋 Active Offers" color="#38bdf8" items={pending} />
      <Section title="✅ Closed Deals" color="#94a3b8" items={closed} />
      {deals.length===0 && (
        <div style={{textAlign:"center",padding:80,color:"#475569",border:"1px dashed rgba(255,255,255,0.07)",borderRadius:16}}>
          No deals yet. Browse the marketplace and make an offer.
        </div>
      )}
    </div>
  );
}'''

# Find and replace BDeals
lines = content.split('\n')
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if 'function BDeals(' in line:
        start_idx = i
    if start_idx is not None and i > start_idx and line.strip() == '}':
        if i+1 < len(lines) and lines[i+1].strip() == '':
            end_idx = i
            break

if start_idx is not None and end_idx is not None:
    lines[start_idx:end_idx+1] = new_bdeals.split('\n')
    content = '\n'.join(lines)
    print(f"Patch 3: BDeals replaced (lines {start_idx}-{end_idx})")
else:
    print(f"WARN: BDeals not found: start={start_idx} end={end_idx}")

open(path, 'w', encoding='utf-8').write(content)
print("All patches done.")
