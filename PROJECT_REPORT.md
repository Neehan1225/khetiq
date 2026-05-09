# KhetIQ — Comprehensive Project Report
## AI-Driven Agricultural Supply Chain & Resilience Co-pilot

---

## 1. Executive Summary

KhetIQ is a full-stack web platform that connects farmers in Karnataka directly with buyers (restaurants, traders, supermarkets, exporters) using **AI-powered crop analysis, real-time weather intelligence, and smart logistics optimization**. The platform eliminates middlemen by providing farmers with data-driven recommendations on which buyer to sell to, factoring in transport costs, APMC mandi prices, and weather risk — all delivered in the farmer's native language (Kannada, Hindi, Telugu, Tamil, Marathi, English).

### Core Value Proposition
- **For Farmers**: Get AI-analyzed crop resilience scores, optimal buyer recommendations, and multilingual voice-first accessibility.
- **For Buyers**: Browse a live marketplace of available crops, make offers, negotiate prices, and track deal fulfillment.
- **For the Ecosystem**: A trust layer built on mutual reviews, fulfillment tracking, and transparent analytics.

---

## 2. Technology Stack

### 2.1 Frontend
| Technology | Purpose |
|---|---|
| **React 18** | Component-based UI with hooks (useState, useEffect, useCallback) |
| **Vite 8** | Fast HMR dev server and build tooling |
| **Axios** | HTTP client for REST API communication |
| **Recharts** | Data visualization (BarChart, PieChart, LineChart, DonutChart) |
| **React-Leaflet** | Interactive geographic maps with OpenStreetMap tiles |
| **Web Speech API** | Browser-native voice input for multilingual data entry |
| **CSS-in-JS (inline)** | Premium dark-mode UI with glassmorphism and micro-animations |

### 2.2 Backend
| Technology | Purpose |
|---|---|
| **FastAPI (Python 3.11)** | Async REST API framework with auto-generated OpenAPI docs |
| **SQLAlchemy 2.0 (Async)** | ORM with async PostgreSQL driver (asyncpg) |
| **PostgreSQL 15** | Relational database for all persistent data |
| **Pydantic v2** | Request/response validation and serialization |
| **Uvicorn** | ASGI server for production deployment |

### 2.3 AI & External Services
| Service | Purpose |
|---|---|
| **Google Gemini 2.0 Flash** | AI reasoning engine for crop analysis and multilingual recommendations |
| **Gemini 1.5 Flash** | Conversational AI copilot and voice transcription |
| **Open-Meteo API** | Real-time 7-day weather forecasts (free, no API key) |
| **APMC Price Database** | Karnataka mandi reference prices for 20+ crops |
| **Google AMED API** | Satellite-based crop health monitoring (with fallback estimator) |
| **Google Maps Distance Matrix** | Road distance calculation (with Haversine fallback) |

### 2.4 Infrastructure
| Component | Details |
|---|---|
| **Docker Compose** | Multi-container orchestration (PostgreSQL + FastAPI backend) |
| **PostgreSQL 15** | Container with persistent volume (`postgres_data`) |
| **Backend Container** | Python 3.11-slim with all dependencies |
| **Frontend** | Vite dev server on port 5173 |
| **Backend API** | FastAPI on port 8000 |

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND (React + Vite)            │
│  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │ Farmer   │  │ Buyer    │  │ Analytics         │  │
│  │ Portal   │  │ Portal   │  │ Dashboard         │  │
│  └────┬─────┘  └────┬─────┘  └────────┬──────────┘  │
│       │              │                 │              │
│       └──────────────┼─────────────────┘              │
│                      │ HTTP (axios)                   │
└──────────────────────┼────────────────────────────────┘
                       │
              ┌────────▼────────┐
              │  FastAPI Backend │ (port 8000)
              │  /api/...        │
              ├─────────────────┤
              │ Routes:          │
              │  /farmers        │
              │  /buyers         │
              │  /crops          │
              │  /deals          │
              │  /reviews        │
              │  /recommendations│
              │  /analytics      │
              │  /copilot        │
              │  /notifications  │
              ├─────────────────┤
              │ Agents:          │
              │  resilience_agent│
              ├─────────────────┤
              │ Services:        │
              │  gemini_service  │
              │  weather_service │
              │  maps_service    │
              │  apmc_service    │
              │  amed_service    │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │  PostgreSQL 15   │ (port 5432)
              │  khetiq_db       │
              └─────────────────┘
