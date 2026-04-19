# Nova Design System - Detailed Specifications

## 1. Foundations

### 1.1 Color Palette
The Nova palette is designed for high-contrast, "glass box" transparency, and focus.

| Color Name | Hex Code | Usage |
| :--- | :--- | :--- |
| **Quantum Blue (Deep)** | `#0A2540` | Backgrounds, sidebar, primary containers. |
| **Quantum Blue (Light)** | `#1A3B5D` | Secondary containers, borders, hover states. |
| **Electric Cyan** | `#06B6D4` | Primary actions, active agent indicators, intelligence highlights. |
| **Stellar White** | `#F8FAFC` | Main text, primary headings. |
| **Nebula Gray** | `#94A3B8` | Muted text, captions, inactive states. |
| **Logic Green** | `#10B981` | Success states, verified outputs, completed tasks. |
| **Alert Amber** | `#F59E0B` | Human-in-the-loop (HITL) gates, warnings, pending approvals. |
| **Signal Red** | `#EF4444` | Errors, failed tool calls, security alerts. |
| **Thought Purple** | `#8B5CF6` | Thinking phase, reasoning process, internal agent communication. |

### 1.2 Typography
- **Primary Font:** `Inter` (Sans-serif) - used for all UI elements, headings, and body text. Highly readable at small sizes.
- **Monospace Font:** `JetBrains Mono` - used for tool outputs, code blocks, and raw data streams, conveying precision.

| Usage | Size | Weight | Line Height |
| :--- | :--- | :--- | :--- |
| H1 (Dashboard Title) | 32px | 700 (Bold) | 1.2 |
| H2 (Section Title) | 24px | 600 (Semi-Bold) | 1.3 |
| H3 (Subsection Title) | 18px | 600 (Semi-Bold) | 1.4 |
| Body (Primary) | 16px | 400 (Regular) | 1.5 |
| Body (Small) | 14px | 400 (Regular) | 1.5 |
| Code/Data | 14px | 500 (Medium) | 1.4 |

### 1.3 Grid & Spacing
- **Base Unit:** 4px.
- **Standard Spacing:** 8px, 16px, 24px, 32px.
- **Layout:** 12-column grid for dashboard views. All containers adhere to this strict structure for scalability and modularity.

---

## 2. Core Components

### 2.1 Agent Avatars
- **Circle shape** with a thin border corresponding to their current status color (Cyan for Acting, Purple for Thinking).
- **Icon-based** (e.g., a shield for Security Agent, a pen for Writer Agent) representing their persona and role.
- **Sub-label:** Name and "Active Role" displayed clearly below or beside the avatar in active lists.

### 2.2 Status Badges
- **Thinking:** Pulsing Thought Purple background with white text, drawing the eye but not demanding immediate action.
- **Acting:** Electric Cyan border with a small "gear" icon spinning, indicating live workflow execution.
- **Awaiting User:** Solid Alert Amber background with black text, demanding intervention.
- **Idle:** Nebula Gray border, receding into the background hierarchy.

### 2.3 Activity Streams
- Log-style entries but categorized by agent. These replace conventional console logs with parsed, conversational summaries.
- High-level intent shown in primary text; raw logs available in "View Details" (Monospace font block).

---

## 3. Advanced Components

### 3.1 Reasoning Maps (The "Glass Box" View)
- **Visual Style:** Directed Acyclic Graph (DAG) with nodes connected by thin, animated paths.
- **Node Anatomy:**
    - **Header:** Goal title.
    - **Status Icon:** (Pending, Active, Completed, Blocked).
    - **Owner:** Small agent avatar in the corner.
- **Interaction:**
    - **Hover:** Show a 1-sentence summary of the reasoning behind this step.
    - **Click:** Open a side panel with the "Internal Monologue" (Chain-of-thought) and citations.

### 3.2 HITL Control Gates (Approval Modals)
- **Design:** Centered modal with an `Alert Amber` top border indicating an interruption in automated workflow.
- **Content:**
    - **Warning Icon:** High visibility.
    - **Impact Statement:** Bold text explaining the consequences (e.g., "This will charge $50 to the API key").
    - **Action Buttons:** 
        - `Approve`: Solid Logic Green.
        - `Deny`: Outline Signal Red.
        - `Modify`: Outline Electric Cyan (allows user to edit the proposed tool call params).

### 3.3 Proactive Collaboration Cues (Insight Cards)
- **Design:** Floating cards in a "Collaboration" side-rail.
- **Visuals:** Thin Electric Cyan border with a subtle gradient background.
- **Language:** Conversational but professional (e.g., "Observation: I found a more efficient way to structure the database. Should I propose a schema update?").

---

## 4. MVP Dashboard Wireframe

### 4.1 Layout Overview
- **Left Sidebar:** Agent Swarm status, project navigation, and settings.
- **Top Bar:** Current high-level Goal, global status (Idle, Active, Blocked), and Credits/Token usage.
- **Main Area (Reasoning Map):** Large canvas for visualizing the multi-agent workflow graph.
- **Right Panel:** Contextual details (Log streams, HITL requests, and Proactive Cues).

### 4.2 ASCII Wireframe

```text
________________________________________________________________________________
| [NAV]    | GOAL: Build and Deploy Custom Model v1.0         | [STATUS: ACTIVE] |
|----------|--------------------------------------------------|------------------|
|          |                                                  |                  |
| [AGENTS] |              [REASONING MAP CANVAS]              | [COLLABORATION]  |
|          |                                                  |                  |
| ( ) CTO  |        (Analyze Requirements)---->(Design)       | [!] HITL GATE    |
| ( ) UX   |                    |                             | Approve API Call?|
| (*) ENG  |                    v                             | [Approve] [Deny] |
|          |             (Implement Logic)                    |                  |
| [FILES]  |                    |                             | [?] INSIGHT      |
| > src/   |                    v                             | Found refactor   |
| > docs/  |               [TESTING...]                       | opportunity in   |
|          |                                                  | engine.ts        |
|----------|--------------------------------------------------|------------------|
| [LOGS]   | ENG: Running vitest --run ...                    | [v] CHAT INPUT   |
|          | UX: Reviewing layout for accessibility ...       |                  |
--------------------------------------------------------------------------------
```

## 5. Related Documentation
- [Design System Brief](./design_system.md)
- [Component Specifications](./COMPONENT_SPECS.md)
- [UX Strategy for Agentic Workflows](./UX_STRATEGY_AGENTIC_WORKFLOWS.md)
- [Brand Guidelines](./brand_guidelines.md)
