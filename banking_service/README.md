# Banking Service API

## Overview

This microservice provides a comprehensive banking system that enables account management and secure fund transfers between accounts. The service ensures data integrity through unique identifiers and validates all transactions to occur only between existing accounts within the system.

## Business Requirements

### Account Management
- Create and manage bank accounts with unique identifiers
- Each account must have:
  - Unique account number
  - Unique email address
  - Unique phone number
  - Account holder information
  - Current balance

### Transaction Management
- Process fund transfers between accounts
- Each transaction must have:
  - Unique transaction ID
  - Source account (sender)
  - Destination account (receiver)
  - Transaction amount
  - Timestamp
  - Transaction status
- Transactions are only permitted between existing accounts in the system
- Ensure atomic operations to maintain data consistency

## Proposed Architecture

### Technology Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Validation**: Pydantic v2
- **Migration**: Alembic
- **API Documentation**: OpenAPI/Swagger (auto-generated)

### Architecture Components

#### 1. API Layer
- **Account Endpoints**
  - `POST /api/v1/accounts` - Create new account
  - `GET /api/v1/accounts/{account_number}` - Retrieve account details
  - `GET /api/v1/accounts` - List all accounts (with pagination)
  - `PUT /api/v1/accounts/{account_number}` - Update account information
  - `DELETE /api/v1/accounts/{account_number}` - Deactivate account

- **Transaction Endpoints**
  - `POST /api/v1/transactions` - Create new transaction
  - `GET /api/v1/transactions/{transaction_id}` - Retrieve transaction details
  - `GET /api/v1/transactions` - List transactions (with filtering and pagination)
  - `GET /api/v1/accounts/{account_number}/transactions` - Get account transaction history

#### 2. Business Logic Layer
- **Account Service**
  - Account creation with unique constraint validation
  - Email and phone number format validation
  - Account number generation (auto-generated or custom format)
  - Balance management

- **Transaction Service**
  - Transaction ID generation (UUID)
  - Account existence validation
  - Sufficient balance verification
  - Atomic debit/credit operations using database transactions
  - Transaction status management (pending, completed, failed)

#### 3. Data Layer
- **Database Schema**
  ```
  accounts
  ├── id (Primary Key)
  ├── account_number (Unique, Indexed)
  ├── email (Unique, Indexed)
  ├── phone_number (Unique, Indexed)
  ├── account_holder_name
  ├── balance (Decimal)
  ├── status (active/inactive)
  ├── created_at
  └── updated_at

  transactions
  ├── id (Primary Key)
  ├── transaction_id (UUID, Unique, Indexed)
  ├── source_account_id (Foreign Key)
  ├── destination_account_id (Foreign Key)
  ├── amount (Decimal)
  ├── status (pending/completed/failed)
  ├── description
  ├── created_at
  └── completed_at
  ```

#### 4. Key Features

**Data Integrity**
- Database-level unique constraints on account_number, email, and phone_number
- Foreign key constraints ensuring referential integrity
- Database transactions for atomic operations

**Transaction Safety**
- Pessimistic locking on account records during transactions
- Balance validation before processing
- Rollback mechanism for failed transactions
- Idempotency support to prevent duplicate transactions

**Validation & Error Handling**
- Pydantic models for request/response validation
- Custom exception handlers for business logic errors
- Comprehensive error messages and HTTP status codes

**Observability**
- Structured logging for all operations
- Transaction audit trail
- Request/response logging middleware

### Design Patterns

1. **Repository Pattern**: Abstract database operations
2. **Service Layer Pattern**: Encapsulate business logic
3. **Unit of Work Pattern**: Manage database transactions
4. **Dependency Injection**: FastAPI's built-in DI for services and database sessions

### Security Considerations

- Input validation and sanitization
- SQL injection prevention through ORM
- Rate limiting on API endpoints
- Authentication/Authorization (to be implemented based on requirements)

### Scalability Considerations

- Stateless API design for horizontal scaling
- Database connection pooling
- Async/await support for I/O operations
- Pagination for list endpoints
- Database indexing on frequently queried fields

## Project Structure

```
banking-service/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── accounts.py
│   │   │   └── transactions.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── account.py
│   │   └── transaction.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── account.py
│   │   └── transaction.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── account_service.py
│   │   └── transaction_service.py
│   └── repositories/
│       ├── __init__.py
│       ├── account_repository.py
│       └── transaction_repository.py
├── tests/
├── alembic/
├── requirements.txt
├── .env.example
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- pip or poetry for dependency management

### Installation
```bash
# Clone the repository
git clone <repository-url>

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start the service
uvicorn app.main:app --reload
```

### API Documentation
Once the service is running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Future Enhancements

- Multi-currency support
- Transaction reversal/refund functionality
- Scheduled/recurring transactions
- Transaction limits and fraud detection
- Account statements and reporting
- Notification service integration (email/SMS)
- Authentication and authorization (JWT/OAuth2)
- Audit logging and compliance features