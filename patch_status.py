import os

app_file = r"c:\Users\Lenovo\Desktop\KhetIQ\frontend\src\App.jsx"
with open(app_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update imports
IMPORT_SEARCH = 'import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from "recharts";'
IMPORT_REPLACE = 'import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, PieChart, Pie } from "recharts";'
content = content.replace(IMPORT_SEARCH, IMPORT_REPLACE)

# 2. Add complete API calls to FDeals
FDEALS_API_SEARCH = """  const handleReviewSubmit = async (reviewData) => {"""
FDEALS_API_REPLACE = """  const handleComplete = async (dealId) => {
    try {
      await axios.patch(`${API}/deals/${dealId}/complete`, { user_type: "farmer" });
      setOptimistic(p => ({...p, [dealId]: "completed"}));
      // Optional: Refresh deals here
    } catch (e) { alert("Failed to mark as completed"); }
  };

  const handleReviewSubmit = async (reviewData) => {"""
content = content.replace(FDEALS_API_SEARCH, FDEALS_API_REPLACE)

# 3. Add complete API calls to BDeals
BDEALS_API_SEARCH = """  const handleReviewSubmit = async (reviewData) => {"""
BDEALS_API_REPLACE = """  const handleComplete = async (dealId) => {
    try {
      await axios.patch(`${API}/deals/${dealId}/complete`, { user_type: "buyer" });
      setOptimistic(p => ({...p, [dealId]: "completed"}));
    } catch (e) { alert("Failed to mark as completed"); }
  };

  const handleReviewSubmit = async (reviewData) => {"""
content = content.replace(BDEALS_API_SEARCH, BDEALS_API_REPLACE)

# 4. FDeals status label, badge, button
FDEALS_CARD_SEARCH = """    const ds = displayStatus(d);
    const isOptimistic = !!optimistic[d.id];
    const topGrad = ds==="accepted"?"linear-gradient(90deg,#16a34a,#15803d)":
                    ds==="rejected"?"linear-gradient(90deg,#dc2626,#991b1b)":
                    ds==="bargaining"?"linear-gradient(90deg,#d97706,#b45309)":
                    "linear-gradient(90deg,#1d4ed8,#4338ca)";"""

FDEALS_CARD_REPLACE = """    const ds = displayStatus(d);
    const isOptimistic = !!optimistic[d.id];
    const isLate = (ds === "accepted" || ds === "locked") && d.expected_delivery_date && new Date(d.expected_delivery_date) < new Date(Date.now() - 2 * 86400000);
    const effectiveStatus = ds === "completed" ? "COMPLETED" : isLate ? "LATE" : (ds === "accepted" || ds === "locked") ? "PENDING" : ds==="rejected" ? "REJECTED" : ds==="bargaining" ? "NEGOTIATING" : "PENDING";
    const statusColor = effectiveStatus==="COMPLETED"?"#4ade80":effectiveStatus==="LATE"?"#f87171":effectiveStatus==="PENDING"?"#fbbf24":ds==="rejected"?"#f87171":ds==="bargaining"?"#fbbf24":"#64748b";
    
    const topGrad = effectiveStatus==="COMPLETED"?"linear-gradient(90deg,#16a34a,#15803d)":
                    effectiveStatus==="LATE"?"linear-gradient(90deg,#dc2626,#991b1b)":
                    ds==="rejected"?"linear-gradient(90deg,#dc2626,#991b1b)":
                    (ds==="accepted" || ds==="locked")?"linear-gradient(90deg,#d97706,#b45309)":
                    ds==="bargaining"?"linear-gradient(90deg,#d97706,#b45309)":
                    "linear-gradient(90deg,#1d4ed8,#4338ca)";"""
content = content.replace(FDEALS_CARD_SEARCH, FDEALS_CARD_REPLACE)

FDEALS_BADGE_SEARCH = """          {(ds==="accepted"||ds==="locked") ? <LockedBadge /> :
           <span style={{ background:statusColor(ds)+"18", border:`1px solid ${statusColor(ds)}35`, color:statusColor(ds), padding:"4px 14px", borderRadius:20, fontSize:12, fontWeight:800, letterSpacing:"1px", textTransform:"uppercase" }}>{statusLabel(ds)}</span>}"""

FDEALS_BADGE_REPLACE = """          {<span style={{ background:statusColor+"18", border:`1px solid ${statusColor}35`, color:statusColor, padding:"4px 14px", borderRadius:20, fontSize:12, fontWeight:800, letterSpacing:"1px", textTransform:"uppercase" }}>{effectiveStatus}</span>}"""
content = content.replace(FDEALS_BADGE_SEARCH, FDEALS_BADGE_REPLACE)

# And action buttons for farmer
FDEALS_ACTION_SEARCH = """          {(ds==="accepted" || ds==="locked") && (
            <div style={{marginTop:12}}>
              <Btn variant="ghost" onClick={(e)=>{ e.stopPropagation(); setReviewModal({ dealId: d.id, revieweeId: d.buyer_id }); }}>Leave Review</Btn>
            </div>
          )}"""

FDEALS_ACTION_REPLACE = """          {(ds==="accepted" || ds==="locked" || ds==="completed") && (
            <div style={{marginTop:12, display:"flex", gap:8}}>
              {ds !== "completed" && (
                <Btn variant="green" disabled={d.farmer_confirmed} onClick={(e)=>{ e.stopPropagation(); handleComplete(d.id); }}>
                  {d.farmer_confirmed ? "Waiting for Buyer..." : "Mark as Completed"}
                </Btn>
              )}
              {ds === "completed" && (
                <Btn variant="ghost" onClick={(e)=>{ e.stopPropagation(); setReviewModal({ dealId: d.id, revieweeId: d.buyer_id }); }}>Leave Review</Btn>
              )}
            </div>
          )}"""
content = content.replace(FDEALS_ACTION_SEARCH, FDEALS_ACTION_REPLACE)


# 5. BDeals status label, badge, button
BDEALS_CARD_SEARCH = """    const ds = displayStatus(d);
    const isOptimistic = !!optimistic[d.id];
    const topGrad = ds==="accepted"?"linear-gradient(90deg,#16a34a,#15803d)":
                    ds==="rejected"?"linear-gradient(90deg,#dc2626,#991b1b)":
                    ds==="bargaining"?"linear-gradient(90deg,#d97706,#ea580c)":
                    "linear-gradient(90deg,#1d4ed8,#4338ca)";"""

BDEALS_CARD_REPLACE = """    const ds = displayStatus(d);
    const isOptimistic = !!optimistic[d.id];
    const isLate = (ds === "accepted" || ds === "locked") && d.expected_delivery_date && new Date(d.expected_delivery_date) < new Date(Date.now() - 2 * 86400000);
    const effectiveStatus = ds === "completed" ? "COMPLETED" : isLate ? "LATE" : (ds === "accepted" || ds === "locked") ? "PENDING" : ds==="rejected" ? "REJECTED" : ds==="bargaining" ? "NEGOTIATING" : "PENDING";
    const statusColor = effectiveStatus==="COMPLETED"?"#4ade80":effectiveStatus==="LATE"?"#f87171":effectiveStatus==="PENDING"?"#fbbf24":ds==="rejected"?"#f87171":ds==="bargaining"?"#fbbf24":"#64748b";
    
    const topGrad = effectiveStatus==="COMPLETED"?"linear-gradient(90deg,#16a34a,#15803d)":
                    effectiveStatus==="LATE"?"linear-gradient(90deg,#dc2626,#991b1b)":
                    ds==="rejected"?"linear-gradient(90deg,#dc2626,#991b1b)":
                    (ds==="accepted" || ds==="locked")?"linear-gradient(90deg,#d97706,#ea580c)":
                    ds==="bargaining"?"linear-gradient(90deg,#d97706,#ea580c)":
                    "linear-gradient(90deg,#1d4ed8,#4338ca)";"""
content = content.replace(BDEALS_CARD_SEARCH, BDEALS_CARD_REPLACE)

BDEALS_BADGE_SEARCH = """          {(ds==="accepted"||ds==="locked") ? <LockedBadge /> :
           <span style={{ background:statusColor(ds)+"18", border:`1px solid ${statusColor(ds)}35`, color:statusColor(ds), padding:"4px 14px", borderRadius:20, fontSize:12, fontWeight:800, letterSpacing:"1px", textTransform:"uppercase" }}>{statusLabel(ds)}</span>}"""

BDEALS_BADGE_REPLACE = """          {<span style={{ background:statusColor+"18", border:`1px solid ${statusColor}35`, color:statusColor, padding:"4px 14px", borderRadius:20, fontSize:12, fontWeight:800, letterSpacing:"1px", textTransform:"uppercase" }}>{effectiveStatus}</span>}"""
content = content.replace(BDEALS_BADGE_SEARCH, BDEALS_BADGE_REPLACE)

# Action buttons for buyer
BDEALS_ACTION_SEARCH = """          {(ds==="accepted" || ds==="locked") && (
            <div style={{marginTop:12}}>
              <Btn variant="ghost" onClick={(e)=>{ e.stopPropagation(); setReviewModal({ dealId: d.id, revieweeId: d.farmer_id }); }}>Leave Review</Btn>
            </div>
          )}"""

BDEALS_ACTION_REPLACE = """          {(ds==="accepted" || ds==="locked" || ds==="completed") && (
            <div style={{marginTop:12, display:"flex", gap:8}}>
              {ds !== "completed" && (
                <Btn variant="green" disabled={d.buyer_confirmed} onClick={(e)=>{ e.stopPropagation(); handleComplete(d.id); }}>
                  {d.buyer_confirmed ? "Waiting for Farmer..." : "Mark as Completed"}
                </Btn>
              )}
              {ds === "completed" && (
                <Btn variant="ghost" onClick={(e)=>{ e.stopPropagation(); setReviewModal({ dealId: d.id, revieweeId: d.farmer_id }); }}>Leave Review</Btn>
              )}
            </div>
          )}"""
content = content.replace(BDEALS_ACTION_SEARCH, BDEALS_ACTION_REPLACE)


# 6. Analytics Dashboard
ANALYTICS_STATS_SEARCH = """      {/* Summary Stats Row */}
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
      </div>"""

ANALYTICS_STATS_REPLACE = """      {/* Summary Stats Row */}
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
      </div>"""
content = content.replace(ANALYTICS_STATS_SEARCH, ANALYTICS_STATS_REPLACE)

with open(app_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Status patch applied successfully")
