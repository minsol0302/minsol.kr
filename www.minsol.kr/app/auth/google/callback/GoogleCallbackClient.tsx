'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/store/auth.store';
import { extractUserFromToken } from '@/utils/jwt';

export default function GoogleCallbackClient() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const login = useAuthStore((state) => state.login);

    useEffect(() => {
        // URL에서 code 파라미터 확인
        const code = searchParams.get('code');
        const error = searchParams.get('error');

        if (error) {
            console.error('구글 인증 에러:', error);
            router.push('/');
            return;
        }

        if (code) {
            // 백엔드 콜백 엔드포인트로 요청
            handleCallback(code);
        } else {
            // code가 없으면 메인 페이지로
            router.push('/');
        }
    }, [searchParams, router]);

    async function handleCallback(code: string) {
        try {
            console.log('[Google Callback Client] Next.js API 라우트로 요청 전송, code:', code?.substring(0, 20) + '...');
            // Next.js API 라우트를 통해 요청 (서버 사이드 프록시)
            const response = await fetch(
                '/api/google/callback',
                {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ code }),
                }
            );

            console.log('[Google Callback Client] API 응답 상태:', response.status, response.statusText);

            // 응답이 성공적이지 않으면 에러 텍스트 확인
            if (!response.ok) {
                let errorText = '';
                try {
                    errorText = await response.text();
                    console.error('[Google Callback Client] API 오류 응답:', errorText);
                    const errorData = JSON.parse(errorText);
                    console.error('[Google Callback Client] 파싱된 에러 데이터:', errorData);

                    if (errorData.redirectUrl) {
                        router.push(errorData.redirectUrl);
                    } else {
                        router.push('/');
                    }
                    return;
                } catch (parseError) {
                    console.error('[Google Callback Client] JSON 파싱 실패:', parseError);
                    console.error('[Google Callback Client] 원본 에러 텍스트:', errorText);
                    router.push('/');
                    return;
                }
            }

            // 성공적인 응답 파싱
            let data;
            try {
                data = await response.json();
                console.log('[Google Callback Client] API 응답 데이터:', data);
            } catch (jsonError) {
                console.error('[Google Callback Client] JSON 파싱 오류:', jsonError);
                router.push('/');
                return;
            }

            if (data.success === true || response.ok) {
                // Access Token과 사용자 정보를 스토어에 저장
                const accessToken = data.accessToken || data.token;

                if (accessToken) {
                    // 사용자 정보가 응답에 있으면 사용, 없으면 JWT에서 추출
                    let user = data.user;

                    if (!user && accessToken) {
                        // JWT 토큰에서 사용자 정보 추출
                        user = extractUserFromToken(accessToken);
                    }

                    if (user) {
                        console.log('[Google Callback Client] Access Token과 사용자 정보를 스토어에 저장');
                        login(accessToken, user);
                    } else {
                        // 사용자 정보를 추출할 수 없으면 Access Token만 저장
                        console.log('[Google Callback Client] Access Token만 스토어에 저장 (사용자 정보 없음)');
                        useAuthStore.getState().setAccessToken(accessToken);
                    }
                }

                const redirectUrl = data.redirectUrl || '/dashboard/google';
                console.log('[Google Callback Client] 로그인 성공, 리다이렉트:', redirectUrl);
                router.push(redirectUrl);
                return;
            }

            // 실패한 경우
            console.error('[Google Callback Client] 로그인 실패:', data);
            if (data.redirectUrl) {
                router.push(data.redirectUrl);
            } else {
                router.push('/');
            }
        } catch (error) {
            console.error('[Google Callback Client] 예외 발생:', error);
            console.error('[Google Callback Client] 에러 타입:', error instanceof Error ? error.constructor.name : typeof error);
            console.error('[Google Callback Client] 에러 메시지:', error instanceof Error ? error.message : String(error));
            console.error('[Google Callback Client] 에러 스택:', error instanceof Error ? error.stack : '스택 없음');
            router.push('/');
        }
    }

    return (
        <div className="flex min-h-screen items-center justify-center bg-white">
            <div className="text-center">
                <p className="text-lg text-gray-600">구글 로그인 처리 중...</p>
            </div>
        </div>
    );
}

