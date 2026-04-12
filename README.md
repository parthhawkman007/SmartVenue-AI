# 🚀 SmartVenue AI

### Real-Time Crowd Intelligence & Safety Management System

---

## 📌 Overview

SmartVenue AI is an intelligent, cloud-native platform designed to monitor, analyze, and optimize crowd behavior in real-time during large-scale events such as Formula 1 races, stadium matches, concerts, and public gatherings.

By combining real-time simulation, AI-driven insights, and secure role-based control, the system enables event organizers to proactively manage crowd density, prevent overcrowding, and improve safety.

---

## 🎯 Problem Statement

Large events often face:

* Overcrowding in critical zones
* Delayed response to crowd surges
* Lack of real-time decision support
* Inefficient manual monitoring systems

SmartVenue AI solves these challenges through automation, AI intelligence, and scalable cloud infrastructure.

---

## ✨ Key Features

### 📊 Real-Time Dashboard

* Live crowd density monitoring across multiple zones
* Visual classification (Low / Moderate / Very Crowded)
* Dynamic updates using Live Sync

---

### ⚡ AI-Powered Insights (Gemini Integration)

* Intelligent alert generation
* Context-aware recommendations
* Tactical field instructions for crowd management

---

### 🚨 Serious Alerts System

* Detects critical overcrowding zones
* Provides immediate rerouting suggestions
* Enables proactive safety measures

---

### 🔁 Live Simulation Engine

* Simulates real-world crowd surge scenarios
* Updates system every 5 seconds
* Helps test system response under pressure

---

### 🔐 Secure Authentication & Role System

* Firebase Authentication (Email + Google Login)
* Role-based access (Admin / User)
* Admin-only system control features

---

### 👥 User Management (Admin Panel)

* View all registered users
* Promote/Demote roles
* Controlled system access

---

### 🌍 Cloud Environment Monitoring

* Event phase tracking (e.g., Mid-Race Pit Cycles)
* Weather conditions (temperature, humidity)
* Context-aware decision support

---

## 🏗️ System Architecture

```text
Frontend (SPA - Vanilla JS)
        ↓
Firebase Authentication + Firestore
        ↓
Backend API (FastAPI - Cloud Run)
        ↓
AI Engine (Google Gemini)
```

---

## 🛠️ Tech Stack

### Frontend

* HTML, CSS, Vanilla JavaScript (SPA Architecture)

### Backend

* FastAPI (Python)
* REST APIs

### Database

* Firebase Firestore

### Authentication

* Firebase Authentication (Email + Google OAuth)

### Cloud & Deployment

* Google Cloud Run (Backend)
* Firebase Hosting (Frontend)

### AI Integration

* Google Gemini (gemini-1.5-flash)

---

## ⚡ Performance & Optimization

* Parallel API execution using `Promise.all()`
* AI response caching (5% density rounding)
* Asynchronous processing pipeline
* Low-latency real-time updates

---

## 🔐 Security

* JWT-based request validation
* Role-based access control (RBAC)
* Admin-only protected endpoints
* Secure environment variable handling

---

## 🧪 Testing Approach

* Real-time simulation testing (crowd surge scenarios)
* Edge-case handling (API fallback, AI timeout)
* Manual QA across roles and views

---

## 🚀 Deployment

### Backend (Cloud Run)

```bash
gcloud run deploy smartvenue-api --source . --region asia-south1
```

### Frontend (Firebase Hosting)

```bash
firebase deploy --only hosting
```

---

## 🔗 Live Demo

* 🌐 Frontend: https://smart-experience-ai.web.app
* ⚙️ Backend API: https://smartvenue-api-xxxx.run.app

---

## 📸 Screenshots

* Dashboard (Live Monitoring)
* AI Insights Panel
* Alerts System
* Admin Control Panel

---

## 🌍 Real-World Impact

SmartVenue AI can be deployed in:

* Sports stadiums (Formula 1, Football)
* Concerts & festivals
* Public transport hubs
* Smart cities

It enables **data-driven decision making**, improves **crowd safety**, and reduces **operational risks**.

---

## 🚀 Future Enhancements

* Mobile application (Flutter)
* IoT sensor integration
* Predictive analytics using ML models
* Notification system (SMS / Push alerts)
* Advanced visualization dashboards

---

## 👨‍💻 Author

**Parth Bhardwaj**
Built as part of a hackathon project focusing on AI + Cloud + Real-Time Systems

---

## ⭐ Final Note

This project demonstrates how AI and cloud technologies can transform traditional crowd management into an intelligent, proactive, and scalable system.

---