```

---

## 4. Database Schema (Entity-Relationship)

### 4.1 Farmers Table
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Auto-generated unique identifier |
| name | VARCHAR(100) | Farmer's full name |
| phone | VARCHAR(15) | Unique, used for login |
| location_lat | FLOAT | GPS latitude |
| location_lng | FLOAT | GPS longitude |
| village | VARCHAR(100) | Optional village name |
| district | VARCHAR(50) | Karnataka district |
| state | VARCHAR(50) | Default: "Karnataka" |
| language | VARCHAR(10) | Preferred language code (kn, hi, en, etc.) |
| created_at | TIMESTAMP | Auto-generated |

### 4.2 Buyers Table
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Auto-generated |
| name | VARCHAR(100) | Business name |
| type | VARCHAR(30) | restaurant / trader / supermarket / processor / exporter |
| gstin | VARCHAR(15) | GST identification number |
| phone | VARCHAR(15) | Login identifier |
| location_lat | FLOAT | GPS latitude |
| location_lng | FLOAT | GPS longitude |
| district | VARCHAR(50) | Business district |
| created_at | TIMESTAMP | Auto-generated |

### 4.3 Crops Table
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Auto-generated |
| farmer_id | UUID (FK → farmers.id) | Owner farmer |
| crop_type | VARCHAR(50) | e.g., tomato, onion, wheat |
| quantity_kg | FLOAT | Available quantity |
| field_size_acres | FLOAT | Optional field size |
| sowing_date | DATE | When planted |
| expected_harvest_date | DATE | Predicted harvest |
| amed_confirmed | BOOLEAN | Whether satellite data confirmed |
| created_at | TIMESTAMP | Auto-generated |

### 4.4 Deals Table
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Auto-generated |
| farmer_id | UUID (FK → farmers.id) | Selling farmer |
| buyer_id | UUID (FK → buyers.id) | Purchasing buyer |
| crop_type | VARCHAR(50) | Crop being traded |
| quantity_kg | FLOAT | Deal quantity |
| agreed_price_per_kg | FLOAT | Initial or final price |
| counter_price_per_kg | FLOAT | Counter-offer price (nullable) |
| transport_cost | FLOAT | Estimated transport cost |
| total_value | FLOAT | quantity × price |
| expected_delivery_date | DATE | When delivery is expected |
| payment_status | VARCHAR(20) | pending / completed |
| deal_status | VARCHAR(20) | offer / accepted / rejected / bargaining / locked / completed |
| initiated_by | VARCHAR(10) | farmer or buyer |
| farmer_confirmed | BOOLEAN | Farmer marked as completed |
| buyer_confirmed | BOOLEAN | Buyer marked as completed |
| created_at | TIMESTAMP | Auto-generated |

### 4.5 Reviews Table
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Auto-generated |
| deal_id | UUID (FK → deals.id) | Associated deal |
| reviewer_type | VARCHAR(20) | "farmer" or "buyer" |
| reviewer_id | UUID | Who wrote the review |
| reviewee_type | VARCHAR(20) | "farmer" or "buyer" |
| reviewee_id | UUID | Who is being reviewed |
| rating | INTEGER | 1-5 stars |
| comment | VARCHAR(500) | Optional text feedback |
| created_at | TIMESTAMP | Auto-generated |

### 4.6 Recommendations Table
| Column | Type | Description |
|---|---|---|
| id | UUID (PK) | Auto-generated |
| farmer_id | UUID (FK → farmers.id) | Target farmer |
| crop_id | UUID (FK → crops.id) | Analyzed crop |
| recommended_buyer_id | UUID (FK → buyers.id) | AI-selected buyer |
| net_profit_estimate | FLOAT | Predicted profit |
| resilience_index | FLOAT | 0-100 crop viability score |
| risk_level | VARCHAR(10) | low / medium / high |
| reasoning | TEXT | AI-generated reasoning |
| generated_at | TIMESTAMP | Auto-generated |

---

## 5. API Endpoints (Complete Reference)

### 5.1 Farmers (`/api/farmers`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | List all farmers |
| POST | `/` | Register new farmer (with phone uniqueness check) |

### 5.2 Buyers (`/api/buyers`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | List all buyers |
| POST | `/` | Register new buyer |

### 5.3 Crops (`/api/crops`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/` | Add a new crop listing |
| GET | `/farmer/{farmer_id}` | Get all crops by farmer |

