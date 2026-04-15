# 📜 GENERAL WORKING CONVENTIONS (CONVENTIONS)

This file is the **Single Source of Truth** for AI when performing this project. The AI must always re-read this file when starting a new session.

---

## 📌 1. FIXED WORKING CONVENTIONS (MANDATORY)
*   **Read and Remember:** AI must always read this file at the start of a new session to grasp history and not repeat old mistakes.
*   **Mandatory Update (Crucial):** AI must automatically update this file (`HUONGDAN/CONVENTIONS.md`) immediately when any new conventions, design changes, or system logic arise. This is the "External Brain" of the project.
*   **Automatic Implementation:** Skip the Implementation Plan creation step and asking for permission. Execute immediately when assigned a task.
*   **Language:** Concise, direct communication in English.
*   **Storage:** Do not create junk files in the root directory. Use `scratch/` for draft files.
*   **Git:** Only perform `pull` and `push` on the `master` branch of the [InternshipFinder](https://github.com/sealdog17/SS2_InternshipFinder) repository.

---

## 🎨 2. DESIGN STANDARDS & TEMPLATES
Always ensure **Pixel-Perfect** synchronization between: Browser, Fullscreen Preview, and PDF File.

### A. BLUE Template (Contemporary)
*   **Layout:** 2 columns (Left sidebar ~36% width).
*   **Color:** Sidebar `#1964d3`, Font Times New Roman.
*   **PDF:** Draw full-bleed sidebar (Zero margins) from `y=0` to `y=842`. Headers have professional dividers.

### B. WHITE Template (Modern Centered)
*   **Layout:** Fully centered.
*   **Typography:**
    *   Name: Uppercase, 22pt, letter-spacing 4px.
    *   Contact: Horizontal format, separated by (•), 8.5pt.
*   **Divider:** 1.5pt black line below contact information.
*   **Spacing:** Plenty of padding/margin to create airy spacing (Airy spacing).

---

## 🛠 3. IMPORTANT TECHNICAL SOLUTIONS (FIXES LOG)

### 🖥 Interface
*   **Fullscreen Scroll:** Use `flex-direction: column` and `align-items: center` to avoid scrolling lock issues when using `justify-content: center`.
*   **Times New Roman:** This font must be registered in ReportLab from `/static/fonts/` to support sharp character rendering.

### 📄 Exporting Files (PDF & PNG)
*   **Sidebar Bleed:** Set doc margins to 0, use `canvas.rect` for the sidebar.
*   **Spacing:** Name `spaceAfter=18`, Contact `spaceAfter=30` to avoid text overlapping.
*   **Headers:** Use `HRFlowable` to create smooth section dividers.
*   **Export PNG:** Use `html2canvas` library with `scale: 2` to allow users to download high-quality CV images.

### ⚙️ System Logic
*   **Time Tracking:** Update `created_at` in the `save_cv` route according to local time.
*   **Template Mapping:** Old-New (`minimalist` -> `white`, `contemporary` -> `blue`).

---
*Last updated: April 15, 2026*
