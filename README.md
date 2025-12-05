# 🌍 Global Climate Risk AI — Real-time Flood, Storm & Heat Forecasting

An intelligence platform that predicts **flood, storm, and heat risk** using:
- Machine Learning (XGBoost)
- 7-day rainfall signal analysis
- Live global disaster alerts (ReliefWeb + GDACS)
- Real-time Open-Meteo weather API

### 🚀 Core Features
| Feature | Technology |
|--------|------------|
| Flood ML Prediction | XGBoost |
| Live Weather Data | Open-Meteo |
| Real Disaster Alerts | ReliefWeb + GDACS |
| Hybrid Risk Engine | ML + Live Intelligence |
| Frontend | Streamlit |
| API Backend | FastAPI |

This system fuses **AI + disaster intelligence** to provide city-level climate risk classification:
``Low — Medium — High``.

---

## 🧠 AI Risk Engine
The risk engine combines:
- Machine learning probability
- Rainfall accumulation
- National disaster alerts
- Local event detection (city)
- Temperature & wind hazard rating

Outputs:
- Flood risk
- Heat risk
- Storm risk
- AI Explanations
- Risk Escalation Logic

---

## ⚡ Run Backend

```bash
cd backend
pip install -r ../requirements.txt
uvicorn main:app --reload
