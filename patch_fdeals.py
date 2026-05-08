import sys

path = r'c:\Users\Lenovo\Desktop\KhetIQ\frontend\src\App.jsx'
content = open(path, 'r', encoding='utf-8').read()

# ── Replace FDeals with full Accept/Counter/Reject UI ──
old_fdeals = '''function FDeals({ deals, onBack }) {
  return (
    <div>
      <button onClick={onBack} style={{ background:"none",border:"none",color:"#475569",cursor:"pointer",fontSize:14,marginBottom:24,display:"flex",alignItems:"center",gap:6 }}>← Dashboard</button>
      <div style={{ fontFamily:"\'Syne\',sans-serif",fontSize:30,fontWeight:900,marginBottom:28 }}>My Deals</div>
      {deals.length===0
        ? <div style={{ textAlign:"center",padding:80,color:"#475569",border:"1px dashed rgba(255,255,255,0.07)",borderRadius:16 }}>No deals yet. Run AI analysis and lock a deal with a buyer.</div>
        : <div style={{ display:"grid",gap:12 }}>
          {deals.map(d=>(
            <Card key={d.id} style={{ position:"relative",overflow:"hidden" }}>
              <div style={{ position:"absolute",top:0,left:0,right:0,height:2,background:d.payment_status==="completed"?"linear-gradient(90deg,#16a34a,#15803d)":"linear-gradient(90deg,#d97706,#b45309)" }} />
              <div style={{ display:"flex",justifyContent:"space-between",flexWrap:"wrap",gap:12 }}>
                <div>
                  <div style={{ fontFamily:"\'Syne\',sans-serif",fontWeight:800,fontSize:20,textTransform:"capitalize",marginBottom:6 }}>{d.crop_type}</div>
                  <div style={{ color:"#94a3b8",fontSize:14 }}>{d.quantity_kg}kg • ₹{d.agreed_price_per_kg}/kg • Delivery: {d.expected_delivery_date}</div>
                  <div style={{ color:"#475569",fontSize:13,marginTop:4 }}>Net: ₹{((d.agreed_price_per_kg*d.quantity_kg)-d.transport_cost).toLocaleString()}</div>
                </div>
                <div style={{ display:"flex",gap:8,alignItems:"flex-start" }}>
                  <Badge color={d.payment_status==="completed"?"#4ade80":"#fbbf24"}>{d.payment_status}</Badge>
                  <Badge color="#64748b">{d.deal_status}</Badge>
                </div>
              </div>
            </Card>
          ))}
        </div>
      }
    </div>
  );
}'''

