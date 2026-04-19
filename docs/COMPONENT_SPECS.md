# Component Specifications: EN-JP Tutor

## 1. Pedagogical Stream Bubble
- **Visuals:** Standard chat bubble with a "Reasoning" toggle icon (a small purple brain/logic icon).
- **Behavior:**
    - On click, expands vertically to show the step-by-step logic used to generate the response.
    - Uses Thought Purple `#8B5CF6` for the background of the expanded section.
    - Each reasoning step is displayed with a small checkmark once "processed".

## 2. Interactive Grammar Highlighting
- **Visuals:** Underlined text within the Japanese translation (e.g., underlining the particle `が`).
- **Behavior:**
    - Hovering over highlighted text displays a tooltip with the word/particle's function.
    - Clicking the text opens the "Reference Panel" (Left Sidebar) with a deep-dive into that specific grammar point.

## 3. Real-time Feedback Toast
- **Visuals:** Small, non-intrusive floating toasts near the input area.
- **Colors:** Logic Green `#10B981` for correct grammar, Alert Amber `#F59E0B` for suggestions, Signal Red `#EF4444` for critical errors.
- **Behavior:** Appears as the user types (if real-time mode is on) or after the user submits a sentence.

## 4. "Glass Box" Reasoning Sidebar
- **Visuals:** A vertical stream of "Thought Nodes" connected by thin lines.
- **Colors:** Nebula Gray `#94A3B8` for background, Electric Cyan `#06B6D4` for the active node.
- **Behavior:** Streams the model's "Internal Monologue" in real-time. This is the visual representation of the agent's reasoning process.

## Related Documentation
- [Learning Dashboard Wireframe](./LEARNING_DASHBOARD_WIREFRAME.md)
- [UX Strategy for Agentic Workflows](./UX_STRATEGY_AGENTIC_WORKFLOWS.md)
- [Nova Design System Specifications](./NOVA_DESIGN_SYSTEM_SPECS.md)
