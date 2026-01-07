import { useAuthStore } from '@/store/auth.store';

/**
 * useAuth Hook
 * - Auth Store의 상태와 액션을 쉽게 사용할 수 있는 커스텀 훅
 */
export const useAuth = () => {
  const {
    // State
    accessToken,
    user,
    isAuthenticated,
    isLoading,
    error,
    
    // Actions
    setAccessToken,
    setUser,
    login,
    logout,
    clearError,
    setError,
    setLoading,
    
    // Async Actions
    refreshAccessToken,
    validateToken,
  } = useAuthStore();

  return {
    // State
    accessToken,
    user,
    isAuthenticated,
    isLoading,
    error,
    
    // Actions
    setAccessToken,
    setUser,
    login,
    logout,
    clearError,
    setError,
    setLoading,
    
    // Async Actions
    refreshAccessToken,
    validateToken,
  };
};

