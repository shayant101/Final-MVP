'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import GetNewCustomers from '../../components/GetNewCustomers';

export default function GetNewCustomersPage() {
  const router = useRouter();

  const handleBackToDashboard = () => {
    router.push('/dashboard');
  };

  return <GetNewCustomers onBackToDashboard={handleBackToDashboard} />;
}