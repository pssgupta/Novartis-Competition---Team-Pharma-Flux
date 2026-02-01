# Clinical Trial Data Analysis Web App

A sophisticated Next.js web application for analyzing clinical trial data using natural language queries and AI-generated dashboards. Built with modern React, TypeScript, and integrated with LangChain for SQL generation and OpenAI GPT-4o for intelligent query processing.

## 🏗️ Architecture Overview

### Frontend Stack
- **Framework**: Next.js 16 with App Router
- **UI Library**: React with TypeScript
- **Styling**: Tailwind CSS with custom design system
- **Charts**: Recharts for data visualization
- **Icons**: Lucide React & Tabler Icons
- **Forms**: Custom form components with validation

### Backend & AI Integration
- **Query Processing**: LangChain for SQL chain generation
- **LLM**: OpenAI GPT-4o for natural language understanding
- **Data Engine**: AlaSQL for in-memory SQL execution
- **Data Sources**: CSV files (subjects, signals, KPIs)

### Data Pipeline
```
User Query → Intent Parsing → SQL Generation → Query Execution → Result Normalization → Chart Inference → Dashboard Rendering
```

## 📁 Project Structure

```
web-app/
├── src/
│   ├── analytics/           # Core analytics engine
│   │   ├── chart-spec.ts    # Chart specification generation
│   │   ├── chart-inference.ts # Automatic chart type detection
│   │   ├── dashboard-builder.ts # AI-powered dashboard creation
│   │   ├── langchain-service.ts # LangChain SQL generation
│   │   ├── pipeline.ts      # Main query processing pipeline
│   │   ├── query-executor.ts # SQL execution on CSV data
│   │   ├── schema.ts        # Database schema definitions
│   │   └── types.ts         # TypeScript type definitions
│   ├── app/                 # Next.js app router pages
│   │   ├── api/             # API routes
│   │   ├── dashboard/       # Main dashboard page
│   │   ├── explore/         # Chat interface for queries
│   │   └── governance/      # Governance dashboard
│   ├── components/          # Reusable UI components
│   │   ├── chart-renderer.tsx # Chart visualization component
│   │   ├── data-table.tsx   # Data table with sorting/filtering
│   │   └── ui/              # Shadcn/ui components
│   ├── data/                # Static data files
│   │   ├── subjects.json    # Subject-level clinical data
│   │   ├── kpis.json        # KPI metrics
│   │   └── signals.json     # Risk signals data
│   └── lib/                 # Utility functions
├── public/                  # Static assets
└── package.json             # Dependencies and scripts
```

## 🔄 Data Flow Architecture

### 1. Query Processing Pipeline
```
User Input → Intent Classification → SQL Generation → Execution → Normalization → Visualization
```

**Key Components:**
- **Intent Parser** (`nl-to-intent.ts`): Classifies queries as data queries vs. conversational
- **SQL Builder** (`sql-builder.ts`): Generates SQL from semantic queries
- **Query Executor** (`query-executor.ts`): Executes SQL on CSV data using AlaSQL
- **Result Normalizer** (`result-normalizer.ts`): Formats results for visualization
- **Chart Inference** (`chart-inference.ts`): Automatically determines best chart type

### 2. Dashboard Generation
```
Query Results → Chart Specifications → Layout Planning → Widget Rendering
```

**AI-Powered Features:**
- **Dashboard Builder** (`dashboard-builder.ts`): Uses GPT-4o to plan dashboard layouts
- **Fallback Mechanisms**: Agentic retry logic for missing data
- **Multi-Widget Support**: Generates 8-10 widgets per dashboard

### 3. Data Schema
```typescript
interface AnalyticsSchema {
  subjects_ranked: {
    columns: [
      { name: 'subject_id', type: 'string' },
      { name: 'study_id', type: 'string' },
      { name: 'dqi', type: 'number' },
      { name: 'risk_level', type: 'string' },
      { name: 'signal_count', type: 'number' }
    ]
  },
  signals: { /* signal data */ },
  subjects: { /* full subject data */ }
}
```

## 🚀 Key Features

### Natural Language Query Interface
- **Chat-based UI** with real-time responses
- **Multi-modal responses**: Charts, tables, and narratives
- **Context-aware conversations** with message history
- **Loading states** and error handling

