# SUPAA Design System (Nova)

This document provides a high-level summary of the Nova Design System. For the comprehensive component catalog and visual states, please refer to the [Nova Design System Specifications](./NOVA_DESIGN_SYSTEM_SPECS.md).

## 1. Design Tokens

### 1.1 Colors
- **Primary (Quantum Blue):** `#0A2540`
- **Secondary (Electric Cyan):** `#00E5FF`
- **Background (Deep Slate):** `#0F172A`
- **Surface (Slate 800):** `#1E293B`
- **Border:** `rgba(255, 255, 255, 0.1)`
- **Success:** `#10B981`
- **Warning:** `#F59E0B`
- **Error:** `#EF4444`

### 1.2 Typography
- **Headings:** Satoshi or Inter (Geometric Sans) - Primary font family for strong readability.
- **Body:** Inter - Used for dense technical text and long-form content.
- **Code:** JetBrains Mono or Fira Code - Legible and modern monospace.

### 1.3 Spacing & Grid
- **Scale:** 8px grid (4, 8, 12, 16, 24, 32, 48, 64) for consistent padding and margins.
- **Container Max-Width:** 1280px on desktop resolutions.

## 2. Components

### 2.1 Buttons
- **Primary:** Background `#00E5FF`, Text `#0F172A`, Weight 600, Radius 6px.
- **Secondary:** Border `1px solid #00E5FF`, Text `#00E5FF`. Hover states increase background opacity slightly.
- **Destructive:** Background `#EF4444`, Text `#FFFFFF`, used for irrecoverable actions like deleting agents or environments.

### 2.2 Cards
- **Style:** Background `#1E293B`, Border `1px solid rgba(255,255,255,0.1)`, Radius 12px.
- **Shadow:** `0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)`. Elevated surfaces use deeper shadows to contrast with the `Deep Slate` background.

### 2.3 AI Interaction Elements
- **Thinking State:** Pulsing dot in Electric Cyan, providing non-intrusive feedback that a process is running.
- **Agent Output:** Encased in a slate card with a subtle cyan left-border accent, distinguishing AI-generated text from human input.
- **Reasoning Toggle:** A clickable affordance that expands inline reasoning steps or tool logs natively in the UI.

## 3. Related Documentation
- [Brand Guidelines](./brand_guidelines.md)
- [UX Strategy for Agentic Workflows](./UX_STRATEGY_AGENTIC_WORKFLOWS.md)
