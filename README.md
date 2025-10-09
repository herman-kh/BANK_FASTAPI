# API of Microservices  

## Requirements  
- Docker & Docker Compose  
- Python 3.12+  
- PostgreSQL  

## Project Description  
The project uses a **microservice architecture** with three main services:  

1. **Auth Service** (Authentication) - port 8001  
2. **Message Service** (Email & notifications) - port 8002  
3. **Balance Service** (User balances management) - port 8003  

All requests go through an **Nginx reverse proxy** on port **8000**.  

### 🌐 Base URL  
http://localhost:8000  

### 📊 URL Structure  
http://localhost:8000/{service}/{endpoint}  

---

## Environment Variables  

Create `.env` files inside each service directory with the following variables:  

### Auth Service (.env)  
```env
DB_HOST=auth_db
DB_PORT=5432
DB_NAME=users
DB_USER=amin
DB_PASSWORD=my_super_password

SECRET_KEY=your_secret_key
REFRESH_TOKEN_SECRET_KEY=your_secret_key_for_refresh_token

JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60000000
JWT_REFRESH_DAYS=30

KAFKA_BOOTSTRAP_SERVERS=kafka:29092
KAFKA_USER_CREATED_TOPIC=user_created
KAFKA_USER_CODE_FOR_REGISTRATION=code_for_registration
KAFKA_MESSAGE_FOR_ALL_USERS=message_for_all_users
```
### Message Service (.env)
```env
EMAIL_KEY=your_email_key
TO_EMAIL=your_email_for_sending_emails

KAFKA_USER_CODE_FOR_REGISTRATION=code_for_registration
KAFKA_BOOTSTRAP_SERVERS=kafka:29092
KAFKA_GROUP_ID=message_service
KAFKA_BILL_EMAIL_TOPIC=bill_sent
KAFKA_MESSAGE_FOR_ALL_USERS=message_for_all_users
```
### Balance Service (.env)
```env
DATABASE_URL=postgresql+asyncpg://amin:my_super_password@balance_db:5432/balances

SECRET_KEY=your_secret_key
JWT_ALGHORITM=HS256

JSON_FILE=exchange_rate.json
JSON_FILE2=commision_for_transfers.json

KAFKA_BOOTSTRAP_SERVERS=kafka:29092
KAFKA_USER_CREATED_TOPIC=user_created
KAFKA_BILL_EMAIL_TOPIC=bill_sent
KAFKA_GROUP_ID=balance_service
```

### Installation & Run

1. Clone the repository:
```bash
git clone <your_repo_url>
cd BANK_FASTAPI
```
2. Create .env files in each service directory using the configs above.

3. Start the project with Docker Compose:
```bash
docker-compose up --build
```

### After Launch

Auth Service → http://localhost:8001 (via /auth)

Message Service → http://localhost:8002 (via /message)

Balance Service → http://localhost:8003 (via /balance)

Nginx reverse proxy → http://localhost:8000

API path format:

```
http://localhost:8000/{service}/{endpoint}
```

### 🔐 Auth Service API

Base path: /auth

Endpoints:


POST /register

POST /register/verify

POST /auth

POST /refresh

Admin-only endpoints:


POST /send_all_users_message

PATCH /update_user_status

GET /get_all_users

DELETE /delete_user

### 💳 Balance Service API

Base path: /balance

Endpoints:


POST /change_money

POST /transfer_money

POST /deposit

GET /watch_balance

Admin-only endpoints:

GET /get_all_users

PATCH /update_commission_for_transfers

PATCH /update_exchange_rate

📚 Interactive Documentation


Auth Service: http://localhost:8000/auth/docs

Message Service: http://localhost:8000/message/docs

Balance Service: http://localhost:8000/balance/docs

⚠️ Important Features


Kafka – inter-service communication (Auth ↔ Balance ↔ Message)

Databases – PostgreSQL (separate DB for each service)

Tokens – JWT with separate access & refresh tokens

Email Verification – confirmation codes sent on registration

🏗️ Architecture


Microservices – each service runs independently

Message Broker – Apache Kafka for async communication

Reverse Proxy – Nginx for routing requests

Databases – separate PostgreSQL instance per service

Containerization – Docker & Docker Compose