new_fdeals = '''function FDeals({ deals, onBack, onRespond }) {
  const [counterInputs, setCounterInputs] = useState({});
  const [showCounter, setShowCounter] = useState({});

  const incomingOffers = deals.filter(d => d.initiated_by === "buyer" && d.deal_status === "offer");
  const myOffers = deals.filter(d => d.initiated_by === "farmer" && d.deal_status === "offer");
  const closedDeals = deals.filter(d => !["offer"].includes(d.deal_status) || d.initiated_by !== "buyer");

  const statusColor = (s) => s==="accepted"?"#4ade80":s==="rejected"?"#f87171":s==="bargaining"?"#fbbf24":s==="locked"?"#818cf8":"#64748b";

  const DealCard = ({ d, showActions }) => (
    <Card key={d.id} style={{ position:"relative",overflow:"hidden" }}>
      <div style={{ position:"absolute",top:0,left:0,right:0,height:2,
        background: d.deal_status==="accepted"?"linear-gradient(90deg,#16a34a,#15803d)":
                    d.deal_status==="rejected"?"linear-gradient(90deg,#dc2626,#991b1b)":
                    d.deal_status==="bargaining"?"linear-gradient(90deg,#d97706,#b45309)":
                    "linear-gradient(90deg,#1d4ed8,#4338ca)" }} />
      <div style={{ display:"flex",justifyContent:"space-between",flexWrap:"wrap",gap:12,marginBottom:showActions?16:0 }}>
        <div style={{ flex:1 }}>
          <div style={{ fontFamily:"\'Syne\',sans-serif",fontWeight:800,fontSize:20,textTransform:"capitalize",marginBottom:6 }}>{d.crop_type}</div>
          <div style={{ color:"#94a3b8",fontSize:14 }}>
            {d.quantity_kg}kg &bull; <span style={{color:"#fbbf24",fontWeight:600}}>₹{d.agreed_price_per_kg}/kg</span> &bull; Delivery: {d.expected_delivery_date}
          </div>
          {d.counter_price_per_kg && (
            <div style={{ marginTop:6,color:"#fb923c",fontSize:13,fontWeight:600 }}>
              🔄 Counter-offer: ₹{d.counter_price_per_kg}/kg from farmer
            </div>
          )}
          <div style={{ color:"#475569",fontSize:13,marginTop:4 }}>Net to farmer: ₹{((d.agreed_price_per_kg*d.quantity_kg)-d.transport_cost).toLocaleString()}</div>
        </div>
        <div style={{ display:"flex",gap:8,alignItems:"flex-start",flexDirection:"column" }}>
          <Badge color={statusColor(d.deal_status)}>{d.deal_status}</Badge>
          <Badge color={d.payment_status==="completed"?"#4ade80":"#94a3b8"}>{d.payment_status}</Badge>
          {d.initiated_by==="buyer" && <Badge color="#38bdf8">Buyer offer</Badge>}
          {d.initiated_by==="farmer" && <Badge color="#4ade80">My offer</Badge>}
        </div>
      </div>
      {showActions && onRespond && (
        <div>
          {showCounter[d.id] ? (
            <div style={{ display:"flex",gap:8,marginTop:8,flexWrap:"wrap",alignItems:"center" }}>
              <input type="number" placeholder="Your price ₹/kg"
                value={counterInputs[d.id]||""}
                onChange={e=>setCounterInputs(prev=>({...prev,[d.id]:e.target.value}))}
                style={{ flex:1,minWidth:120,background:"rgba(255,255,255,0.06)",border:"1px solid rgba(251,146,60,0.4)",color:"#e2e8f0",padding:"9px 13px",borderRadius:9,fontSize:14,outline:"none" }} />
              <Btn variant="ghost" onClick={()=>setShowCounter(p=>({...p,[d.id]:false}))} style={{padding:"9px 14px"}}>Cancel</Btn>
              <Btn variant="blue" onClick={()=>{ onRespond(d.id,"bargaining",parseFloat(counterInputs[d.id])); setShowCounter(p=>({...p,[d.id]:false})); }} style={{padding:"9px 14px"}}>Send Counter</Btn>
            </div>
          ) : (
            <div style={{ display:"flex",gap:8,flexWrap:"wrap",marginTop:4 }}>
              <Btn variant="green" onClick={()=>onRespond(d.id,"accepted",null)} style={{padding:"8px 18px",fontSize:13}}>✓ Accept</Btn>
              <Btn variant="ghost" onClick={()=>setShowCounter(p=>({...p,[d.id]:true}))} style={{padding:"8px 18px",fontSize:13,color:"#fb923c",border:"1px solid rgba(251,146,60,0.35)"}}>⇄ Counter</Btn>
              <Btn variant="red" onClick={()=>onRespond(d.id,"rejected",null)} style={{padding:"8px 18px",fontSize:13}}>✗ Reject</Btn>
            </div>
          )}
        </div>
      )}
    </Card>
  );

  return (
    <div>
      <button onClick={onBack} style={{ background:"none",border:"none",color:"#475569",cursor:"pointer",fontSize:14,marginBottom:24,display:"flex",alignItems:"center",gap:6 }}>← Dashboard</button>
      <div style={{ fontFamily:"\'Syne\',sans-serif",fontSize:30,fontWeight:900,marginBottom:28 }}>My Deals</div>

      {incomingOffers.length>0 && (
        <div style={{ marginBottom:32 }}>
          <div style={{ display:"flex",alignItems:"center",gap:10,marginBottom:14 }}>
            <div style={{ fontFamily:"\'Syne\',sans-serif",fontWeight:700,fontSize:18,color:"#fbbf24" }}>📩 Incoming Offers from Buyers</div>
            <span style={{ background:"rgba(251,191,36,0.15)",border:"1px solid rgba(251,191,36,0.4)",color:"#fbbf24",borderRadius:20,padding:"2px 10px",fontSize:12,fontWeight:700 }}>{incomingOffers.length}</span>
          </div>
          <div style={{ display:"grid",gap:12 }}>
            {incomingOffers.map(d=><DealCard key={d.id} d={d} showActions={true} />)}
          </div>
        </div>
      )}

      {myOffers.length>0 && (
        <div style={{ marginBottom:32 }}>
          <div style={{ fontFamily:"\'Syne\',sans-serif",fontWeight:700,fontSize:18,color:"#4ade80",marginBottom:14 }}>📤 My Offers Sent to Buyers</div>
          <div style={{ display:"grid",gap:12 }}>
            {myOffers.map(d=><DealCard key={d.id} d={d} showActions={false} />)}
          </div>
        </div>
      )}

      {closedDeals.length>0 && (
        <div style={{ marginBottom:32 }}>
          <div style={{ fontFamily:"\'Syne\',sans-serif",fontWeight:700,fontSize:18,color:"#94a3b8",marginBottom:14 }}>📋 Deal History</div>
          <div style={{ display:"grid",gap:12 }}>
            {closedDeals.map(d=><DealCard key={d.id} d={d} showActions={false} />)}
          </div>
        </div>
      )}

      {deals.length===0 && (
        <div style={{ textAlign:"center",padding:80,color:"#475569",border:"1px dashed rgba(255,255,255,0.07)",borderRadius:16 }}>
          No deals yet. Run AI analysis to send an offer, or wait for buyers to contact you.
        </div>
      )}
    </div>
  );
}'''

if 'function FDeals({ deals, onBack }) {' in content:
    content = content.replace('function FDeals({ deals, onBack }) {', 'function FDeals({ deals, onBack, onRespond }) {', 1)

# Find and replace the old body - do it line by line
lines = content.split('\n')
start_idx = None
end_idx = None
for i,line in enumerate(lines):
    if 'function FDeals(' in line:
        start_idx = i
    if start_idx is not None and i > start_idx and line.strip() == '}' and end_idx is None:
        # Check next line is blank or comment
        if i+1 < len(lines) and ('// ──' in lines[i+1] or lines[i+1].strip() == ''):
            end_idx = i
            break

if start_idx is not None and end_idx is not None:
    lines[start_idx:end_idx+1] = new_fdeals.split('\n')
    content = '\n'.join(lines)
    print(f"FDeals replaced (lines {start_idx}-{end_idx})")
else:
    print(f"FDeals NOT found: start={start_idx} end={end_idx}")

open(path, 'w', encoding='utf-8').write(content)
print("Done")
