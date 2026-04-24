# 📌 User Stories & Acceptance Criteria

## 🧠 OVERVIEW

This document outlines the core user stories and acceptance criteria for our note-taking application. It serves as a blueprint for development, ensuring that all features align with user needs and business goals. The user stories are categorized into three main modules: Authentication & Identity, Note Management, and Navigation & Discovery. Each user story is accompanied by specific acceptance criteria to guide implementation and testing.

## 🧩 USER STORIES

### 🔐 Authentication & Identity

| User Story ID | Module | Title | Requirement | User Story | Purpose |
| :--------------- | :-------- | :------ | :------------- | :------------ | :--------- |
| US-AUTH-01 | Authentication & Identity | Manual Registration | Account Creation | As a new user, I want to create an account using my email and password | To have a private, secure space for notes. |
| US-AUTH-02 | Authentication & Identity | Email Verification | Account Activation | As a registered user, I want to click a link in my email to verify my account | To gain full access to application features. |
| US-AUTH-03 | Authentication & Identity | Google OAuth | Social Login | As a user, I want to sign in using my Google account | To skip manual registration and password management. |
| US-AUTH-04 | Authentication & Identity | Password Reset | Recovery Flow | As a user who forgot my password, I want to request a reset link via email | To securely regain access without losing data. |

---

### 📝 Note Management

| User Story ID | Module | Title | Requirement | User Story | Purpose |
| :--------------- | :-------- | :------ | :------------- | :------------ | :--------- |
| US-NOTE-05 | Note Management | Note Management | CRUD Operations | As a logged-in user, I want to create, edit, and delete notes | To capture and manage thoughts in real-time. |
| US-NOTE-06 | Note Management | Categorization | Visual Org | As a user, I want to group notes into color-coded categories | To visually distinguish between task types. |

---

## 🧭 Navigation & Discovery

| User Story ID | Module | Title | Requirement | User Story | Purpose |
| :--------------- | :-------- | :------ | :------------- | :------------ | :--------- |
| US-NAV-07 | Navigation & Discovery | Time Filtering | Navigation | As a busy user, I want to filter notes by "Today," "Week," or "Month" | To quickly find relevant notes based on time. |

## ✅ ACCEPTANCE CRITERIA

### 🔐 Authentication & Identity

| Acceptance Criteria ID | User Story ID | Module | Requirement | Description |
| :------------------------ | :--------------- | :-------- | :------------- | :------------- |
| AC-AUTH-01 | US-AUTH-01 | Authentication & Identity | Data Validation | System must validate proper email format. |
| AC-AUTH-02 | US-AUTH-01 | Authentication & Identity | Security | Passwords must be hashed; no plain-text storage allowed. |
| AC-AUTH-03 | US-AUTH-01 | Authentication & Identity | Onboarding | Account is set to "Inactive" until email is verified. |
| AC-AUTH-04 | US-AUTH-02 | Authentication & Identity | Token Security | Verification link must use a secure, time-limited token. |
| AC-AUTH-05 | US-AUTH-02 | Authentication & Identity | State Change | Successful clicks must transition user status to "Active". |
| AC-AUTH-06 | US-AUTH-03 | Authentication & Identity | Auth Integration | System must securely redirect to Google consent screen. |
| AC-AUTH-07 | US-AUTH-03 | Authentication & Identity | Session Management | Backend must issue JWT (Access/Refresh) upon success. |
| AC-AUTH-08 | US-AUTH-04 | Authentication & Identity | Security | Reset links must be one-time-use and time-limited. |
| AC-AUTH-09 | US-AUTH-04 | Authentication & Identity | Enumeration | System must not reveal if an email exists in the DB. |
| AC-AUTH-10 | US-AUTH-03 | Authentication & Identity | OAuth Avatar | System must extract and save the picture URL from the Google OAuth payload. |
| AC-AUTH-11 | US-AUTH-01 | Authentication & Identity | Manual Avatar | For manual users, the system must set avatar_url to null by default. |
| AC-AUTH-12 | US-AUTH-05 | Authentication & Identity | Avatar Display | UI must show the Google image if available; otherwise, generate a colored circle with user initials. |
| AC-AUTH-15 | US-AUTH-01 / US-AUTH-03 | Authentication & Identity | Identity Convergence | The system must use the email as the unique user identifier. A single account must exist per email, regardless of registration method. |
| AC-AUTH-16 | US-AUTH-01 | Authentication & Identity | Google → Manual Conflict | If a user registered via Google attempts manual registration with the same email, the system must block the action and prompt: "Account already exists. Log in with Google or reset your password." |
| AC-AUTH-17 | US-AUTH-03 | Authentication & Identity | Manual → Google Linking | If a user with an existing manual account signs in with Google using the same email, the system must link the Google account and grant access to existing data. |

---

### 📝 Note Management

| Acceptance Criteria ID | User Story ID | Module | Requirement | Description |
| :------------------------ | :--------------- | :-------- | :------------- | :------------- |
| AC-NOTE-01 | US-NOTE-05 | Note Management | Data Structure | Notes must include Title, Description, and Timestamps. |
| AC-NOTE-02 | US-NOTE-05 | Note Management | Privacy | Users can only access/modify notes they created. |
| AC-NOTE-03 | US-NOTE-06 | Note Management | Customization | Users can define category titles and hex colors. |

---

### 🧭 Navigation & Discovery

| Acceptance Criteria ID | User Story ID | Module | Requirement | Description |
| :------------------------ | :--------------- | :-------- | :------------- | :------------- |
| AC-NAV-01 | US-NAV-07 | Navigation & Discovery | Backend Logic | Filters must utilize `created_at` or `updated_at` timestamps. |
| AC-NAV-02 | US-NAV-07 | Navigation & Discovery | UX | UI must update note lists instantly (no refresh). |
