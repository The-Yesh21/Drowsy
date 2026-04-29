# 🚗 Automated Drowsiness Detection System

> **AI-Powered Real-Time Driver Safety Platform** | Computer Vision + Full-Stack Web Application

A production-grade drowsiness detection system combining advanced computer vision, asynchronous backend infrastructure, and an intuitive analytics dashboard. Designed for fleet management, insurance companies, and transportation platforms.

## 📊 System Overview

### Problem Statement
Driver fatigue causes ~20% of fatal road accidents. This system provides **real-time drowsiness detection** with AI-powered safety insights to prevent accidents before they happen.

### Solution Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Computer      │────▶│   FastAPI        │────▶│   React          │
│   Vision Engine │     │   Backend        │     │   Dashboard      │
│  (OpenCV +      │     │  (JWT + MongoDB) │     │  (Real-time      │
│   MediaPipe +   │     │  + WebSockets    │     │   Analytics)     │
│   ONNX Model)   │     │  + Gemini AI     │     │  (Tailwind)      │
└─────────────────┘     └──────────────────┘     └──────────────────┘
         ▲                      ▲                         ▲
         │                      │                         │
         └──────────────────────┴─────────────────────────┘
               Real-time Telemetry & Control Flow
```

## ✨ Key Features

| Feature | Details |
|---------|---------|
| 🎯 **Real-Time Detection** | Eye Aspect Ratio (EAR), Mouth Aspect Ratio (MAR), head pose tracking |
| 🤖 **AI-Powered Insights** | Google Gemini 1.5 for safety risk analysis & trip summaries |
| 📡 **Live WebSocket Broadcasting** | Sub-100ms latency real-time data streaming |
| 🔐 **Enterprise Security** | JWT authentication, role-based access control |
| 📈 **Advanced Analytics** | Multi-chart dashboards with historical trend analysis |
| 🔄 **Async Architecture** | Non-blocking I/O for high throughput |
| ☁️ **Cloud-Ready** | MongoDB Atlas, containerizable with Docker |
| 📱 **Responsive UI** | Mobile-friendly React dashboard with Recharts |

## 🏗️ Architecture Layers

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Stage 1: Vision Engine** | Python, OpenCV, MediaPipe, ONNX | Real-time facial analysis & drowsiness inference |
| **Stage 2: Backend API** | FastAPI, MongoDB, WebSockets, Gemini AI | Data persistence, authentication, AI analysis |
| **Stage 3: Frontend** | React 19, Vite, Tailwind CSS, Recharts | Real-time dashboard & user interface |
| **Stage 4: Integration** | Async subprocess management | Seamless cross-platform orchestration |

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance async web framework
- **MongoDB Atlas** - Cloud database with real-time sync
- **Motor** - Async MongoDB driver
- **WebSockets** - Real-time bidirectional communication
- **JWT (Jose)** - Secure authentication
- **Google Generative AI** - AI-powered safety analysis

### Frontend
- **React 19** - Modern UI library
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Responsive data visualization
- **Zustand** - Lightweight state management
- **Axios** - HTTP client

### Computer Vision
- **OpenCV** - Image processing
- **MediaPipe** - Facial landmark detection
- **ONNX Runtime** - ML model inference
- **NumPy** - Numerical computing

---

## 📋 Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.10+** - [Download](https://www.python.org/downloads/)
- ✅ **Node.js 18+** - [Download](https://nodejs.org/)
- ✅ **MongoDB Atlas Account** - [Create Free Cluster](https://www.mongodb.com/cloud/atlas/register)
- ✅ **Google Gemini API Key** - [Get API Key](https://ai.google.dev/)
- ✅ **Git** - For version control

---

## 🚀 Quick Start Guide

### Step 1️⃣ Clone & Setup Repository

```bash
git clone https://github.com/yourusername/drowsy-detection.git
cd drowsy-detection
```

### Step 2️⃣ Configure Environment Variables

**Backend Configuration** (`backend/.env`):
```env
MONGODB_URL="mongodb+srv://USERNAME:PASSWORD@cluster.mongodb.net/?appName=Cluster0"
DB_NAME=drowsiness_detector
GEMINI_API_KEY=your_google_gemini_api_key_here
JWT_SECRET=your_super_secret_jwt_key_change_in_production
JWT_EXPIRE_MINUTES=1440
```

**Frontend Configuration** (`dashboard/.env`):
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

> 💡 **Tip**: To find your MongoDB credentials, go to MongoDB Atlas → Connect → Drivers and copy the connection string. Remember to URL-encode special characters (e.g., `@` → `%40`).

### Step 3️⃣ Install Dependencies

**Backend Setup:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend Setup:**
```bash
cd dashboard
npm install
```

---

## 🏃 Running the Application

### Terminal 1: Start Backend Server
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Started reloader process [XXXX]
```

