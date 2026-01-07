'use client';

import { useEffect, ReactNode } from 'react';
import { useAuthStore } from '@/store/auth.store';

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Auth Provider
 * - 앱 시작 시 토큰 유효성 검증
 * - Access Token 자동 갱신
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const validateToken = useAuthStore((state) => state.validateToken);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  useEffect(() => {
    // 앱 시작 시 토큰 유효성 검증
    if (isAuthenticated) {
      validateToken();
    }
  }, [isAuthenticated, validateToken]);

  // Access Token 자동 갱신 (50분마다 - Access Token은 1시간 유효)
  useEffect(() => {
    if (!isAuthenticated) return;

    const interval = setInterval(
      () => {
        validateToken();
      },
      50 * 60 * 1000
    ); // 50분

    return () => clearInterval(interval);
  }, [isAuthenticated, validateToken]);

  return <>{children}</>;
}

