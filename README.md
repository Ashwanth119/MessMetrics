# MessMetrics

**Personalized nutrition intelligence for hostel mess systems.**

MessMetrics is a full-stack web application that turns a hostel's weekly mess menu into personalized, day-by-day eating guidance for every student, and gives the mess council hard data to improve the menu over time.

---

https://calorieninjas.com/profile
for the calories

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Disclaimer](#disclaimer)

---

## Overview

### The problem

Hostel messes feed thousands of students every day. Students with different bodies, goals, and dietary restrictions all get the same menu.

### The solution

MessMetrics does not try to change what the mess cooks. Instead, it:

1. **Ingests the weekly menu** by scraping the hostel website, with a manual upload option for mess council members when the scraped data is missing or outdated.
2. **Maps every dish to a nutritional profile** using Indian food composition data, with a human review step for uncertain matches.
3. **Guides each student** on what to eat from the existing menu, based on their body, goals, and dietary restrictions.
4. **Gives the mess council an aggregate dashboard** that turns vague complaints into measurable evidence for menu reform.

## Key Features

### Menu data pipeline

- Scheduled scraping of the weekly menu from the hostel website, with change detection
- Manual menu upload by admins (spreadsheet, PDF, or photo) and a manual entry grid as a fallback
- Manual upload overrides scraped data for that week
- Preview, edit, and Draft to Published workflow before students see anything
- Version history with rollback, and "last updated" and source labels on every menu
- Scrape failure alerts and stale-data warnings

### Dish and nutrition mapping

- Automatic matching of menu items to canonical dishes and nutrition profiles
- Handles spelling variants and mixed-language dish names
- Confidence scores with an admin review queue for low-confidence matches
- Standard serving sizes (katori, ladle, piece) and "estimated" labels where data is not verified

### Student features

- Campus email login and onboarding profile (body metrics, goal, diet type, allergies)
- Calorie and macro targets calculated from the profile
- **Daily plan** per meal: what to take, how much, and what to limit
- **Weekly view** with good-day / tough-day indicators
- Gap suggestions when the mess menu falls short on protein, fibre, or other nutrients
- Quick meal logging and planned vs. actual tracking
- Dish ratings and feedback tags, plus reporting of incorrect menu data
- Email reminders and weekly digest

### Mess council and admin features

- Menu status dashboard (current week, source, freshness)
- Aggregate nutrition analytics compared against recommended levels
- Gap analysis, for example "protein is below target on 4 of 7 days"
- Feedback clustering by dish and meal, with trends over time
- "What if" menu reform simulator
- Exportable PDF and CSV reports for the warden and administration
- **Privacy by design:** admins only see aggregated, anonymized data, never an individual student's records

### Platform

- Role-based access (student, admin, super admin)
- Audit log of menu and data changes
- Multi-hostel ready data model
- Responsive, mobile-first website

---

## Tech Stack

### Frontend - React

### Backend - FastAPI

### Data and ingestion - Website scraping, Spreadsheets, PDFs

### Database and storage - PostgreSQL

### DevOps - Docker, GitHub

---

## Project Structure

```
messmetrics/
├── README.md
├── docker-compose.yml
├── .env.example
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── frontend/                      # Next.js app
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/            # login, register
│   │   │   ├── (student)/         # dashboard, plan, log, weekly, profile
│   │   │   └── (admin)/           # menus, review queue, analytics, reports
│   │   ├── components/            # shared and feature UI components
│   │   ├── lib/                   # API client, utilities, validators
│   │   └── hooks/                 # custom React hooks
│   └── public/
│
├── backend/                       # FastAPI app
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/                   # database migrations
│   ├── app/
│   │   ├── main.py                # app entry point
│   │   ├── core/                  # config, security, dependencies
│   │   ├── api/                   # route handlers (auth, menus, plans, logs, admin)
│   │   ├── models/                # SQLAlchemy models
│   │   ├── schemas/               # Pydantic schemas
│   │   ├── services/
│   │   │   ├── ingestion/         # scraper, spreadsheet/PDF/photo parsers
│   │   │   ├── normalization/     # LLM menu normalization
│   │   │   ├── nutrition/         # dish matching and nutrition mapping
│   │   │   ├── personalization/   # targets, filters, plan optimizer
│   │   │   └── analytics/         # aggregate stats, gap analysis
│   │   ├── workers/               # background jobs and schedulers
│   │   └── db/                    # session and base setup
│   └── tests/
│
├── data/
│   ├── nutrition/                 # IFCT / USDA source data and loaders
│   └── samples/                   # sample menus in different formats
│
└── docs/
    ├── architecture.md
    ├── database-schema.md
    └── api.md
```

---

## Getting Started

> Setup steps will be finalized as the project takes shape. The intended workflow is:



| Service            | URL                        |
| ------------------ | -------------------------- |
| Frontend           | -                          |
| Backend API        | -                          |
| API docs (Swagger) | -                          |

---

## Disclaimer

MessMetrics provides general nutrition guidance based on standard formulas and food composition data. It is **not medical advice**. Students with medical conditions should consult a qualified healthcare professional. Nutrition values for some dishes are estimates.

---

## License

To be decided.
