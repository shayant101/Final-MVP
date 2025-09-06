'use client';

import React from 'react';
import TemplateCustomizer from '../../../../../components/WebsiteBuilder/TemplateCustomizer';
import { useParams } from 'next/navigation';

export default function TemplateCustomizerPage() {
  const params = useParams();
  const templateId = params.templateId as string;

  return (
    <div className="template-customizer-page">
      <TemplateCustomizer templateId={templateId} />
    </div>
  );
}