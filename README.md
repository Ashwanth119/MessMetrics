# MessMetrics

**Personalized nutrition intelligence for hostel mess systems.**

MessMetrics is a web application that helps hostel students understand the nutritional value of their mess food, estimate their daily calorie requirements, and track their food consumption.

## Key Features

- Student registration, login, and profile management.
- Hostel-wise mess menu retrieval from the IIT Bombay InstiApp API.
- Nutritional information retrieval using the CalorieNinjas API.
- Personalized BMR and daily calorie requirement estimation.
- Meal tracking and nutritional intake calculation.

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | React 19, Vite |
| Backend | Python, FastAPI |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Data Validation | Pydantic |
| Authentication | JWT, OAuth2 |
| Nutrition API | CalorieNinjas |
| Menu Data Source | IIT Bombay InstiApp API |

## Project Structure

```text
MessMetrics/
│
├── backend-fastapi/
│   ├── app/
│   │   ├── auth.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── router1.py
│   │   └── schemas.py
│   │
│   ├── simple_emotion_pipeline.ipynb
│   ├── .env.example
│   ├── .gitignore
│   ├── create_college_admin.py
│   ├── create_tables.py
│   ├── requirements.txt
│   ├── seed_hostels.py
│   └── seed_roles.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProtectedRoute.jsx
│   │   │   └── Sidebar.jsx
│   │   │
│   │   ├── context/
│   │   │   └── SelectedDateContext.jsx
│   │   │
│   │   ├── layouts/
│   │   │   ├── StudentLayout.css
│   │   │   └── StudentLayout.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Calories.jsx
│   │   │   ├── Dashboard.css
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Menu.css
│   │   │   ├── Menu.jsx
│   │   │   ├── Nutrition.css
│   │   │   ├── Nutrition.jsx
│   │   │   ├── Placeholder.jsx
│   │   │   ├── Profile.jsx
│   │   │   └── Register.jsx
│   │   │
│   │   ├── services/
│   │   │   └── api.js
│   │   │
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── .env.example
│   ├── .gitignore
│   ├── eslint.config.js
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## Code Organization

### Backend

| File | Responsibility |
|---|---|
| `main.py` | FastAPI application entry point and router registration. |
| `auth.py` | Password hashing, authentication, JWT generation, and authorization. |
| `database.py` | PostgreSQL connection, SQLAlchemy engine, and database sessions. |
| `models.py` | SQLAlchemy database models and relationships. |
| `schemas.py` | Pydantic request and response schemas. |
| `router1.py` | API endpoint implementations and application operations. |
| `create_tables.py` | Creates database tables. |
| `seed_hostels.py` | Populates the database with initial hostel records. |
| `seed_roles.py` | Populates the database with application roles. |
| `create_college_admin.py` | Creates the initial college administrator account. |
| `simple_emotion_pipeline.ipynb` | Jupyter notebook containing the emotion detection pipeline. |

### Frontend

| File / Directory | Responsibility |
|---|---|
| `App.jsx` | Application routing and page configuration. |
| `main.jsx` | Frontend entry point and React initialization. |
| `App.css` | Application-level styling. |
| `index.css` | Global styles and theme definitions. |
| `components/` | Reusable components such as sidebar and protected routes. |
| `context/` | Shared application state and React contexts. |
| `layouts/` | Common page layouts. |
| `pages/` | Individual application pages such as Dashboard, Menu, Profile, and Nutrition. |
| `services/api.js` | Communication with the backend API. |

## Getting Started

### Prerequisites

- Python 3.12 or later, compatible with project dependencies.
- Node.js and npm.
- PostgreSQL.
- Git.

### 1. Clone the Repository

```bash
git clone https://github.com/Ashwanth119/MessMetrics.git
cd MessMetrics
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend-fastapi
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create the backend environment file:

```bash
cp .env.example .env
```

Update the `.env` file with your PostgreSQL credentials, JWT secret, and CalorieNinjas API key.

Initialize the database using the provided setup scripts:

```bash
python create_tables.py
python seed_hostels.py
python seed_roles.py
```

Create the initial college administrator account:

```bash
python create_college_admin.py
```

Start the backend server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at [http://localhost:8000](http://localhost:8000).

### 3. Frontend Setup

Open another terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install the dependencies:

```bash
npm install
```

Create the frontend environment file:

```bash
cp .env.example .env
```

Start the frontend development server:

```bash
npm run dev
```

The frontend will be available at [http://localhost:5173](http://localhost:5173).

## Environment Variables

### Backend

The backend requires the following environment variables in `backend-fastapi/.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mess_metrics
DB_USER=your_db_user
DB_PASSWORD=your_db_password

JWT_SECRET_KEY=replace_with_a_secure_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

CALORIE_NINJA_API_KEY=your_calorie_ninja_api_key
```

### Frontend

The frontend requires the following variable in `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

Use `.env.example` as a template for configuring the environment. Do not commit actual `.env` files, database passwords, JWT secrets, or API keys.

**Note:** If the backend runs inside WSL while PostgreSQL runs on the Windows host, update `DB_HOST` to the appropriate Windows host IP address reachable from WSL instead of using `localhost`.

## API Documentation

Interactive API documentation is provided by FastAPI through Swagger UI.

Once the backend is running, access:

[http://localhost:8000/docs](http://localhost:8000/docs)

## License

To be decided.