# Comprehensive Hybrid Next.js Migration Plan

## 1. Guiding Principles

This plan synthesizes two approaches: one focused on a **modern tech stack and advanced features (Plan 1)**, and another on a **methodical, safety-first migration (Plan 2)**.

- **Foundation:** We will build the new application using the modern, future-proof stack defined in Plan 1 (Next.js App Router, TypeScript, Tailwind CSS, shadcn/ui, Zustand).
- **Methodology:** We will execute the migration following the strict, phased, and verifiable process from Plan 2 to ensure stability and minimize risk.
- **Goal:** The outcome will be a modern, performant, and feature-rich application built on a stable foundation, with all existing functionality preserved and enhanced.

## 2. Technical Architecture Decisions

- **Framework:** Next.js 13+ with App Router.
- **Language:** TypeScript.
- **Styling:** Tailwind CSS with shadcn/ui for component primitives.
- **State Management:** Zustand for complex client-side state, React Server Components for server-fetched state.
- **Routing:** Next.js file-based routing (App Router).
- **Data Fetching:** Server Components for initial data, Axios for client-side mutations to the existing FastAPI backend.
- **Publishing System:** Replace the custom SSG with Next.js Incremental Static Regeneration (ISR) and On-Demand Revalidation via webhooks from the FastAPI backend.
- **Deployment:** Vercel for the Next.js frontend, existing infrastructure for the FastAPI backend.

## 3. The Hybrid Migration Plan: A 5-Phase Approach

---

### **Phase 1: Project Setup & Core Structure (Week 1)**

*Goal: Initialize the new Next.js application with the target tech stack and render the basic, static layout of the homepage. The CRA app remains untouched.*

1.  **[ ] Initialize Next.js Project:**
    -   Create a new directory `frontend-next`.
    -   Initialize a Next.js project with TypeScript, ESLint, and Tailwind CSS.
    -   Install `shadcn-ui`.
2.  **[ ] Basic Scaffolding:**
    -   Set up a basic project structure: `app/`, `components/`, `lib/`, `context/`.
    -   Configure absolute imports and path aliases for cleaner code.
3.  **[ ] Static Asset Migration:**
    -   Copy all assets from `client/public/` to `frontend-next/public/`.
4.  **[ ] Global Styles & Layout:**
    -   Move the contents of the main global stylesheet (e.g., `index.css`) into `frontend-next/app/globals.css`.
    -   Create the root layout (`app/layout.tsx`) and import the global stylesheet.
5.  **[ ] Create Home Page Shell:**
    -   Create the home page file (`app/page.tsx`).
    -   Copy the JSX structure from the CRA `App.js` into this file.
    -   **Important:** Comment out all logic, state, event handlers, and data fetching. The goal is a static render only.

**✅ Verification Checkpoint:**
- Run `npm run dev` in `frontend-next`.
- The homepage should render with correct styling but no functionality.

---

### **Phase 2: Component & Styling Migration (Week 2)**

*Goal: Migrate all reusable components and their styles. The application should look identical to the original, but still without full functionality.*

1.  **[ ] Component Migration:**
    -   Copy the entire `client/src/components/` directory into `frontend-next/components/`.
2.  **[ ] TypeScript Conversion:**
    -   Convert all copied component files from `.js`/`.jsx` to `.ts`/`.tsx`.
    -   Add basic types for props (`any` is acceptable for now to unblock progress; a follow-up task will be to add strict types).
3.  **[ ] Styling Integration:**
    -   Update CSS import paths in all components.
    -   Begin replacing standard CSS with Tailwind utility classes where straightforward.
4.  **[ ] Fix Component Imports:**
    -   Update all import paths in `app/page.tsx` and within the migrated components to reflect the new structure.

**✅ Verification Checkpoint:**
- Run the dev server.
- The homepage and its components should now look visually identical to the production CRA version.

---

### **Phase 3: Logic, State & Publishing System Migration (Weeks 3-4)**

*Goal: Breathe life into the application by migrating routing, state management, API calls, and the core publishing logic.*

1.  **[ ] Routing Migration:**
    -   For each route in the CRA app, create a corresponding folder and `page.tsx` file in `frontend-next/app/`.
    -   Replace all `react-router-dom` `<Link>` components with `next/link`.
    -   Replace `useNavigate` hooks with `useRouter` from `next/navigation`.
2.  **[ ] State Management Migration:**
    -   Migrate existing Context providers into `frontend-next/context/`.
    -   Wrap the root layout (`app/layout.tsx`) with these providers.
    -   Introduce Zustand for new, complex client-side state.
3.  **[ ] API Integration:**
    -   Copy the Axios configuration into the new project.
    -   Uncomment the data-fetching logic on all pages and components.
    -   Ensure all API calls correctly target the FastAPI backend.
4.  **[ ] Publishing System (SSG to ISR):**
    -   Identify pages that were previously statically generated.
    -   Implement `generateStaticParams` and use ISR with a revalidation timer (e.g., 300 seconds) for these pages.
    -   Create a Next.js API route (`/api/revalidate`) that can be called by a webhook from FastAPI to trigger on-demand revalidation.

**✅ Verification Checkpoint:**
- The entire application should be functional.
- Test all navigation, login/logout flows, and data-dependent pages.
- Verify that the publishing webhook correctly triggers a page refresh.

---

### **Phase 4: Advanced Features & New Modules (Weeks 5-6)**

*Goal: With the core application migrated, implement the new, high-value features from Plan 1.*

1.  **[ ] Implement AI Digital Presence Grader:**
    -   Build the UI for the grader report (`/grader/[runId]`).
    -   Integrate with FastAPI endpoints that handle the crawling and scoring logic.
2.  **[ ] Implement Digital Marketing Checklist:**
    -   Build the UI for viewing and managing checklist templates and tasks.
    -   Connect to FastAPI for task storage and auto-generation from grader results.
3.  **[ ] Implement Advanced Auth & Tenancy:**
    -   Integrate NextAuth or enhance the JWT solution.
    -   Implement the middleware for mapping hostnames to tenant slugs.
4.  **[ ] Implement Billing:**
    -   Integrate Stripe Checkout for subscription management.
    -   Implement feature gating based on subscription level (Starter vs. Pro).

**✅ Verification Checkpoint:**
- All new feature modules are functional and integrated with the backend.
- Multi-tenancy and billing logic are working correctly.

---

### **Phase 5: Finalization, Testing & Deployment (Week 7)**

*Goal: Polish the application, perform comprehensive testing, and deploy to production.*

1.  **[ ] Optimization and Refinement:**
    -   Replace all `<img>` tags with `<Image>` from `next/image`.
    -   Refactor components to leverage Server Components where possible.
    -   Ensure Lighthouse scores are ≥ 95.
2.  **[ ] Environment Variables:**
    -   Copy `.env` to `.env.local` and prefix all browser-exposed variables with `NEXT_PUBLIC_`.
3.  **[ ] Comprehensive Testing:**
    -   Conduct end-to-end testing, comparing the functionality of the new Next.js app against the old CRA app.
    -   Perform accessibility (a11y) and SEO audits.
4.  **[ ] Deployment:**
    -   Deploy the `frontend-next` application to Vercel.
    -   Update DNS records to point to the new application.
5.  **[ ] Cleanup:**
    -   Once the new site is stable in production, delete the old `client/` directory.
    -   Remove CRA-specific dependencies (e.g., `react-scripts`) from the root `package.json`.
