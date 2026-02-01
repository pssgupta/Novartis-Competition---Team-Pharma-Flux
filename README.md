# Novartis-Competition---Team-Pharma-Flux
Working solution for Novartis use cases with documented methodology and results.
**Live Demo**

• Landing Page: https://novaratis-landing-page.vercel.app/ 

• Dashboard Application: https://novaratis-app.vercel.app/

This repository contains the final, cleaned, and reproducible prototype developed for Problem Statement 1 of the Novaratis competition.
**The project implements an AI-assisted clinical trial operations control system that transforms fragmented clinical and operational data into actionable, explainable, and auditable insights. The solution focuses on standardized data flows, real-time operational visibility, governed decision-making, and natural language access to data using a GenAI-powered assistant.**
This is a systems and data-driven solution and does not involve training custom machine learning models.


**What This Project Does**

The system ingests **standardized clinical and operational datasets** and presents them through an **integrated control center dashboard.** It highlights emerging risks, prioritizes subjects and sites, supports action readiness, and maintains full governance and audit trails.
On top of the dashboard, a **conversational interface** powered by the OpenAI API enables users to **ask natural language questions** and receive structured, context-aware insights derived strictly from governed data.
The solution is designed with **human-in-the-loop validation** at every critical decision point to ensure explainability, trust, and inspection readiness.


**Core Capabilities**

~ The control center provides a unified operational view with global KPIs, risk trends, and prioritized subjects and sites.

~ Risk signals are surfaced through standardized scoring and rule-based logic rather than opaque black-box models.

~ Action workflows convert insights into draft actions, approvals, and tracked outcomes with full traceability.

~ Governance features ensure identity tracking, timestamps, immutable logs, and audit-ready records across the entire workflow.

~ The “Talk to Data” interface allows users to query data in plain language without writing SQL, while enforcing strict context boundaries to prevent hallucinations.



**Repository Structure**

~ The app directory contains the dashboard, user interface, and chatbot integration logic.

~ The data directory contains standardized sample datasets and documentation describing the data structure and assumptions.

~ The logic directory contains rule-based signal detection, prioritization logic, and data transformation pipelines.

~ The governance directory contains components related to audit trails, action traceability, and inspection readiness.

~ The results directory contains representative outputs such as screenshots, exported tables, and example chatbot responses.

~ The report file documents the system architecture, workflows, evaluation criteria, limitations, and proposed next steps in detail.



**Setup Instructions**

Clone the repository to your local machine.
Create and activate a virtual environment if required.
Install dependencies listed in the requirements file.
Set environment variables using the provided example file before running the application.


**Running the Application**

Start the dashboard application from the app directory using the main entry file.
Once running, the system loads standardized data, renders the control center views, and enables interaction with the GenAI-powered chat interface.
All system behavior is deterministic and driven by governed data and predefined logic.


**Evaluation and Validation**

The solution is evaluated qualitatively and quantitatively based on operational visibility, correctness of prioritization, explainability of insights, governance completeness, and usability.
Evaluation criteria and validation mapping aligned with competition success metrics are documented in the report.


**Limitations and Future Work**

The current prototype operates on predefined datasets and relies on external API access for conversational functionality.
Future extensions include scaling to live data streams, deeper cross-study analytics, enhanced prompt governance, and optional integration with fine-tuned or local language models.


**License**

This project is released under the MIT License for academic review and competition evaluation purposes.
