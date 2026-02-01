# Clinical Trial Data Analysis - User Flow & Technical Architecture

## 📋 User Flow Diagrams

### Primary User Journey: Natural Language Query to Dashboard

```mermaid
graph TD
    A[User enters Explore page] --> B[User types natural language query]
    B --> C[Query sent to /api/explore endpoint]
    C --> D[Pipeline processes query]
    D --> E{Intent Classification}
    E -->|Data Query| F[SQL Generation via LangChain]
    E -->|Conversational| G[Direct AI Response]
    F --> H[SQL Execution on CSV data]
    H --> I[Result Normalization]
    I --> J[Chart Type Inference]
    J --> K[Dashboard Planning with GPT-4o]
    K --> L[Widget Generation]
    L --> M[Render Multi-Widget Dashboard]
    G --> N[Render Narrative Response]
    M --> O[User interacts with charts]
    N --> O
    O --> P[User refines query or starts new conversation]
```

### Dashboard Generation Flow

```mermaid
graph TD
    A[Query Results Available] --> B[Chart Spec Generation]
    B --> C[GPT-4o Dashboard Planning]
    C --> D{Planning Successful?}
    D -->|Yes| E[Generate 8-10 Widget Specs]
    D -->|No| F[Agentic Fallback Query]
    F --> G[Retry with Simplified Query]
    G --> C
    E --> H[Layout in Bento Grid]
    H --> I[Color Coding by Risk Level]
    I --> J[Render Interactive Charts]
    J --> K[Add Tooltips & Legends]
```

### Data Processing Pipeline

```mermaid
graph TD
    A[User Query] --> B[Intent Parser]
    B --> C{Semantic Analysis}
    C --> D[Extract Entities: Study, Subject, Risk Level]
    C --> E[Extract Metrics: DQI, Signal Count]
    C --> F[Extract Filters: Date ranges, Thresholds]
    D --> G[SQL Builder]
    E --> G
    F --> G
    G --> H[Template Selection]
    H --> I[Parameter Binding]
    I --> J[SQL Validation]
    J --> K[AlaSQL Execution]
    K --> L[Result Formatting]
    L --> M[Chart Inference Engine]
    M --> N{Data Type Detection}
    N --> O[Time Series → Line Chart]
    N --> P[Categorical → Bar/Pie Chart]
    N --> Q[Single Metric → KPI Card]
    O --> R[Spec Generation]
    P --> R
    Q --> R
```

## 🏗️ Technical Architecture

### System Components Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Next.js App Router]
        B[React Components]
        C[Tailwind CSS]
        D[Recharts]
    end

    subgraph "Analytics Engine"
        E[Pipeline Orchestrator]
        F[Intent Parser]
        G[SQL Builder]
        H[Query Executor]
        I[Result Normalizer]
        J[Chart Inference]
        K[Dashboard Builder]
    end

    subgraph "AI/ML Layer"
        L[LangChain SQL Chain]
        M[OpenAI GPT-4o]
        N[Prompt Engineering]
        O[Response Parsing]
    end

    subgraph "Data Layer"
        P[AlaSQL Engine]
        Q[CSV Data Files]
        R[Schema Definitions]
        S[Result Cache]
    end

    A --> E
    E --> F
    E --> G
    E --> H
    E --> I
    E --> J
    E --> K
    F --> L
    G --> L
    K --> M
    L --> M
    H --> P
    P --> Q
    E --> R
    B --> D
    C --> B
```

### Component Interaction Flow

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant API as API Route
    participant P as Pipeline
    participant IP as Intent Parser
    participant SB as SQL Builder
    participant QE as Query Executor
    participant DB as Dashboard Builder
    participant AI as GPT-4o

    U->>FE: Submit query
    FE->>API: POST /api/explore
    API->>P: processQuery()
    P->>IP: classifyIntent()
    IP->>AI: Analyze query intent
    AI-->>IP: Intent classification
    IP-->>P: Return intent type

    alt Data Query
        P->>SB: buildSQL()
        SB->>QE: execute()
        QE-->>SB: Query results
        SB-->>P: Normalized results
        P->>DB: generateDashboard()
        DB->>AI: Plan dashboard layout
        AI-->>DB: Widget specifications
        DB-->>P: Dashboard spec
    else Conversational Query
        P->>AI: Generate response
        AI-->>P: Narrative response
    end

    P-->>API: Analytics result
    API-->>FE: Response data
    FE-->>U: Render dashboard/narrative
```

### Data Schema Architecture

```mermaid
erDiagram
    SUBJECTS_RANKED ||--o{ SIGNALS : has
    SUBJECTS_RANKED {
        string subject_id PK
        string study_id
        number dqi
        string risk_level
        number signal_count
        string assigned_cra
        string primary_domain
    }
    SIGNALS {
        string subject_id FK
        string study_id
        string signal_type
        string severity
        date created_at
        string description
    }
    SUBJECTS ||--o{ SUBJECTS_RANKED : aggregates
    SUBJECTS {
        string subject_id PK
        string study_id
        json demographics
        json medical_history
        json adverse_events
        date enrollment_date
    }
    KPIS {
        string study_id PK
        number total_subjects
        number critical_risk_count
        number avg_dqi
        date calculated_at
    }
```

## 🔄 Detailed Component Flows

### Intent Parsing Flow

