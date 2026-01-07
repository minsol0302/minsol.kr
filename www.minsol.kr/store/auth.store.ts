import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// ============================================================================
// Types
// ============================================================================

export interface User {
    id: string;
    email?: string;
    nickname?: string;
    profileImage?: string;
    provider: 'google' | 'kakao' | 'naver';
}

interface AuthState {
    // State
    accessToken: string | null;
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;
}

interface AuthActions {
    // Actions
    setAccessToken: (token: string) => void;
    setUser: (user: User) => void;
    login: (accessToken: string, user: User) => void;
    logout: () => void;
    clearError: () => void;
    setError: (error: string) => void;
    setLoading: (isLoading: boolean) => void;

    // Async Actions
    refreshAccessToken: () => Promise<boolean>;
    validateToken: () => Promise<boolean>;
}

type AuthStore = AuthState & AuthActions;

// ============================================================================
// Initial State
// ============================================================================

const initialState: AuthState = {
    accessToken: null,
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
};

// ============================================================================
// Store
// ============================================================================

export const useAuthStore = create<AuthStore>()(
    devtools(
        persist(
            (set, get) => ({
                // Initial State
                ...initialState,

                // ========================================================================
                // Sync Actions
                // ========================================================================

                /**
                 * Access Token 설정
                 */
                setAccessToken: (token: string) => {
                    set(
                        {
                            accessToken: token,
                            isAuthenticated: !!token,
                            error: null,
                        },
                        false,
                        'auth/setAccessToken'
                    );
                },

                /**
                 * 사용자 정보 설정
                 */
                setUser: (user: User) => {
                    set(
                        {
                            user,
                            error: null,
                        },
                        false,
                        'auth/setUser'
                    );
                },

                /**
                 * 로그인 (Access Token과 사용자 정보 동시 설정)
                 */
                login: (accessToken: string, user: User) => {
                    set(
                        {
                            accessToken,
                            user,
                            isAuthenticated: true,
                            isLoading: false,
                            error: null,
                        },
                        false,
                        'auth/login'
                    );
                },

                /**
                 * 로그아웃
                 * - Access Token 제거
                 * - 사용자 정보 제거
                 * - Refresh Token은 서버에서 HttpOnly 쿠키로 관리되므로 별도 처리 불필요
                 */
                logout: () => {
                    // 서버에 로그아웃 요청 (HttpOnly 쿠키 제거)
                    fetch('/api/auth/logout', {
                        method: 'POST',
                        credentials: 'include', // 쿠키 포함
                    }).catch((error) => {
                        console.error('[Auth Store] 로그아웃 요청 실패:', error);
                    });

                    set(
                        {
                            ...initialState,
                        },
                        false,
                        'auth/logout'
                    );
                },

                /**
                 * 에러 제거
                 */
                clearError: () => {
                    set(
                        {
                            error: null,
                        },
                        false,
                        'auth/clearError'
                    );
                },

                /**
                 * 에러 설정
                 */
                setError: (error: string) => {
                    set(
                        {
                            error,
                            isLoading: false,
                        },
                        false,
                        'auth/setError'
                    );
                },

                /**
                 * 로딩 상태 설정
                 */
                setLoading: (isLoading: boolean) => {
                    set(
                        {
                            isLoading,
                        },
                        false,
                        'auth/setLoading'
                    );
                },

                // ========================================================================
                // Async Actions
                // ========================================================================

                /**
                 * Access Token 갱신
                 * - Refresh Token은 HttpOnly 쿠키에 저장되어 있으므로 자동으로 전송됨
                 * - 서버에서 새로운 Access Token을 반환
                 */
                refreshAccessToken: async (): Promise<boolean> => {
                    try {
                        set({ isLoading: true, error: null }, false, 'auth/refreshAccessToken/pending');

                        const response = await fetch('/api/auth/refresh', {
                            method: 'POST',
                            credentials: 'include', // HttpOnly 쿠키 포함
                        });

                        if (!response.ok) {
                            throw new Error('토큰 갱신 실패');
                        }

                        const data = await response.json();

                        if (data.accessToken) {
                            set(
                                {
                                    accessToken: data.accessToken,
                                    isAuthenticated: true,
                                    isLoading: false,
                                    error: null,
                                },
                                false,
                                'auth/refreshAccessToken/fulfilled'
                            );
                            return true;
                        }

                        throw new Error('Access Token이 응답에 없습니다');
                    } catch (error) {
                        const errorMessage = error instanceof Error ? error.message : '토큰 갱신 실패';
                        set(
                            {
                                accessToken: null,
                                isAuthenticated: false,
                                isLoading: false,
                                error: errorMessage,
                            },
                            false,
                            'auth/refreshAccessToken/rejected'
                        );
                        return false;
                    }
                },

                /**
                 * Access Token 유효성 검증
                 * - 만료되었거나 유효하지 않으면 자동으로 갱신 시도
                 */
                validateToken: async (): Promise<boolean> => {
                    const { accessToken, refreshAccessToken } = get();

                    if (!accessToken) {
                        // Access Token이 없으면 갱신 시도
                        return await refreshAccessToken();
                    }

                    try {
                        set({ isLoading: true }, false, 'auth/validateToken/pending');

                        const response = await fetch('/api/auth/validate', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                Authorization: `Bearer ${accessToken}`,
                            },
                            credentials: 'include',
                        });

                        if (response.ok) {
                            set({ isLoading: false }, false, 'auth/validateToken/fulfilled');
                            return true;
                        }

                        // Access Token이 만료되었으면 갱신 시도
                        if (response.status === 401) {
                            return await refreshAccessToken();
                        }

                        throw new Error('토큰 검증 실패');
                    } catch (error) {
                        const errorMessage = error instanceof Error ? error.message : '토큰 검증 실패';
                        set(
                            {
                                isLoading: false,
                                error: errorMessage,
                            },
                            false,
                            'auth/validateToken/rejected'
                        );

                        // 검증 실패 시 갱신 시도
                        return await refreshAccessToken();
                    }
                },
            }),
            {
                name: 'auth-storage', // localStorage key
                partialize: (state) => ({
                    // accessToken과 user만 localStorage에 저장
                    // refreshToken은 HttpOnly 쿠키에 저장되므로 제외
                    accessToken: state.accessToken,
                    user: state.user,
                    isAuthenticated: state.isAuthenticated,
                }),
            }
        ),
        {
            name: 'AuthStore', // Redux DevTools에서 표시될 이름
            enabled: process.env.NODE_ENV === 'development',
        }
    )
);

// ============================================================================
// Selectors (Optional - 성능 최적화용)
// ============================================================================

export const selectIsAuthenticated = (state: AuthStore) => state.isAuthenticated;
export const selectUser = (state: AuthStore) => state.user;
export const selectAccessToken = (state: AuthStore) => state.accessToken;
export const selectIsLoading = (state: AuthStore) => state.isLoading;
export const selectError = (state: AuthStore) => state.error;

