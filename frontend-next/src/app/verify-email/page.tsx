'use client';

import React, { Suspense } from 'react'
import EmailVerificationSuccess from '../../components/EmailVerificationSuccess'

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <EmailVerificationSuccess />
    </Suspense>
  )
}