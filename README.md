# SmartVenue AI

Real-time crowd intelligence and safety management for large events such as Formula 1 races, football matches, concerts, and public gatherings.

## Overview

SmartVenue AI combines live crowd simulation, secure role-based controls, and Gemini-powered recommendations to help operators monitor venue pressure, detect risk zones, and respond faster to crowd surges.

## Features

- Live dashboard for crowd density and trend monitoring
- Alerts feed for high-risk zones
- AI insights powered by Google Gemini
- Event environment panel with contextual conditions
- Admin controls for starting, stopping, and simulating venue activity
- Firebase Authentication with role-based access control

## Architecture

```text
Frontend (Vanilla JS SPA)
        ->
Firebase Authentication
        ->
FastAPI Backend
        ->
Firestore + Gemini
```

## Tech Stack

- Frontend: HTML, CSS, Vanilla JavaScript
- Backend: FastAPI, Pydantic
- Database: Firestore
- Authentication: Firebase Authentication
- Hosting: Firebase Hosting
- Compute: Google Cloud Run
- AI: Gemini 1.5 Flash

## Security

- Bearer-token verification on backend routes
- Firebase custom claims for admin authorization
- Deny-by-default Firestore security rules
- Admin-only write access for system state and crowd data

## Testing

Backend tests are written with `pytest` and `fastapi.testclient`.

Covered scenarios include:

- health and root endpoints
- unauthorized and forbidden access paths
- admin route validation
- mocked Firestore failures
- integration flow for environment, crowd, alerts, and insights

## Deployment

### Backend

```bash
gcloud run deploy smartvenue-api --source . --region asia-south1
```

### Frontend

```bash
firebase deploy --only hosting
```

## Firebase Configuration

- Hosting public directory: `frontend`
- Firestore region: `asia-south1`
- Firestore rules file: `firestore.rules`

## Project Structure

```text
backend/
  app.py
  core/
  firestore/
  models/
  routes/
  services/
  tests/
frontend/
  index.html
  app.js
public/
  index.html
  app.js
```

## Future Improvements

- frontend module split for easier maintenance
- end-to-end UI tests
- structured application logging output
- Firestore emulator-backed integration tests
