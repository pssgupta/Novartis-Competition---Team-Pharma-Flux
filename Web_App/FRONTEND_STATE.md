# Frontend State Documentation
**Date:** 29 January 2026
**Project:** Clinical Ops Control Center (Web App)
**Framework:** Next.js 14+ (App Router), TypeScript, Tailwind CSS
**UI Library:** shadcn/ui

## 1. Page Structure

### A. Control Center (Home)
**Route:** `/` (and `/dashboard`)
**File:** `src/app/page.tsx`
**Purpose:** Primary operational dashboard for Clinical Research Associates (CRAs) and Study Managers.

**Key Sections:**
1.  **KPI Cards (`SectionCards`)**:
    *   **Subjects Under Monitoring**: Total subject count (1,248).
    *   **Critical Subjects**: Red alert metric for subjects with DQI < 85%.
    *   **Subjects with Open Issues**: Count of subjects with at least one active risk signal.
    *   **Data Readiness Risk**: Percentage of subjects in High/Critical risk categories.

2.  **Operational Risk Trend (`ChartAreaInteractive`)**:
    *   **Visualization**: Interactive stacked area chart.
    *   **Metric**: Timeline of "Critical" vs "High" risk accumulation over 2026.
    *   **Interactivity**: Filter by time range (30d, 90d, etc.).

3.  **Subject Risk Table (`DataTable`)**:
    *   **Columns**: Subject ID, Primary Risk Domain, Risk Level (Badge), DQI Score, Signal Count, Assigned CRA.
    *   **Features**:
        *   Sortable/Filterable (though logic is minimal right now).
        *   **Action Drawer**: Clicking a row (or "details") opens a right-side drawer.

4.  **Subject Detail Drawer**:
    *   **Location**: Embedded within `DataTable` interactions.
    *   **Content**:
        *   Summary metrics (Specific DQI vs Signal Count).
        *   **Review Findings**: List of specific issues with "Trace IDs" (e.g., "Inconsistent visit dates").
        *   **Form**: Assignment of CRA and Investigation Notes.

### B. Data Library
**Route:** `/data-library`
**File:** `src/app/data-library/page.tsx`
**Purpose:** Evidence transparency for Reviewers, Auditors, and Data Architects. Proves the system is grounded in real data ingestion.

**Tabs:**
1.  **Raw Data (Phase 1)**:
    *   Lists ingested source files (e.g., `lab_results.csv`, `visit_log.csv`) with timestamps.
    *   Represents the output of the "Standardization" phase.
2.  **Canonical Data (Phase 2)**:
    *   Shows the schema and descriptions of standardized Parquet files (`subject.parquet`, `measurement.parquet`).
    *   Represents the "Ingestion" phase.
3.  **Risk Signals (Phase 3)**:
    *   Registry of detected signals (e.g., `SIG-8821`).
    *   Displays Subject, Domain, Severity, and traceable IDs.
4.  **DQI & Aggregates (Phase 4)**:
    *   High-level aggregation metrics (Average Protocol DQI, Domain Coverage).

## 2. Navigation Structure
**Component:** `src/components/app-sidebar.tsx` & `src/components/nav-main.tsx`

*   **Control Center**: Links to `/`.
*   **Subjects**: Alias for Control Center (focus on the table).
*   **Data Library**: Links to `/data-library`.
*   **Governance**: Placeholder.
*   **Settings**: Placeholder.

## 3. Key Components & Architecture

*   **`src/components/section-cards.tsx`**:
    *   Hardcoded semantic mapping of clinical KPIs.
    *   Uses `lucide-react` / `@tabler/icons-react` for iconography.
*   **`src/components/chart-area-interactive.tsx`**:
    *   Uses `recharts` for charting.
    *   Mock data generation tuned for 2026 timeline.
*   **`src/components/data-table.tsx`**:
    *   Uses `@tanstack/react-table` for table logic.
    *   Uses `vaul` / shadcn `Drawer` for the side panel details.
    *   Integrated with `zod` schema for type safety (though currently loosely defined).

## 4. Current Data Source
*   **Mock Data**: Most data is currently static or imported from `src/app/dashboard/data.json`.
*   **Integration Status**: The frontend is *not yet* connected to the backend/parquet files in `Data_Analysis`. It serves as a fully functional UI shell ready for API integration.

## 5. Next Steps for Development
1.  **API Routes**: Create Next.js API routes to read the JSON/Parquet outputs from `Data_Analysis/*`.
2.  **Hook Integration**: Replace static JSON imports with `swr` or `react-query` hooks fetching from those API routes.
3.  **Dynamic Filtering**: Enable real filtering on the DataTable based on the API response.
