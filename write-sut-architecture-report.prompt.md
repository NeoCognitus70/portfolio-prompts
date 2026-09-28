# Prompt — Write a pedagogical SUT architecture and testability report

Use this prompt to generate an authoritative, evidence-grounded, pedagogical architecture and testability report for a System Under Test (SUT) across desktop, polyglot microservice, dual-surface, or mobile-web implementations, or invoke it without pasting:
`Read and follow portfolio-prompts/write-sut-architecture-report.prompt.md using SUT_PATH=<relative path to SUT project> [PROJECT=<folder>]`.

This is an analytical and educational document, not a defect review or implementation worklist. It keeps the target project read-only and produces an in-depth architectural evaluation explaining how the application is engineered for deterministic UI or API automation.

---

You are preparing a pedagogical architecture and testability report on the **`{SUT_NAME}`** application.

The invocation must identify the target by specifying `SUT_PATH=<path to SUT project folder>` (e.g. `SUT_PATH=src/TradeBlotter.Sut` or `SUT_PATH=services/`) and optionally `PROJECT=<portfolio project folder>` (default: current project). If the target SUT cannot be resolved, **ask which SUT to analyse and stop**.

## Purpose

Produce an educational, rigorous, and evidence-grounded report that allows a senior automation architect, lead SDET, or technical reviewer to understand:

1. **Why the SUT exists:** The role it plays within the portfolio and the specific testability challenges it was designed to resolve.
2. **Domain Architecture:** The business entities, domain models, lifecycle states, and state transition invariants.
3. **Application & Framework Mechanics:**
   - *Desktop:* MVVM implementation, reactive property notification chains, UI thread marshalling (`DispatcherTimer`), and container virtualization (`VirtualizingStackPanel`).
   - *API / Microservices:* Contract adherence (OpenAPI / AsyncAPI), inter-service decoupling, event bus architectures, in-memory state models, and polyglot parity.
   - *Web / SPA:* Single-page application lifecycle, component hierarchy, isolated mathematical or domain logic cores, and DOM event dispatching.
4. **Automation Surface & Accessibility Engineering:**
   - *Desktop:* Explicit `AutomationProperties.AutomationId` catalogs, dynamic row style setters, and modal window lifecycle/ownership.
   - *API / Microservices:* REST route hierarchies, HTTP verbs, payload contracts, Swagger UI endpoints, and event topic schemas.
   - *Web / SPA:* Semantic elements, stable `data-testid` attributes, ARIA roles, and form input accessibility.
5. **Determinism by Design:** The mechanisms enforcing test repeatability (baseline seed matrices, monotonic sequence generators, locale-invariant parsing, in-memory reset handshakes).
6. **Empirical Performance Telemetry:** Captured system metrics (startup latency, readiness detection speed, working set memory, test step dispatch times, and clean teardown duration).
7. **Screenplay Pattern Integration:** How Screenplay Actors, Tasks, and Questions drive and interrogate the SUT across UI or API layers.
8. **Pedagogical Lessons:** Transferable automation lessons and architectural anti-patterns to avoid.

The report must stand alone. A technical reader must not require prior conversational context or knowledge of the generating agent.

## Operating Boundaries

* Treat `{SUT_PATH}` and `{PROJECT}/` as **strictly read-only**. Do not modify source files, markup, project files, or Git state.
* Base all claims on empirical evidence inspected from real source code, markup, schemas, probe logs, or BDD feature files. Never invent or estimate metrics.
* Remain **AI-agent agnostic**. Do not mention specific LLM model names, proprietary tool contexts, or agent internal prompts.
* Use **en-GB spelling** throughout (e.g. *standardised*, *initialisation*, *behaviour*, *virtualised*, *authorisation*).
* Use GitHub-style markdown file links with the `file:///` scheme and forward slashes for all referenced files and code symbols.
* All architectural diagrams must be rendered using **Mermaid** (`flowchart TD` / `flowchart LR` or `sequenceDiagram`). Follow strict Mermaid conventions:
  * Quote node labels containing special characters like parentheses, brackets, or colons (e.g. `id["Label (Extra Info)"]`).
  * **Never include raw HTML tags** (such as `<br/>`, `<b>`, or `<span>`) in Mermaid node labels. Use `\n` inside double quotes for multi-line labels.

## Inputs

Required:
* `SUT_PATH` — Relative path to the SUT project folder (e.g. `src/TradeBlotter.Sut` or `src/`).

Optional:
* `PROJECT` — Project root folder within the portfolio (default: derived from working directory).
* `PROBE_EVIDENCE` — Path to an empirical probe report or telemetry JSON if available.
* `SPECS_PATH` — Relative path to the companion BDD feature suite.
* `AUDIENCE` — Intended readership. Default: *Test Automation Architects, Lead SDETs, and Portfolio Reviewers*.

---

## Step-by-Step Analysis Workflow

### Step 1 — Project Discovery & Source Inventory
1. Locate and read the project manifest (`.csproj`, `package.json`, `requirements.txt`). Capture target runtime, dependencies, and configuration.
2. Inventory all source components: views, controllers, services, models, schemas, and entrypoints.
3. Check for companion probe harnesses or telemetry documents.

