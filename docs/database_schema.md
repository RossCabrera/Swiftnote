# 🔗 Database Schema - Entity Relationship Diagram

## 🎯 OVERVIEW

This is the complete database schema for Swiftnote application with authentication, email verification, password reset, categories, and notes.

## 📊 ERD DIAGRAM

```mermaid
---
id: b74f9644-e3e1-49bf-bc6b-4e3012ae4d09
---
erDiagram
  USER ||--o{ EMAIL_VERIFICATION_TOKEN : "verifies"
  USER ||--o{ PASSWORD_RESET_TOKEN : "resets"
  USER ||--o{ CATEGORY : "owns"
  USER ||--o{ NOTE : "creates"
  CATEGORY o|--o{ NOTE : "categorizes"
  
  USER {
    uuid id PK
    string email UK
    string username
    string password 
    first_name string
    last_name string
    string avatar_url 
    boolean is_verified
    boolean is_active
    boolean is_staff
    boolean is_superuser
    datetime last_login
    datetime date_joined
  }
  
  EMAIL_VERIFICATION_TOKEN {
    uuid id PK
    uuid user_id FK
    string token UK
    datetime creates_at
    datetime expires_at
    boolean is_used
  }
  
  PASSWORD_RESET_TOKEN {
    uuid id PK
    uuid user_id FK
    string token UK
    datetime created_at
    datetime expires_at
    boolean is_used
  }
  
  CATEGORY {
    uuid id PK
    uuid user_id FK
    string name
    string color_hex
  }
  
  NOTE {
    uuid id PK
    uuid user_id FK
    uuid category_id FK "Nullable"
    string title
    text content
    datetime created_at
    datetime updated_at
    boolean is_archived
  }
```

---

## 🔑 KEY RELATIONSHIPS

- **User to EmailVerificationToken**: One-to-Many (1:N) - A user can have multiple verification tokens over time, but each token belongs to one user.
- **User to PasswordResetToken**: One-to-Many (1:N) - A user can request multiple password resets, but each token is associated with one user.
- **User to Category**: One-to-Many (1:N) - A user can create multiple categories, but each category belongs to one user.
- **User to Note**: One-to-Many (1:N) - A user can create multiple notes, but each note belongs to one user.
- **Category to Note**: One-to-Many (1:N) - A category can  contain multiple notes, but each note can belong to only one category (or none).

---
