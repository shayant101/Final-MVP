'use client';

import React from 'react';
import WebsiteBuilder from '../../components/WebsiteBuilder/WebsiteBuilder';
import { useRouter } from 'next/navigation';

export default function WebsiteBuilderPage() {
  const router = useRouter();

  const handleBackToDashboard = () => {
    router.push('/dashboard');
  };

  return (
    <div className="website-builder-page">
      <WebsiteBuilder onBackToDashboard={handleBackToDashboard} />
    </div>
  );
}