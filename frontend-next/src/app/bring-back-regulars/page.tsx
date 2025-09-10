'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import BringBackRegulars from '../../components/BringBackRegulars';

export default function BringBackRegularsPage() {
  const router = useRouter();

  const handleBackToDashboard = () => {
    router.push('/dashboard');
  };

  return <BringBackRegulars onBackToDashboard={handleBackToDashboard} />;
}