### Terminal 2: Start Frontend Development Server
```bash
cd dashboard
npm run dev
```

**Expected Output:**
```
  VITE v5.0.0  ready in XXX ms

  ➜  Local:   http://localhost:5173/
```

### 🌐 Access the Application

1. Open your browser to **http://localhost:5173**
2. **Register** a new account or login
3. Click **"Start Session"** to begin monitoring
4. See real-time drowsiness metrics update live
5. Click **"End Session"** to generate AI safety report

---

## 📊 Usage Walkthrough

### Dashboard Features

| Page | Purpose |
|------|---------|
| **Login/Register** | User authentication & account management |
| **Dashboard** | Real-time drowsiness metrics & live charts |
| **Analytics** | Historical data, trends, and performance insights |
| **Sessions** | Past trip logs with AI-generated safety reports |
| **Settings** | User preferences & account configuration |

### Real-Time Metrics Displayed

- 👁️ **Eye Aspect Ratio (EAR)** - Eye closure detection
- 👄 **Mouth Aspect Ratio (MAR)** - Yawn detection
- 🔄 **Blink Rate** - Blink frequency analysis
- 📍 **Head Pose** - Head movement & nod detection
- ⚠️ **Risk Score** - AI-computed drowsiness probability
- ⏱️ **Session Duration** - Total monitoring time

---

## 🚀 Deployment

### ⭐ Recommended: Railway.app (Backend) + Vercel (Frontend)

**The fastest way to production!**

| Platform | Use Case | Cost | Setup Time |
|----------|----------|------|-----------|
| **Railway.app** | FastAPI Backend | $5-20/month | 15 min |
| **Vercel** | React Frontend | Free-$20/month | 10 min |
| **MongoDB Atlas** | Database | Free-$57/month | Already set up |

### 🎯 Quick Deploy (30 minutes)

**Step 1: Deploy Backend to Railway**
```bash
# 1. Push code to GitHub
git add . && git commit -m "Ready for deployment" && git push

# 2. Go to railway.app/dashboard
# 3. Click "Create New" → "Deploy from GitHub"
# 4. Select your repository
# 5. Add environment variables (MONGODB_URL, GEMINI_API_KEY, etc.)
# 6. Wait 2-5 minutes for deployment ✅
```

**Step 2: Deploy Frontend to Vercel**
```bash
# 1. Go to vercel.com/dashboard
# 2. Click "Add New Project"
# 3. Import your GitHub repository
# 4. Set root directory: dashboard
# 5. Add environment variables:
#    VITE_API_URL=https://your-railway-app.up.railway.app
#    VITE_WS_URL=wss://your-railway-app.up.railway.app
# 6. Deploy ✅
```

### 📖 Complete Deployment Guide

For detailed step-by-step instructions with troubleshooting, see [**DEPLOYMENT.md**](./DEPLOYMENT.md)

**Includes:**
- ✅ Environment variable setup
- ✅ Health checks & monitoring
- ✅ Custom domains (optional)
- ✅ Troubleshooting guide
- ✅ Security best practices
- ✅ Cost optimization

---

### Other Deployment Options

| Option | Backend | Frontend | Best For |
|--------|---------|----------|----------|
| **Railway + Vercel** | Railway | Vercel | 🏆 Recommended |
| **Docker + AWS** | EC2/ECS | S3+CloudFront | Advanced users |
| **Heroku** | Heroku | Vercel | Legacy choice |
| **Self-hosted** | VPS | VPS | Full control |

