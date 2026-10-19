# Essay screen design

## 0. Research log
Reference: minimalist-skill and Notion, for warm document surfaces and quiet controls. Korean system fonts replace Latin display typography. External concept generation and optional development tooling are outside this assigned implementation; no visual/performance score is claimed.

## 1. Identity
A quiet writing desk with a warm paper canvas, white panels and numbered sections. The result is a draft to review against personal experience.

## 2. Color
Tokens: canvas #f6f5f1, surface #ffffff, ink #262b27, muted #62685f, line #dcded5, subtle #efefe9, accent #254f3c, accent-hover #193c2c, success #295b40, success-wash #eaf2eb, warning #80551e, warning-wash #fbf2df, error #9c3830, error-wash #f9eeeb. Automatic dark variants live with the CSS tokens. Status uses washes, never colored edge stripes.

## 3. Type
System-ui, Apple SD Gothic Neo, Malgun Gothic, sans-serif. Display 32–48px; section 22px; lead 18px; body/input 16px; helper 14px; overline 12px. Body line-height 1.65; draft line-height 1.9.

## 4. Layout
4px base; spacing 4/8/12/16/24/32/48/64px. Max width 1200px. Desktop 44% input and remaining result column with 24px gap. Below 960px a single column; below 480px short fields stack. Document owns scroll. All text surfaces wrap long words.

## 5. Components
Field: visible label, required semantics, helper and linked error; focus first invalid field. Button: minimum 48px height, filled primary or bordered secondary, hover/active/focus/disabled states. Panel: neutral border, 12px corners, 24px padding. Feedback: inline polite progress/needs-input and alert errors. Result: immutable request snapshot, editable draft, live count and copy feedback. Empty state explains the next step.

## 6. Interaction
Button press transform 120ms; pending spinner 1s, removed for reduced motion. Form locks for entire request. Client deadline 75 seconds allows two server calls plus overhead; never retry. Editing makes no model request. Out-of-range text can still be copied.

## 7. Surface
Borders-only, no shadows. Radius 6px controls and 12px panels. No decorative imagery, gradients or unsupported brand claims.

## 8. Accessibility and verification
WCAG AA target: keyboard reading order, linked labels/errors, visible focus, 16px inputs, live asynchronous feedback. C and leader verify phone/desktop light/dark, overflow, pending/error/needs-input, snapshot integrity and clipboard. Browser/performance verification is pending, not claimed complete.