### AI-Generated Dashboards
- **Automatic chart type selection** (bar, line, pie, KPI)
- **Bento grid layouts** with responsive design
- **Color-coded risk levels** (Critical, High, Medium, Low)
- **Interactive tooltips** and legends

### Data Visualization
- **Recharts integration** for professional charts
- **Custom color palettes** for clinical data
- **Responsive design** for all screen sizes
- **Export capabilities** for dashboard data

### Clinical Trial Analytics
- **Risk signal analysis** with DQI (Data Quality Index)
- **Subject-level insights** across multiple studies
- **Study comparison** and trend analysis
- **Governance workflows** for data review

## 🛠️ Development Setup

### Prerequisites
- Node.js 18+
- npm or yarn
- OpenAI API key

### Installation
```bash
cd web-app
npm install
```

### Environment Configuration
Create `.env.local`:
```env
OPENAI_API_KEY=your_openai_api_key
```

### Development
```bash
npm run dev
```

### Build
```bash
npm run build
npm start
```

## 📊 API Endpoints

### Query Processing
- `POST /api/kpis` - KPI data
- `POST /api/subjects` - Subject data
- `POST /api/subjects/[id]` - Individual subject details

### AI Features
- `POST /api/genai/actions` - Generate governance actions
- `POST /api/genai/draft-actions` - Draft email actions
- `POST /api/genai/narrative` - Generate narratives
- `POST /api/genai/pattern-explain` - Explain patterns
- `POST /api/genai/root-cause` - Root cause analysis

## 🔧 Configuration

### Chart Types
- **KPI**: Single metric display with trend indicators
- **Bar Chart**: Categorical comparisons
- **Line Chart**: Time series and trends
- **Pie Chart**: Proportional distributions

### Risk Levels
- **Critical**: Red (#ef4444)
- **High**: Orange (#f97316)
- **Medium**: Yellow (#eab308)
- **Low**: Green (#22c55e)

### Data Quality Index (DQI)
- Range: 0-100
- Thresholds: <70 (Critical), 70-85 (High), 85-95 (Medium), >95 (Low)

## 🎨 UI/UX Design

### Design System
- **Color Palette**: Professional clinical theme
- **Typography**: Clean, readable fonts
- **Spacing**: Consistent 4px grid system
- **Components**: Reusable, accessible UI components

### Responsive Layout
- **Mobile-first** design approach
- **Breakpoint system**: sm, md, lg, xl
- **Flexible grids** for dashboard widgets

## 🔒 Security & Compliance

### Data Handling
- **Client-side processing** only
- **No sensitive data storage**
- **OpenAI API compliance** for healthcare data
- **Input validation** and sanitization

### Error Handling
- **Graceful degradation** for failed queries
- **User-friendly error messages**
- **Fallback mechanisms** for AI failures

## 📈 Performance Optimization

### Build Optimizations
- **Next.js compilation** with TypeScript checking
- **Code splitting** for route-based loading
- **Image optimization** and lazy loading
- **Bundle analysis** for size monitoring

### Runtime Performance
- **Memoization** for expensive computations
- **Virtual scrolling** for large datasets
- **Debounced search** for query optimization
- **Progressive loading** for dashboard widgets

## 🧪 Testing Strategy

### Unit Tests
- Component testing with React Testing Library
- Utility function testing
- API route testing

### Integration Tests
- End-to-end query flows
- Dashboard generation workflows
- Data pipeline validation

## 🚀 Deployment

### Build Process
```bash
npm run build
npm run start
```

### Environment Variables
- Production API keys
- Database connections (if applicable)
- Monitoring and logging configuration

### Monitoring
- Error tracking with Sentry
- Performance monitoring
- User analytics

## 🤝 Contributing

### Code Standards
- TypeScript strict mode
- ESLint configuration
- Prettier formatting
- Conventional commits

### Development Workflow
1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Create pull request

## 📚 Additional Resources

### Data Sources
- Clinical trial subject data (CSV)
- Risk signal definitions
- KPI calculations
- Study metadata

### AI Prompts
- Query intent classification
- SQL generation templates
- Dashboard planning prompts
- Narrative generation

### Configuration Files
- `tsconfig.json` - TypeScript configuration
- `tailwind.config.js` - Styling configuration
- `next.config.ts` - Next.js configuration
- `eslint.config.mjs` - Linting rules

---

Built with ❤️ for clinical data analysis and insights generation.