```mermaid
flowchart TD
    A[Raw User Query] --> B[Preprocess: Clean & Normalize]
    B --> C[Token Analysis]
    C --> D{Contains Data Keywords?}
    D -->|Yes| E[Extract Entities]
    D -->|No| F[Conversational Response]
    E --> G[Validate Against Schema]
    G --> H[Generate Semantic Query]
    H --> I[Return Data Query Intent]
    F --> J[Return Conversational Intent]
```

### SQL Generation Flow

```mermaid
flowchart TD
    A[Semantic Query] --> B[Template Selection]
    B --> C[Parameter Extraction]
    C --> D[Type Coercion]
    D --> E[Filter Building]
    E --> F[Join Construction]
    F --> G[SQL Assembly]
    G --> H[Syntax Validation]
    H --> I[Return Generated SQL]
```

### Chart Inference Flow

```mermaid
flowchart TD
    A[Query Results] --> B[Column Type Analysis]
    B --> C[Data Distribution Check]
    C --> D{Metric Type?}
    D -->|Single KPI| E[KPI Chart Spec]
    D -->|Multiple Metrics| F{Time Series?}
    F -->|Yes| G[Line Chart Spec]
    F -->|No| H{Categorical Data?}
    H -->|Yes| I[Bar/Pie Chart Spec]
    H -->|No| J[Table Fallback]
    E --> K[Spec Validation]
    G --> K
    I --> K
    J --> K
    K --> L[Return Chart Spec]
```

## 📊 Dashboard Layout Algorithm

```mermaid
flowchart TD
    A[Query Results] --> B[Identify Key Metrics]
    B --> C[Calculate Widget Count: 8-10]
    C --> D[Prioritize by Importance]
    D --> E[Assign Chart Types]
    E --> F[Bento Grid Layout]
    F --> G[Responsive Breakpoints]
    G --> H[Color Scheme Application]
    H --> I[Tooltip Configuration]
    I --> J[Legend Setup]
    J --> K[Final Layout Spec]
```

## 🚨 Error Handling & Fallbacks

```mermaid
flowchart TD
    A[Process Request] --> B{Error Occurs?}
    B -->|No| C[Return Success]
    B -->|Yes| D{Error Type?}
    D -->|SQL Syntax| E[Simplify Query]
    D -->|No Data| F[Agentic Fallback]
    D -->|AI Timeout| G[Cached Response]
    D -->|Schema Mismatch| H[Schema Repair]
    E --> I[Retry Processing]
    F --> I
    G --> I
    H --> I
    I --> J{Retry Successful?}
    J -->|Yes| C
    J -->|No| K[Graceful Degradation]
    K --> L[Return Error Message]
```

## 🔧 Configuration & Customization

### Chart Type Selection Matrix

| Data Type | Metric Count | Time Dimension | Preferred Chart |
|-----------|-------------|----------------|-----------------|
| Numeric | 1 | No | KPI Card |
| Numeric | 1 | Yes | Line Chart |
| Numeric | 2-5 | No | Bar Chart |
| Numeric | 2-5 | Yes | Multi-Line Chart |
| Categorical | Any | No | Pie Chart |
| Mixed | Any | Any | Table View |

### Risk Level Color Mapping

```json
{
  "Critical": "#ef4444",
  "High": "#f97316",
  "Medium": "#eab308",
  "Low": "#22c55e"
}
```

### Responsive Breakpoint System

```css
/* Mobile First */
.grid-cols-1 /* 1 column on mobile */
@media (min-width: 768px) { .md:grid-cols-2 } /* 2 columns on tablet */
@media (min-width: 1024px) { .lg:grid-cols-3 } /* 3 columns on desktop */
@media (min-width: 1280px) { .xl:grid-cols-4 } /* 4 columns on large desktop */
```

## 📈 Performance Optimization Flows

### Query Caching Strategy

```mermaid
flowchart TD
    A[Incoming Query] --> B[Generate Cache Key]
    B --> C{Cache Hit?}
    C -->|Yes| D[Return Cached Result]
    C -->|No| E[Process Query]
    E --> F[Store in Cache]
    F --> D
    D --> G[Update Access Time]
```

### Lazy Loading Implementation

```mermaid
flowchart TD
    A[Dashboard Load] --> B[Load Critical Widgets]
    B --> C[Render Initial Layout]
    C --> D[User Scrolls/Views]
    D --> E{Widget in Viewport?}
    E -->|Yes| F[Load Widget Data]
    E -->|No| G[Defer Loading]
    F --> H[Render Widget]
    G --> I[Monitor Scroll Position]
    I --> E
```

## 🔐 Security Architecture

### Input Validation Flow

```mermaid
flowchart TD
    A[User Input] --> B[Sanitize Input]
    B --> C[Length Validation]
    C --> D[Content Filtering]
    D --> E[Schema Validation]
    E --> F{Valid?}
    F -->|Yes| G[Process Query]
    F -->|No| H[Return Validation Error]
    G --> I[Safe Execution]
```

### API Security Measures

```mermaid
flowchart TD
    A[API Request] --> B[Rate Limiting]
    B --> C[Authentication Check]
    C --> D[Input Validation]
    D --> E[Query Sanitization]
    E --> F[Execution Monitoring]
    F --> G[Response Filtering]
    G --> H[Return Safe Response]
```

---

*This documentation provides comprehensive technical architecture and user flow diagrams for the Clinical Trial Data Analysis web application.*