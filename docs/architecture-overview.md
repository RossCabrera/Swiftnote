# Architecture Overview

## 🎯 OVERVIEW

This document provides a high-level overview of the architecture for the Swiftnote application. It covers the core components, their interactions, and the underlying technologies used to build a scalable and maintainable note-taking platform. The architecture is designed to support user authentication, note management, and a responsive frontend interface while ensuring security and performance.

## 🏗️ ARCHITECTURE COMPONENTS

1. **Frontend (React + TypeScript):** A modern, responsive user interface built with React and TypeScript, utilizing Vite for fast development and Tailwind CSS for styling. It communicates with the backend via REST API calls.
2. **Backend (Django REST Framework):** A robust API layer built with Django REST Framework (DRF) that handles business logic, data management, and authentication. It uses JWT for stateless authentication and integrates with third-party services for email verification and OAuth.
3. **Database (PostgreSQL):** A relational database that stores user data, notes, categories, and authentication tokens. It is designed to support complex queries and ensure data integrity.
4. **Authentication & Authorization:** A secure authentication system that supports both manual registration and Google OAuth, with email verification and password reset functionality.
5. **API Documentation:** Auto-generated OpenAPI documentation using DRF-Spectacular to provide clear and comprehensive API specifications for frontend-backend communication.
6. **State Management:** Zustand is used on the frontend to manage global state, particularly for authentication status and user information, ensuring a seamless user experience across the application.
7. **Email Service (Resend):** A third-party service integrated for sending verification and onboarding emails, ensuring reliable email delivery and management.

## PROJECT STRUCTURE

### 📁 Root Directory

```plaintext
swiftnote/
├── .gitignore            # Crucial: ignore venv/, node_modules/, and .env
├── README.md             # Setup instructions for both projects
├── backend/              # Django REST Framework (DRF) Project
└── frontend/             # React + TypeScript (Vite) Project
```

### 🏗️ Backend Architecture

The backend is built with Django REST Framework (DRF) and follows a modular structure to separate concerns and enhance maintainability.

```plaintext
backend/
├── config/               # Project-wide configuration
│   ├── settings.py       # JWT, Allauth, CORS, and DB settings
│   ├── urls.py           # Main Router: includes api/ and auth/ routes
│   ├── wsgi.py           # Deployment entry point
│   └── asgi.py           # Async entry point
│
├── apps/                 # Custom logic isolated by feature
│   ├── authentication/   # User, OAuth, and Email Verification
│   │   ├── models.py     # Custom User & EmailVerificationToken
│   │   ├── serializers.py# Registration & Login payloads
│   │   ├── views.py      # Auth endpoints (Manual & Google)
│   │   └── urls.py       # Auth-specific routing
│   │
│   └── notes/            # Note & Category management
│       ├── models.py     # Note & Category models
│       ├── serializers.py# Converts models to JSON
│       ├── views.py      # CRUD logic for notes
│       └── urls.py       # Notes-specific routing
│
├── .env                  # Sensitive keys (Google OAuth, DB creds)
├── requirements.txt      # Essential dependencies only
├── manage.py             # Django CLI
└── venv/                 # Local Python environment (Ignored by Git)
```

### ⚛️ Frontend Structure

The frontend is built with React and TypeScript using Vite for fast development. It follows a component-based architecture.

```plaintext
frontend/
├── public/               # Static assets (Favicons, etc.)
│
├── src/
│   ├── api/              # Centralized Axios instances
│
│   ├── components/       # Shared UI components
│   │   ├── layout/       # WRAPPERS: Sidebar, Navbar, AuthLayout
│   │   └── ui/           # REUSABLES: Buttons, Inputs, Modals
│   ├── features/         # Logic grouped by functional area
│   │   ├── auth/         # Login/Register logic & hooks
│   │   └── notes/        # Note grid & Category filtering
│   ├── pages/            # View components (Home, Login, Workspace)
│   ├── store/            # Zustand state management (JWT/User)
│   ├── routes/           # Protected & Public routing
│   ├── types/            # TypeScript interfaces (User, Note)
│   └── App.tsx           # Root component
│
├── .env                  # VITE_API_URL=http://localhost:8000
├── package.json          # Node dependencies
└── node_modules/         # Local JS libraries (Ignored by Git)
```

## TECH STACK SUMMARY

### 🐍 Backend (Django + DRF)

The backend is built with **Django REST Framework (DRF)** to create a modular, secure, and scalable API.

- **Django REST Framework (DRF):** Core API layer for REST communication between frontend and backend.
- **PostgreSQL:** Production-grade relational database for reliability and scalability.
- **JWT Authentication:** Stateless auth using access + refresh tokens for secure requests.
- **Django Allauth + dj-rest-auth:** Handles authentication flows like manual sign-up and Google OAuth.
- **Resend:** Email service for verification and onboarding emails.
- **DRF-Spectacular:** Auto-generates OpenAPI 3.0 documentation for API endpoints.

---

### 🎨 Frontend (React + TypeScript)

The frontend is a modern **React + TypeScript** app built with **Vite** for speed and simplicity.

- **React + TypeScript:** Strongly typed, scalable UI architecture.
- **Tailwind CSS:** Utility-first styling for a clean, minimal productivity UI.
- **Zustand:** Lightweight global state management (auth state, user session).
- **Axios:** Handles API requests and JWT authentication headers.
- **TanStack Query:** Manages server state (especially notes caching and syncing).
- **Lucide React:** Icon library for modern UI icons.
- **date-fns:** Utility for formatting dates and timestamps.

---

## 💡 Why this stack?

- **Separation of concerns:** Frontend and backend are fully decoupled via REST API.
- **Scalability:** Modular structure supports growth (auth, notes, search, archiving, etc.).
- **Real-world architecture:** Mirrors production apps with JWT auth + OAuth flows.
- **Maintainability:** Organized by features for long-term extensibility.

---
