# Image Loading Cache Fix

## Issue Identified
Hero images disappear when scrolling between websites in the website builder carousel.

## Root Cause Analysis
1. **Database Mismatch**: Database contains URLs to images that no longer exist in filesystem
2. **Frontend Caching**: Browser caches failed image loads and doesn't retry
3. **Error Handling**: Images get hidden on error but don't recover when scrolling back

## Backend Evidence
```
ERROR: Image not found at: a75c35d9-7964-469d-8d65-22eedbaccfa8_hero.webp
ERROR: Image not found at: c622004c-cf5d-4e90-a232-903744b209fc_hero.webp

Files actually in directory:
- 6a64360f-9e87-471c-aed7-4674b98ce259_hero.webp ✅ (exists)
- 2691ce8c-6019-42a4-a4cb-c049dcd526fe_hero.webp ✅ (exists)
```

## Solution Strategy
1. **Fix Frontend Caching**: Add cache-busting and retry logic
2. **Improve Error Handling**: Better fallback and recovery
3. **Database Cleanup**: Sync database URLs with actual files

## Frontend Fix Applied
Updated WebsiteBuilder.js image loading with:
- Cache-busting parameters
- Retry logic on error
- Better error state management
- Fallback image handling