'use client';

import React from 'react';
import WebsiteEditor from '../../../../components/WebsiteBuilder/WebsiteEditor';
import { useParams } from 'next/navigation';

export default function WebsiteEditorPage() {
  const params = useParams();
  const id = params.id as string;

  return (
    <div className="website-editor-page">
      <WebsiteEditor id={id} />
    </div>
  );
}