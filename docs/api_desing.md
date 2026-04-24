# API Endpoints

## OVERVIEW

This document provides a comprehensive list of all API endpoints for the Swiftnote application, categorized by functionality. It includes authentication routes, note management routes, and documentation access points. Each endpoint is described with its HTTP method, URL path, purpose, required payloads, and access level (public or protected). This serves as a reference for both frontend and backend developers to ensure consistent implementation and integration across the application.

## 🔐 AUTHENTICATION ENDPOINTS (PROTECTED)

These endpoints handle the entry points for your users.

| Method | Endpoint | Purpose | Key Payload (Body) |
| :-------- | :---------- | :--------- | :------------------- |
| POST | `/api/auth/register/` | Manual Sign-up | `{ email, password, username }` |
| POST | `/api/auth/verify-email/` | Verify Token | `{ token }` |
| POST | `/api/auth/login/` | Manual Login | `{ email, password }` → Returns Access/Refresh |
| POST | `/api/auth/google/` | Google OAuth | `{ code }` or `{ token_from_google }` |
| POST | `/api/auth/refresh/` | Get new Access Token | `{ refresh_token }` |
| POST | `/api/auth/password-reset/` | Request reset email | `{ email }` |

---

## 📝 NOTES ENDPOINTS (PROTECTED)

These endpoints require a valid JWT Access Token in the header:

```plaintext
Authorization: Bearer <token>
```

### Notes

| Method | Endpoint | Purpose | Query Params |
| :-------- | :---------- | :--------- | :-------------- |
| GET | `/api/notes/` | Retrieve all notes for the logged-in user | `?filter=today`, `?filter=week`, `?category=uuid` |
| POST | `/api/notes/` | Create a new sticky note | — |
| PATCH | `/api/notes/{id}/` | Partial update (content, pin, archive, etc.) | — |
| DELETE | `/api/notes/{id}/` | Move note to trash or permanently delete | — |

### Categories

| Method | Endpoint | Purpose |
| :-------- | :---------- | :--------- |
| GET | `/api/categories/` | Fetch user's custom color categories |
| POST | `/api/categories/` | Create a new category (e.g., "Urgent" with a red hex code) |
| DELETE | `/api/categories/{id}/` | Remove a category |

---

## 📚 DOCUMENTATION ENDPOINTS

These endpoints provide schema access and interactive API documentation.

| Method | Endpoint | Purpose | Access |
| :-------- | :---------- | :--------- | :-------- |
| GET | `/api/schema/` | Download raw OpenAPI schema (YAML/JSON) | Public |
| GET | `/api/schema/swagger-ui/` | Interactive Swagger UI documentation | Public |
| GET | `/api/schema/redoc/` | Alternative Redoc documentation UI | Public |

---
