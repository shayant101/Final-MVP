'use client';

import React from 'react';
import { useRouter } from 'next/navigation';

export default function WebsiteBuilderPage() {
  const router = useRouter();

  // Redirect to dashboard which will show website-builder view
  React.useEffect(() => {
    router.push('/dashboard?view=website-builder');
  }, [router]);

  return (
    <div className="redirecting">
      <p>Redirecting to Website Builder...</p>
    </div>
  );
}