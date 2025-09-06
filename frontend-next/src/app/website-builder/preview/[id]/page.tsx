'use client';

import React from 'react';
import WebsitePreview from '../../../../components/WebsiteBuilder/WebsitePreview';
import { useParams } from 'next/navigation';

export default function WebsitePreviewPage() {
  const params = useParams();
  const id = params.id as string;

  return (
    <div className="website-preview-page">
      <WebsitePreview id={id} />
    </div>
  );
}