### 5.4 Deals (`/api/deals`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/` | Create a new deal/offer |
| PATCH | `/{id}/status` | Update deal status |
| PATCH | `/{id}/counter` | Send counter-offer price |
| PATCH | `/{id}/accept` | Accept a deal |
| PATCH | `/{id}/reject` | Reject a deal |
| PATCH | `/{id}/complete` | Two-sided completion confirmation |
| GET | `/farmer/{farmer_id}` | Get farmer's deals |
| GET | `/buyer/{buyer_id}` | Get buyer's deals |

### 5.5 Reviews (`/api/reviews`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/` | Submit a review (1-5 stars + comment) |
| GET | `/{type}/{id}` | Get reviews for a user (avg rating + 3 most recent) |

### 5.6 Recommendations (`/api/recommendations`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/analyze/{crop_id}` | Run full AI analysis on a crop |
| GET | `/farmer/{farmer_id}` | Get past recommendations |

### 5.7 Analytics (`/api/analytics`)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/dashboard?days=30` | Full analytics dashboard data |

### 5.8 AI Copilot (`/api/copilot`)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/ask` | Text-based AI advisor (multilingual) |
| POST | `/voice` | Voice-based AI advisor (audio upload) |

---

## 6. Core Algorithms & Logic

### 6.1 Haversine Distance Formula
Used to calculate straight-line distance between farmer and buyer GPS coordinates.

```python
def haversine_distance(lat1, lng1, lat2, lng2):
    R = 6371  # Earth's radius in km
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    return R * 2 * asin(sqrt(a))
```

### 6.2 Transport Cost Estimation
```python
def calculate_transport_cost(distance_km, quantity_kg):
    base_rate = 10 if quantity_kg > 500 else 12  # ₹/km
    return distance_km * base_rate
```

### 6.3 LATE Status Detection (Frontend)
Automatically flags overdue deals on the client side:
```javascript
const isLate = (deal) => {
    if (!["locked","accepted"].includes(deal.deal_status)) return false;
    const delivery = new Date(deal.expected_delivery_date);
    const today = new Date();
    const diffDays = (today - delivery) / (1000 * 60 * 60 * 24);
    return diffDays > 2;  // More than 2 days overdue
};
```

### 6.4 Two-Sided Deal Completion
Both farmer AND buyer must independently confirm delivery before status changes to "completed":
```python
# Backend logic
if body.user_type == "farmer":
    deal.farmer_confirmed = True
elif body.user_type == "buyer":
    deal.buyer_confirmed = True

if deal.farmer_confirmed and deal.buyer_confirmed:
    deal.deal_status = "completed"
```

### 6.5 Fulfillment Rate Metric
```python
fulfillment_rate = (completed_deals / total_accepted_deals) × 100
```

### 6.6 AI Resilience Index (Gemini 2.0)
The AI analyzes crop data, weather, and buyer options to produce:
- **Resilience Index** (0-100): Overall crop viability score
- **Risk Level**: low / medium / high
- **Harvest Urgency**: normal / urgent (based on weather)
- **Best Buyer Selection**: Factoring distance, transport cost, and net profit
- **Multilingual Reasoning**: Full explanation in farmer's language

---

## 7. Feature-by-Feature Breakdown

### 7.1 Farmer Portal

#### 7.1.1 Registration & Login
- Phone-based authentication (10-digit validation)
- Voice input for phone number entry (Web Speech API)
- GPS location capture with detailed error handling
- Phone uniqueness check (HTTP 409 if duplicate)
- Multilingual interface (6 languages)

#### 7.1.2 Crop Dashboard
- Add new crops with type, quantity, field size, harvest date
- Voice input for quantity field
- View all crops in a responsive grid layout
- Each crop card shows type, quantity, field size, harvest date

#### 7.1.3 AI Analysis (Run AI Analysis button)
- Calls `/api/recommendations/analyze/{crop_id}`
- Triggers the full Resilience Agent pipeline:
  1. Fetches 7-day weather forecast from Open-Meteo
  2. Retrieves APMC mandi reference price
  3. Gets satellite field data (AMED or fallback)
  4. Calculates transport cost to every buyer
  5. Sends all data to Gemini 2.0 for reasoning
- Displays:
  - Resilience Index (0-100 with color-coded bar)
  - Risk Level badge
  - Live Weather summary
  - APMC Market Price
  - Recommended Buyer with net profit
  - AI Reasoning in farmer's language
  - Price tip (actionable advice)
  - All Buyers ranked by profit

#### 7.1.4 Deal Locking
- "Lock Deal with Best Buyer" creates a deal with status "locked"
- Animated overlay confirms the deal lock
- Deal appears in "My Deals" tab

