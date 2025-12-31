**Ficet (Financial Pocket)**

## Requirements

### Functional requirements

- Track personal expenses and income
- Be able to extract data transactions from bank statements or receipts
- Categorize transactions (food, transport, entertainment, etc.)
- Generate monthly/annual financial reports
- Summarize, analyze, and visualize financial data including health metrics, spending predictions, spending insights, spending trends, and goal tracking
- Allow users to set financial goals and track progress
- Provide alerts for unusual spending or budget overruns
- Support multiple currencies and exchange rate tracking
- Set budget limits for categories
- Offline capability for basic lightweight operations (e.g., adding transactions and viewing reports) excluding data extraction features

### Non-functional requirements

- Low latency for real-time transaction processing
- High availability and fault tolerance
- Data encryption for sensitive financial information
- Regular automated backups for data recovery

## Capacity Planning

### Storage

- User metadata (profiles, preferences, settings) - ~1KB per user x 500k = ~500MB total

- User transaction data (historical records, categorizations, notes) - estimated 500 transactions per month ~1KB per transaction × 500 × 12 months × 500k users = 6,000,000KB = 6GB per year

- User profile pictures and attachments - estimated 100MB per user × 500k users = 50TB total per month

- Daily bandwidth:
  - each receipt/bank statement picture: 3MB; each user submits 10 pictures; 500k users × 10 × 3MB = 15,000,000MB = 15TB per day
  - Total daily bandwidth: ~15TB

## Architecture

### Storage Design

This system will use blob storage to store all user pictures and attachments.
- User pictures and attachments are immutable and stored without versioning
- All files are stored with this path pattern: `users/{userId}/{attachmentType}/{filename}`


### Relational Database
```mermaid
erDiagram
    USER {
        uuid id PK
        string email
        string password_hash
        string name
        string profile_picture_path
        string preferred_currency
        jsonb settings
        timestamp created_at
        timestamp updated_at
    }
    
    TRANSACTION {
        uuid id PK
        uuid user_id FK
        uuid category_id FK
        decimal amount
        string currency
        string type "income/expense"
        string description
        date transaction_date
        string source "manual/receipt/bank_statement"
        string attachment_path
        timestamp created_at
        timestamp updated_at
    }
    
    CATEGORY {
        uuid id PK
        uuid user_id FK
        string name
        string type "income/expense"
        string icon
        boolean is_default
        timestamp created_at
    }
    
    BUDGET {
        uuid id PK
        uuid user_id FK
        uuid category_id FK
        decimal limit_amount
        string currency
        string period "weekly/monthly/annual"
        date start_date
        date end_date
        timestamp created_at
        timestamp updated_at
    }
    
    FINANCIAL_GOAL {
        uuid id PK
        uuid user_id FK
        string name
        decimal target_amount
        decimal current_amount
        string currency
        date target_date
        string status "active/completed/cancelled"
        timestamp created_at
        timestamp updated_at
    }
    
    ALERT {
        uuid id PK
        uuid user_id FK
        string type "budget_exceeded/unusual_spending/goal_milestone/low_balance"
        string message
        boolean is_read
        jsonb metadata
        timestamp created_at
    }
    
    EXCHANGE_RATE {
        uuid id PK
        string from_currency
        string to_currency
        decimal rate
        timestamp fetched_at
    }
    
    ANALYTICS_REPORT {
        uuid id PK
        uuid user_id FK
        string report_type "monthly/annual/weekly/daily"
        date period_start
        date period_end
        jsonb data
        timestamp generated_at
    }

    USER ||--o{ TRANSACTION : "has"
    USER ||--o{ CATEGORY : "creates"
    USER ||--o{ BUDGET : "sets"
    USER ||--o{ FINANCIAL_GOAL : "defines"
    USER ||--o{ ALERT : "receives"
    USER ||--o{ ANALYTICS_REPORT : "generates"
    CATEGORY ||--o{ TRANSACTION : "categorizes"
    CATEGORY ||--o{ BUDGET : "limits"
```

### High level

```mermaid
flowchart LR
    A[Mobile/Web App]
    B[API Gateway]
    C[Load Balancer]
    E[Database]
    F[Storage]

    subgraph Backend[Backend Services]
        D1[Service 1]
        D2[Service 2]
        D3[Service 3]
    end

    A --> B
    B --> C
    C --> Backend
    Backend --> F
    Backend --> E
```

### System Workflow

#### Submit Transaction from Picture

```mermaid
sequenceDiagram
    participant A as User
    participant B as Backend Service
    participant C as Storage
    participant D as Database
    participant E as AI Service

    A ->> B: Upload Image for processing
    B ->> B: validate user
    alt Invalid User
        B ->> A: Return error
    end

    B ->> B: validate image format and size
    alt Invalid Format/Size
        B ->> A: Return error
    end


    par
        B ->> E: Send image to AI for extraction
    and
        B ->> C: Store image
    end

    E ->> B: Return extracted transaction data
    B ->> E: Categorize transaction
    E ->> B: Return categorized transaction data
    B ->> D: Save transaction data to database
    B ->> A: Return success status
```

#### Submit Transaction from Manual Entry

```mermaid
sequenceDiagram
    participant A as User
    participant B as Backend Service
    participant D as Database

    A ->> B: Submit transaction details manually
    B ->> B: validate user and transaction data
    alt Invalid Data
        B ->> A: Return validation error
    end
    B ->> D: Save transaction data to database
    B ->> A: Return success status
```

#### Fetch Transactions

```mermaid
sequenceDiagram
    participant A as User
    participant B as Backend Service
    participant D as Database
    participant E as Storage

    A ->> B: Request transaction history
    B ->> B: validate user
    alt Invalid User
        B ->> A: Return error
    end
    B ->> D: Query transaction data
    loop over transactions
        alt have image
            B ->> E: Request image URLs for transactions
            E ->> B: Return image URLs
            D ->> B: Return transaction records with images
        else
            D ->> B: Return transaction records without images
        end
    end

    B ->> A: Return transaction list
```

#### Summarize, analyze, and visualize periodic transactions
> **_NOTE_**: This workflow processes transactions and categorizes them over time periods e.g weekly, monthly, and annually and only runs on the last period's time.

> **_TODO_**: This workflow can be improved to support real-time updates and more sophisticated analytics.

```mermaid
sequenceDiagram
    participant A as User
    participant B as Backend Service
    participant D as Database
    participant F as Analytics Service

    A ->> B: Request financial summary/analysis
    B ->> B: validate user
    alt Invalid User
        B ->> A: Return error
    end

    B ->> B: Generate time period

    B ->> B: Check if in last period's time
    alt Not in last period
        B ->> A: Return no analysis needed
    end

    B ->> D: Query all transactions on the period

    B ->> F: Send transaction data for analysis
    F ->> B: Return analysis results (spending trends, categories, etc.)
    B ->> D: Save analysis results to database
    B ->> A: Return summarized financial insights
```

#### Fetch Financial Insights
```mermaid
sequenceDiagram
    participant A as User
    participant B as Backend Service
    participant F as Analytics Service

    A ->> B: Request financial insights
    B ->> B: validate user
    alt Invalid User
        B ->> A: Return error
    end

    B ->> F: Request financial insights
    F ->> B: Return financial insights
    B ->> A: Return financial insights
```
