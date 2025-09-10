'use client';

import React from 'react';
import { useRouter } from 'next/navigation';

export default function TemplatesPage() {
  const router = useRouter();

  // Redirect to dashboard which will show templates view
  React.useEffect(() => {
    router.push('/dashboard?view=templates');
  }, [router]);

  return (
    <div className="redirecting">
      <p>Redirecting to Template Gallery...</p>
    </div>
  );
}