#### 7.1.5 My Deals (Farmer)
- Categorized sections: Incoming Offers, In Negotiation, My Offers Sent, Closed Deals
- Status badges: PENDING (yellow), COMPLETED (green), LATE (red)
- Accept/Reject/Counter-Offer actions on incoming offers
- "Mark as Completed" button for two-sided confirmation
- "Leave Review" button after completion
- Click buyer name → Profile Card with rating and reviews

### 7.2 Buyer Portal

#### 7.2.1 Registration & Login
- Same phone-based auth as farmer
- Additional fields: business type, GSTIN
- GPS location capture

#### 7.2.2 Marketplace
- Browse all available crops from all farmers
- Each listing shows: crop type, quantity, farmer name, district, distance
- "Make Offer" button opens offer modal
- Offer modal shows: APMC reference price, transport cost estimate, net calculation
- Click farmer name → Profile Card with reviews

#### 7.2.3 Deal Negotiation
- Make initial offer with custom price and quantity
- Counter-offer workflow (buyer ↔ farmer)
- Accept/Reject actions
- Full negotiation timeline visualization

#### 7.2.4 My Deals (Buyer)
- Categorized: Offers Sent, Active Deals, Completed
- Status badges with LATE detection
- "Mark as Completed" button
- "Leave Review" after completion

### 7.3 Analytics Dashboard

#### 7.3.1 Summary Cards
- Total Farmers, Total Buyers, Total Deals, Accepted Deals

#### 7.3.2 Fulfillment Rate
- Donut chart showing completed vs pending deals
- Percentage calculation: (completed / accepted) × 100

#### 7.3.3 Supply vs Demand Chart
- Bar chart comparing crop supply (farmer listings) vs demand (buyer deals)
- Per-crop breakdown

#### 7.3.4 Geographic Map
- Interactive Leaflet map with farmer locations
- Circle markers sized by crop volume
- Popups showing farmer details and crops

#### 7.3.5 Top Rated Leaderboards
- Top Rated Farmers (by average review rating)
- Top Rated Buyers (by average review rating)

#### 7.3.6 Market Intelligence Cards
- Most Active Crop (by deal count)
- Top District (by farmer registrations)
- Top Buyer by Volume (total deal value)
- Average Price Gap vs APMC (farmer advantage/disadvantage)

### 7.4 Review & Trust System
- 5-star rating with hover preview
- Optional text comment (max 200 chars)
- One review per user per deal (duplicate prevention)
- Profile Card modal showing: average rating, review count, 3 most recent reviews
- Reviews aggregated in Analytics for leaderboards

