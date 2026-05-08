import os

app_file = r"c:\Users\Lenovo\Desktop\KhetIQ\frontend\src\App.jsx"
with open(app_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Elevate profileModal and reviewModal in FarmerPortal
# FarmerPortal starts around line 554
# Adding reviewModal state
farmer_portal_start = "function FarmerPortal({ toast, bg, onBack }) {"
farmer_portal_states = """  const [page, setPage] = useState("login");
  const [farmer, setFarmer] = useState(null);
  const [crops, setCrops] = useState([]);
  const [recommendation, setRecommendation] = useState(null);
  const [deals, setDeals] = useState([]);
  const [buyers, setBuyers] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [lang, setLang] = useState("kn");
  const [dealLockOverlay, setDealLockOverlay] = useState(null);
  const [profileModal, setProfileModal] = useState(null);
  const [reviewModal, setReviewModal] = useState(null);"""

# Replace the existing states in FarmerPortal
old_farmer_states = """  const [page, setPage] = useState("login");
  const [farmer, setFarmer] = useState(null);
  const [crops, setCrops] = useState([]);
  const [recommendation, setRecommendation] = useState(null);
  const [deals, setDeals] = useState([]);
  const [buyers, setBuyers] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [lang, setLang] = useState("kn");
  const [dealLockOverlay, setDealLockOverlay] = useState(null);
  const [profileModal, setProfileModal] = useState(null);"""

content = content.replace(old_farmer_states, farmer_portal_states)

# Add handleReviewSubmit to FarmerPortal
farmer_review_handler = """  const handleReviewSubmit = async (reviewData) => {
    try {
      await axios.post(`${API}/reviews/`, {
        deal_id: reviewData.dealId, reviewer_type: "farmer", reviewer_id: farmer.id,
        reviewee_type: "buyer", reviewee_id: reviewData.revieweeId,
        rating: reviewData.rating, comment: reviewData.comment
      });
      setReviewModal(null);
      toast("Review submitted! Thank you.");
    } catch (e) { toast("Failed to submit review", "error"); }
  };"""

# Insert it before the Header in FarmerPortal
content = content.replace("  const Header = () => (", farmer_review_handler + "\n\n  const Header = () => (")

# Update FarmerPortal return to render modals
farmer_return_old = """        {page==="deals" && <FDeals deals={deals} buyers={buyers} onBack={()=>setPage("dashboard")} onRespond={respondToDeal} farmerId={farmer.id} />}
        {profileModal && <ProfileCardModal type={profileModal.type} id={profileModal.id} name={profileModal.name} onClose={()=>setProfileModal(null)} />}"""

farmer_return_new = """        {page==="deals" && <FDeals deals={deals} buyers={buyers} onBack={()=>setPage("dashboard")} onRespond={respondToDeal} farmerId={farmer.id} onProfileOpen={setProfileModal} onReviewOpen={setReviewModal} />}
        {profileModal && <ProfileCardModal type={profileModal.type} id={profileModal.id} name={profileModal.name} onClose={()=>setProfileModal(null)} />}
        {reviewModal && <ReviewModal data={reviewModal} onClose={()=>setReviewModal(null)} onSubmit={handleReviewSubmit} />}"""

content = content.replace(farmer_return_old, farmer_return_new)


# 2. Elevate states in BuyerPortal
buyer_portal_states_old = """  const [lang, setLang] = useState("en");
  const [offerModal, setOfferModal] = useState(null);
  const [profileModal, setProfileModal] = useState(null);
  const [profileModal, setProfileModal] = useState(null);"""

buyer_portal_states_new = """  const [lang, setLang] = useState("en");
  const [offerModal, setOfferModal] = useState(null);
  const [profileModal, setProfileModal] = useState(null);
  const [reviewModal, setReviewModal] = useState(null);"""

content = content.replace(buyer_portal_states_old, buyer_portal_states_new)

# Add handleReviewSubmit to BuyerPortal
buyer_review_handler = """  const handleReviewSubmit = async (reviewData) => {
    try {
      await axios.post(`${API}/reviews/`, {
        deal_id: reviewData.dealId, reviewer_type: "buyer", reviewer_id: buyer.id,
        reviewee_type: "farmer", reviewee_id: reviewData.revieweeId,
        rating: reviewData.rating, comment: reviewData.comment
      });
      setReviewModal(null);
      toast("Review submitted! Thank you.");
    } catch (e) { toast("Failed to submit review", "error"); }
  };"""

content = content.replace("  const acceptCounter = async (dealId, counterPrice) => {", buyer_review_handler + "\n\n  const acceptCounter = async (dealId, counterPrice) => {")

# Update BuyerPortal return to render modals
buyer_return_old = """        {profileModal && <ProfileCardModal type={profileModal.type} id={profileModal.id} name={profileModal.name} onClose={()=>setProfileModal(null)} />}
        {page==="deals" && <BDeals deals={deals} farmers={farmers} onBack={()=>setPage("market")} onAcceptCounter={acceptCounter} onCounterOffer={counterOffer} onRejectDeal={rejectDeal} buyerId={buyer.id} />}"""

buyer_return_new = """        {profileModal && <ProfileCardModal type={profileModal.type} id={profileModal.id} name={profileModal.name} onClose={()=>setProfileModal(null)} />}
        {reviewModal && <ReviewModal data={reviewModal} onClose={()=>setReviewModal(null)} onSubmit={handleReviewSubmit} />}
        {page==="deals" && <BDeals deals={deals} farmers={farmers} onBack={()=>setPage("market")} onAcceptCounter={acceptCounter} onCounterOffer={counterOffer} onRejectDeal={rejectDeal} buyerId={buyer.id} onProfileOpen={setProfileModal} onReviewOpen={setReviewModal} />}"""

content = content.replace(buyer_return_old, buyer_return_new)


# 3. Clean up BDeals local states and handlers
# BDeals starts around line 1991
bdeals_params_old = "function BDeals({ deals, farmers, onBack, onAcceptCounter, onCounterOffer, onRejectDeal, buyerId }) {"
bdeals_params_new = "function BDeals({ deals, farmers, onBack, onAcceptCounter, onCounterOffer, onRejectDeal, buyerId, onProfileOpen, onReviewOpen }) {"

content = content.replace(bdeals_params_old, bdeals_params_new)

# Remove BDeals local states and handleReviewSubmit (it was there in my previous view)
bdeals_locals_old = """  const [optimistic, setOptimistic] = useState({});
  const [reviewModal, setReviewModal] = useState(null);
  const [profileModal, setProfileModal] = useState(null);

  const handleComplete = async (dealId) => {"""

bdeals_locals_new = """  const [optimistic, setOptimistic] = useState({});

  const handleComplete = async (dealId) => {"""

content = content.replace(bdeals_locals_old, bdeals_locals_new)

# In BDeals' DealItem, replace setProfileModal and setReviewModal calls with props
content = content.replace('setProfileModal({type:"farmer", id:d.farmer_id, name:farmerName})', 'onProfileOpen({type:"farmer", id:d.farmer_id, name:farmerName})')
content = content.replace('setReviewModal({ dealId: d.id, revieweeId: d.farmer_id })', 'onReviewOpen({ dealId: d.id, revieweeId: d.farmer_id })')


# 4. Clean up FDeals local states and handlers
# Need to find FDeals. It's likely around line 1147
fdeals_params_old = "function FDeals({ deals, buyers, onBack, onRespond, farmerId }) {"
fdeals_params_new = "function FDeals({ deals, buyers, onBack, onRespond, farmerId, onProfileOpen, onReviewOpen }) {"

content = content.replace(fdeals_params_old, fdeals_params_new)

fdeals_locals_old = """  const [optimistic, setOptimistic] = useState({}); // {dealId: "accepted"|"rejected"|"bargaining"}
  const [reviewModal, setReviewModal] = useState(null);
  const [profileModal, setProfileModal] = useState(null);

  const handleComplete = async (dealId) => {"""

fdeals_locals_new = """  const [optimistic, setOptimistic] = useState({}); // {dealId: "accepted"|"rejected"|"bargaining"}

  const handleComplete = async (dealId) => {"""

content = content.replace(fdeals_locals_old, fdeals_locals_new)

# In FDeals' DealCard (or similar), replace calls
# Wait, I need to check the component name in FDeals. It was DealCard in my earlier view.
content = content.replace('setProfileModal({type:"buyer", id:d.buyer_id, name:buyerName})', 'onProfileOpen({type:"buyer", id:d.buyer_id, name:buyerName})')
content = content.replace('setReviewModal({ dealId: d.id, revieweeId: d.buyer_id })', 'onReviewOpen({ dealId: d.id, revieweeId: d.buyer_id })')

with open(app_file, "w", encoding="utf-8") as f:
    f.write(content)

print("App.jsx patched successfully")
