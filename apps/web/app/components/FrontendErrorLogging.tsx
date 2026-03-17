'use client';

import { useEffect } from 'react';

import { frontendLog } from '@/lib/observability';

export default function FrontendErrorLogging() {
  useEffect(() => {
    const onError = (event: ErrorEvent) => {
      frontendLog('frontend.runtime_error', {
        message: event.message,
        source: event.filename,
        line: event.lineno,
        column: event.colno,
      });
    };

    const onUnhandledRejection = (event: PromiseRejectionEvent) => {
      frontendLog('frontend.unhandled_rejection', {
        reason: String(event.reason),
      });
    };

    window.addEventListener('error', onError);
    window.addEventListener('unhandledrejection', onUnhandledRejection);

    return () => {
      window.removeEventListener('error', onError);
      window.removeEventListener('unhandledrejection', onUnhandledRejection);
    };
  }, []);

  return null;
}
