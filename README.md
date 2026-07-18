# 🩺 MediLens

**AI-Powered Medical Report Analyzer**

MediLens is a web application that helps users understand their medical reports in simple, easy-to-read language. Users can upload a blood test report (PDF or image), and the application extracts the report data, analyzes it using AI, and provides clear explanations with general health insights.

> Disclaimer: MediLens is for educational purposes only and does **not** provide medical diagnoses or replace professional medical advice.

---

## ✨ Features

- 📄 Upload medical reports (PDF/Image)
- 🔍 Automatic text extraction (PDF Parser & OCR)
- 🤖 AI-powered report analysis
- ✅ Highlights Normal, Borderline, and Abnormal values
- 📚 Explains each medical parameter in simple language
- 💡 General lifestyle recommendations
- 📂 Report history
- 📊 Dashboard with report summaries
- 📱 Responsive UI
- 🌙 Dark Mode

---

## 🛠️ Tech Stack

### Frontend
- React

### Backend
- Node.js
- Express.js

### Database
- MongoDB

### AI
- Google Gemini API / OpenAI API

### Document Processing
- Tesseract OCR
- PDF Parser

---

## 🔄 Project Workflow

```text
User Uploads Report
        │
        ▼
Frontend
        │
        ▼
Backend
        │
        ▼
Document Processing
(PDF Parsing + OCR)
        │
        ▼
AI Analysis
        │
        ▼
Database Storage
        │
        ▼
Frontend Dashboard
```

---

## 📁 Project Structure

```text
MediLens/
├── frontend/
├── backend/
├── docs/
├── README.md
└── .gitignore
```

---

## 🚀 Future Enhancements

- Compare previous reports
- Trend analysis and graphs
- Multi-language support
- Voice explanation
- Download AI-generated summary
- Email report summaries

---

## ⚠️ Disclaimer

MediLens is intended for educational and informational purposes only. It does not provide medical diagnoses, treatment recommendations, or professional healthcare advice. Always consult a qualified healthcare professional for medical concerns.