### 7.5 AI Copilot
- Text-based conversational AI advisor
- Voice-based advisor (audio upload to Gemini)
- Context-aware: includes recent deals in prompts
- Returns response + 3 suggested follow-up questions
- Multilingual (responds in user's preferred language)

### 7.6 Notification System
- Backend route for deal status change notifications
- Real-time toast notifications on the frontend

---

## 8. Deal Lifecycle (State Machine)

```
                    ┌──────────┐
                    │  OFFER   │ (initial state)
                    └────┬─────┘
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ ACCEPTED │ │BARGAINING│ │ REJECTED │
        └────┬─────┘ └────┬─────┘ └──────────┘
             │            │
             │     ┌──────┼──────┐
             │     ▼      ▼      ▼
             │  ACCEPTED REJECTED COUNTER
             │     │               │
             │     │      ┌────────┘
             ▼     ▼      ▼
        ┌────────────────────┐
        │   LOCKED / ACCEPTED │
        └────────┬───────────┘
                 │
     ┌───────────┼───────────┐
     ▼                       ▼
 farmer_confirmed=true   buyer_confirmed=true
     │                       │
     └───────────┬───────────┘
                 ▼
        ┌────────────────┐
        │   COMPLETED    │
        └────────────────┘
```

---

## 9. External API Integrations

### 9.1 Open-Meteo Weather API (FREE, No Key)
- **URL**: `https://api.open-meteo.com/v1/forecast`
- **Data**: 7-day forecast with daily precipitation, max/min temp, weather codes
- **Used for**: AI resilience analysis, harvest urgency detection
- **Fallback**: Returns "weather data unavailable" with 30°C defaults

### 9.2 Google Gemini AI
- **Model for Analysis**: `gemini-2.0-flash-lite`
- **Model for Copilot**: `gemini-1.5-flash`
- **Used for**: Crop resilience scoring, buyer recommendation, multilingual reasoning, voice transcription
- **Fallback**: Deterministic algorithm using transport cost + weather keywords

### 9.3 APMC Mandi Prices
- **Source**: Hardcoded from data.gov.in averages (20+ crops)
- **Used for**: Base price reference, price gap analysis in analytics

### 9.4 Google AMED (Optional)
- **Used for**: Satellite-based crop stage and field health
- **Fallback**: KhetIQ estimator based on crop growth cycles

### 9.5 Google Maps Distance Matrix (Optional)
- **Used for**: Actual road distance between farmer and buyer
- **Fallback**: Haversine formula for straight-line distance

---

## 10. Seed Data Profile

The platform ships with realistic demo data:
- **40 Farmers** across 8 Karnataka districts (Belagavi, Dharwad, Mysuru, etc.)
- **15 Buyers** (restaurants, traders, supermarkets, processors, exporters)
- **100 Deals** (50 completed, 20 pending, 15 bargaining, 10 late, 5 rejected)
- **100 Reviews** (bidirectional: farmer→buyer and buyer→farmer for completed deals)
- **120+ Crops** (12 crop types with realistic quantities)

### Test Credentials
- **Farmer Login**: 9900000000 through 9900000039
- **Buyer Login**: 9900000040 through 9900000054

---

## 11. UI/UX Design Philosophy

- **Dark Mode**: Deep navy (#04080f) background with high-contrast text
- **Typography**: Syne (headings, 900 weight) + DM Sans (body text)
- **Color System**: Green (#4ade80) for farmer, Blue (#38bdf8) for buyer, Gold (#fbbf24) for highlights
- **Glassmorphism**: Cards with subtle borders and backdrop blur
- **Micro-animations**: fadeUp, pulse, step-pop, optimistic-pulse
- **Responsive Grid**: Auto-fit columns with minmax() for all screen sizes
- **Voice-First**: Microphone buttons on all input fields for accessibility

---

## 12. Security & Validation

- Phone number uniqueness enforced at database level (UNIQUE constraint)
- Phone format validation (10-digit check on frontend)
- CORS configured for cross-origin requests
- UUID-based identifiers (non-guessable)
- Input validation via Pydantic models on all API endpoints
- Review duplicate prevention (one review per user per deal)
- Deal status guard rails (cannot accept rejected deal, cannot reject accepted deal)

---

## 13. How to Run

```bash
# 1. Start database and backend
docker-compose up --build -d

# 2. Seed demo data
docker-compose exec backend python seed_data.py --reset

# 3. Start frontend
cd frontend
npm install
npm run dev

# 4. Access
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## 14. File Structure

```
KhetIQ/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env
│   ├── seed_data.py
│   ├── reset_db.py
│   └── app/
│       ├── main.py              # FastAPI app entry point
│       ├── config.py            # Environment settings
│       ├── database.py          # SQLAlchemy async engine
│       ├── models/
│       │   ├── farmer.py
│       │   ├── buyer.py
│       │   ├── crop.py
│       │   ├── deal.py
│       │   ├── review.py
│       │   └── recommendations.py
│       ├── routes/
│       │   ├── farmers.py
│       │   ├── buyers.py
│       │   ├── crops.py
│       │   ├── deals.py
│       │   ├── reviews.py
│       │   ├── recommendations.py
│       │   ├── analytics.py
│       │   ├── ai_copilot.py
│       │   └── notifications.py
│       ├── agents/
│       │   └── resilience_agent.py  # Core AI pipeline
│       └── services/
│           ├── gemini_service.py    # Gemini AI integration
│           ├── weather_service.py   # Open-Meteo weather
│           ├── maps_service.py      # Distance & transport
│           ├── apmc_service.py      # Mandi price lookup
│           └── amed_service.py      # Satellite field data
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── src/
        └── App.jsx              # Single-file React application (2565 lines)
```

---

## 15. Future Scope

1. **Payment Gateway Integration** (Razorpay/UPI for in-app payments)
2. **Real-time Chat** between farmer and buyer (WebSocket)
3. **Push Notifications** for deal status changes
4. **Mobile App** (React Native) for field use
5. **Crop Image Analysis** using Gemini Vision for disease detection
6. **Government Scheme Integration** (PM-KISAN, e-NAM linking)
7. **Multi-state Expansion** beyond Karnataka
8. **Blockchain-based Contract Farming** for deal immutability

---

*Report generated for KhetIQ v2.0.0 | May 2026*