### Option 3: Docker + Any Cloud (AWS, GCP, Digital Ocean)

**Create Dockerfile for Backend:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Deploy:**
```bash
docker build -t drowsy-backend .
docker push your-registry/drowsy-backend:latest
```

### Complete Deployment Checklist

- [ ] Push code to GitHub
- [ ] Remove all hardcoded secrets
- [ ] Create production `.env` files
- [ ] Configure CORS for production domain
- [ ] Set up MongoDB backups
- [ ] Enable HTTPS/SSL
- [ ] Configure API rate limiting
- [ ] Set up monitoring & logging
- [ ] Test all features in production

---

## 📁 Project Structure

```
drowsy-detection/
├── backend/                      # FastAPI backend
│   ├── models/                   # Database schemas
│   ├── routers/                  # API endpoints
│   ├── services/                 # Business logic
│   ├── main.py                   # FastAPI app
│   ├── database.py               # MongoDB setup
│   ├── config.py                 # Configuration
│   └── requirements.txt           # Python dependencies
│
├── dashboard/                    # React frontend
│   ├── src/
│   │   ├── components/           # UI components
│   │   ├── pages/                # Page components
│   │   ├── store/                # Zustand state
│   │   ├── api/                  # API client
│   │   └── hooks/                # Custom hooks
│   └── package.json              # Node dependencies
│
├── detector/                     # Computer vision
│   ├── face_mesh.py              # MediaPipe integration
│   ├── metrics.py                # EAR, MAR calculations
│   ├── ensemble.py               # ONNX inference
│   └── models/
│       └── model.onnx            # Trained model
│
├── training/                     # Model training pipeline
│   ├── train.py                  # Training script
│   ├── evaluate.py               # Evaluation metrics
│   └── export_onnx.py            # Model export
│
├── main.py                       # Local detector entry point
├── config.py                     # Root configuration
└── README.md                     # This file
```

---

## 🔒 Security Best Practices

- ✅ Use environment variables for all secrets
- ✅ Enable HTTPS in production
- ✅ Implement rate limiting on APIs
- ✅ Use strong JWT secrets
- ✅ Enable CORS only for trusted domains
- ✅ Validate all user inputs
- ✅ Keep dependencies updated
- ✅ Use MongoDB IP whitelisting

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Clear cache
rm -rf backend/__pycache__

# Reinstall dependencies
cd backend && pip install -r requirements.txt --force-reinstall

# Check MongoDB connection
python -c "from config import settings; print(settings.MONGODB_URL)"
```

### Frontend not connecting to backend
```bash
# Check environment variables in dashboard/.env
cat dashboard/.env

# Ensure backend is running on port 8000
lsof -i :8000
```

### ONNX model errors
```bash
# Verify model exists
ls -la detector/models/model.onnx

# Reinstall ONNX Runtime
pip install onnxruntime --upgrade
```

---

## 📚 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MediaPipe Facial Mesh Guide](https://developers.google.com/mediapipe/solutions/vision/face_landmarker)
- [React 19 Docs](https://react.dev/)
- [MongoDB Atlas Guide](https://docs.atlas.mongodb.com/)
- [Gemini API Quickstart](https://ai.google.dev/tutorials/quickstart)

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Quality Standards
- Python: Follow PEP 8, use type hints
- JavaScript: Use ESLint configuration provided
- Maintain 80%+ test coverage
- Document all public functions

---

## 📄 License

This project is licensed under the **MIT License** - see the LICENSE file for details.

---

## 👨‍💼 Author

**Yeshwanth** - Full-Stack Developer  
- 🔗 [LinkedIn](www.linkedin.com/in/the-yesh21)
- 🐙 [GitHub](https://github.com/The-Yesh21)
- 📧 [Email](mailto:yeshwanth9750@gmail.com)

---

## 🙏 Acknowledgments

- **MediaPipe** - Facial landmark detection
- **Google Gemini** - AI safety analysis
- **MongoDB** - Database infrastructure
- **React & Vite** - Frontend ecosystem

---

## ⭐ Show Your Support

If this project helped you, please consider giving it a star! It motivates us to continue improving.

```
Made with ❤️ for safer driving
```
