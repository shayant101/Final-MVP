'use client';

import React from 'react';
import TemplateGallery from '../../../components/WebsiteBuilder/TemplateGallery';
import { useRouter } from 'next/navigation';

export default function TemplatesPage() {
  const router = useRouter();

  const handleBackToDashboard = () => {
    router.push('/dashboard');
  };

  return (
    <div className="templates-page">
      <TemplateGallery onBackToDashboard={handleBackToDashboard} />
    </div>
  );
}