### Step 2 — Domain Modelling & State Machine Extraction
1. Inspect the domain models. Document all properties, data types, and formatting rules.
2. Map discrete lifecycle states (e.g. `PENDING`, `FILLED`, `PARTIAL`, `CANCELLED` or authenticated vs unauthenticated states).
3. Trace the business workflows: how records are created, updated, validated, and transitioned.

### Step 3 — Technical & Runtime Architecture Analysis
1. Inspect data management and state propagation (e.g. reactive MVVM bindings, in-memory repositories, or event-driven state mirrors).
2. Inspect concurrency and background operations (timers, async dispatchers, worker threads, or event brokers). Verify clean teardown.
3. Inspect presentation/rendering controls or service routing mechanisms.

### Step 4 — UI Automation / API Surface Accessibility Audit
1. Audit the exposed automation surface:
   - For UI: extract all `AutomationProperties.AutomationId` or `data-testid` hooks into a complete mapping table.
   - For API: extract all REST routes, HTTP methods, status codes, and emitted domain events into an endpoint catalog.
2. Audit modal windows, popups, or secondary dialogs (verify parent-child ownership and scoped discovery).

### Step 5 — Determinism & Test Isolation Assessment
1. Inspect initial data seeding routines. Confirm whether seed data is static, deterministic, and covers all relevant lifecycle states.
2. Verify sequence number generation (e.g. monotonic order ID generators) or deterministic mock fixtures.
3. Check string, number, and date parsers for culture invariance (`CultureInfo.InvariantCulture`).
4. Check for state cleanup / reset hooks (e.g. `POST /internal/reset` or synchronous in-memory store clearing).

### Step 6 — Empirical Telemetry Synthesis
1. Extract or capture empirical benchmarks from test runs, probe records, or CI logs (startup latency, execution duration, per-step dispatch, memory footprint, teardown time).
2. Format metrics into a comparison table contrasting target specifications against empirical measurements.

### Step 7 — Screenplay Pattern & BDD Alignment
1. Inspect companion BDD features (`*.feature`) and step definitions.
2. Map how persona-based actors interact with the SUT via Tasks and Questions.
3. Synthesise the runtime interaction into a Mermaid sequence diagram.

### Step 8 — Pedagogical Synthesis & Takeaways
1. Formulate 4–6 core engineering lessons highlighting why the SUT's design accelerates automation and what anti-patterns it overcomes.

---

## Required Report Structure

Author the final report following this structure:

```markdown
# Pedagogical Report: `{SUT_NAME}` ({SUT_TYPE} SUT)

**Target Component:** [{SUT_NAME}](file:///{ABSOLUTE_SUT_PATH})  
**Repository:** [{PROJECT_NAME}]({REPO_URL})  
**Portfolio Project:** {PORTFOLIO_ID} ({PROJECT_TITLE})  
**Runtime & Platform:** {RUNTIME_STACK}, {FRAMEWORK}, {OS_PLATFORM}  

---

## 1. Executive Summary & Pedagogical Purpose
[Context on why this SUT was engineered, the structural gaps it addresses, and its primary architectural principles.]

### System Architecture Diagram
[Insert a comprehensive Mermaid flowchart (flowchart TD) illustrating background feeds, main window/service state, visual tree/endpoints, and secondary lifecycles with clear directional arrows.]

---

## 2. Domain Model & Business Workflows
[Breakdown of domain models, attributes, discrete lifecycle states, and state transition rules.]

---

## 3. Technical Architecture & Implementation
### 3.1. Core Mechanics & State Management
[Analysis of state propagation, MVVM/data stores, and reactive updates.]

### 3.2. Asynchronous Operations & Concurrency
[Analysis of timers, dispatchers, event buses, and clean teardown in disposal hooks.]

### 3.3. Rendering / Container / Routing Configuration
[Analysis of virtualization, routing tables, and execution boundaries.]

---

## 4. Automation Surface & Accessibility Engineering
### 4.1. Explicit Automation Catalog (AutomationId / API Endpoints)
[Complete markdown table detailing all interactive controls or API routes.]

### 4.2. Advanced Locators / Dynamic Identification / Contract Bindings
[Code snippet and analysis of dynamic bindings or schema contracts.]

### 4.3. Secondary Windows / Modals / Inter-Service Boundaries
[Analysis of modal dialog ownership, scoping, or service-to-service contracts.]

---

## 5. Determinism & Test Isolation Hooks
### 5.1. Baseline Seed Data Matrix
[Details of pre-seeded records, ID sequencing, and initial state coverage.]

### 5.2. Deterministic Form Validation & Error Paths
[Analysis of validation logic, culture-invariant parsing, and predictable mock responses.]

---

## 6. Empirical Performance & Telemetry Baseline
[Markdown table comparing target thresholds against real captured metrics.]

---

## 7. How the Screenplay Test Suite Drives the SUT
### Runtime Interaction Sequence
[Insert a Mermaid sequence diagram (sequenceDiagram) showing Actors, Tasks, SUT boundaries, and Questions.]

### BDD Feature Alignment
[Gherkin scenario snippet and walk-through of Actor Tasks and Questions.]

---

## 8. Pedagogical Lessons & Takeaways for Automation Engineers
[Numbered list of transferable principles and architectural guidelines.]
```
