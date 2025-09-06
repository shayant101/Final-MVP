# Next.js Migration Issues & Solutions

## Overview
This document tracks issues encountered during the React to Next.js migration and their solutions for future reference.

---

## Phase 2: Component & Styling Migration

### ✅ RESOLVED ISSUES

#### 1. **Server-Side Rendering (SSR) localStorage Issues**
**Problem:** `localStorage is not defined` errors during server-side rendering
**Files Affected:** 
- [`frontend-next/src/contexts/AuthContext.tsx`](frontend-next/src/contexts/AuthContext.tsx:49)
- [`frontend-next/src/contexts/ThemeContext.tsx`](frontend-next/src/contexts/ThemeContext.tsx:31)

**Solution:**
```typescript
// ❌ WRONG - Direct localStorage access in useState
const [token, setToken] = useState(localStorage.getItem('token'));

// ✅ CORRECT - Check for client-side before accessing localStorage
const [token, setToken] = useState<string | null>(null);

useEffect(() => {
  if (typeof window !== 'undefined') {
    const savedToken = localStorage.getItem('token');
    setToken(savedToken);
  }
}, []);
```

#### 2. **Missing 'use client' Directives**
**Problem:** React hooks and context providers not working in Next.js App Router
**Files Affected:** All context providers and components using hooks

**Solution:**
```typescript
// Add 'use client' directive at the top of files using React hooks
'use client';

import React, { useState, useEffect } from 'react';
```

#### 3. **React Router to Next.js Navigation**
**Problem:** `useNavigate` from React Router doesn't exist in Next.js
**Files Affected:** 
- [`frontend-next/src/components/LandingPage.tsx`](frontend-next/src/components/LandingPage.tsx:7)

**Solution:**
```typescript
// ❌ WRONG - React Router
import { useNavigate } from 'react-router-dom';
const navigate = useNavigate();
navigate('/login');

// ✅ CORRECT - Next.js
import { useRouter } from 'next/navigation';
const router = useRouter();
router.push('/login');
```

#### 4. **TypeScript Interface Definitions**
**Problem:** Missing TypeScript interfaces for contexts and components
**Files Affected:** Context files and component props

**Solution:**
```typescript
// Define proper interfaces for contexts
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<any>;
  // ... other methods
}

// Define interfaces for component props
interface ComponentProps {
  children: ReactNode;
  // ... other props
}
```

#### 5. **CSS Custom Properties (CSS Variables) Missing**
**Problem:** Layout issues due to undefined CSS variables like `--spacing-xl`, `--radius-lg`
**Files Affected:** [`frontend-next/src/app/globals.css`](frontend-next/src/app/globals.css:44)

**Solution:**
Added missing CSS variables to globals.css:
```css
/* Spacing Variables */
--spacing-xs: 0.25rem;    /* 4px */
--spacing-sm: 0.5rem;     /* 8px */
--spacing-md: 1rem;       /* 16px */
--spacing-lg: 1.5rem;     /* 24px */
--spacing-xl: 2rem;       /* 32px */
--spacing-2xl: 3rem;      /* 48px */
--spacing-3xl: 4rem;      /* 64px */

/* Border Radius Variables */
--radius-sm: 0.375rem;
--radius-md: 0.5rem;
--radius-lg: 0.75rem;
--radius-xl: 1.5rem;
--radius-2xl: 1.5rem;

/* Font Variables */
--font-mono: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
```

#### 6. **TypeScript Error Handling**
**Problem:** `error` parameter in catch blocks typed as `unknown`
**Files Affected:** [`frontend-next/src/components/Login.tsx`](frontend-next/src/components/Login.tsx:44)

**Solution:**
```typescript
// ❌ WRONG
} catch (error) {
  setError(error.message); // TypeScript error: 'error' is unknown
}

// ✅ CORRECT
} catch (error) {
  setError(error instanceof Error ? error.message : 'An error occurred');
}
```

#### 7. **CSS Custom Properties in React Styles**
**Problem:** TypeScript errors when using CSS custom properties in inline styles
**Files Affected:** [`frontend-next/src/app/page.tsx`](frontend-next/src/app/page.tsx:252)

**Solution:**
```typescript
// ❌ WRONG
style={{'--progress': '89%'}}

// ✅ CORRECT
style={{'--progress': '89%'} as React.CSSProperties}
```

---

## 🔄 ONGOING ISSUES TO MONITOR

### 1. **Component Import Dependencies**
- Some components may still reference other components that need migration
- Watch for missing component imports during development

### 2. **CSS File Organization**
- Currently have both `landing.css` and `LandingPage.css` - may need consolidation
- Monitor for duplicate or conflicting styles

### 3. **Route Structure**
- Need to create proper Next.js routes for `/login`, `/dashboard`, etc.
- Currently getting 404s for these routes (expected)

---

## 📋 MIGRATION CHECKLIST TEMPLATE

For each new component migration:

- [ ] Add `'use client'` directive if using React hooks
- [ ] Update React Router imports to Next.js navigation
- [ ] Add proper TypeScript interfaces for props
- [ ] Fix localStorage/sessionStorage SSR issues
- [ ] Update import paths to match Next.js structure
- [ ] Test component rendering without errors
- [ ] Verify styling works with CSS variables
- [ ] Check for proper error handling in async functions

---

## 🛠️ TOOLS & COMMANDS

### Check for TypeScript Errors
```bash
cd frontend-next && npm run build
```

### Development Server
```bash
cd frontend-next && npm run dev
```

### Clear Next.js Cache
```bash
cd frontend-next && rm -rf .next && npm run dev
```

---

## 📚 REFERENCE LINKS

- [Next.js App Router Migration Guide](https://nextjs.org/docs/app/building-your-application/upgrading/app-router-migration)
- [Next.js Client Components](https://nextjs.org/docs/app/building-your-application/rendering/client-components)
- [Next.js Navigation](https://nextjs.org/docs/app/building-your-application/routing/linking-and-navigating)

---

## 📝 NOTES

- **Phase 2 Status:** ✅ COMPLETED - All major styling and component issues resolved
- **Next Phase:** Phase 3 will focus on logic, state management, and API integration
- **Key Success:** Landing page now renders correctly with proper styling and interactive components

---

*Last Updated: Phase 2 Completion - September 6, 2025*