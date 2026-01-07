'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function KakaoCallbackClient() {
    const router = useRouter();
    const searchParams = useSearchParams();

    useEffect(() => {
        // URL에서 code 파라미터 확인
        const code = searchParams.get('code');
        const error = searchParams.get('error');

        if (error) {
            console.error('카카오 인증 에러:', error);
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
            console.log('[Kakao Callback Client] Next.js API 라우트로 요청 전송, code:', code?.substring(0, 20) + '...');
            // Next.js API 라우트를 통해 요청 (서버 사이드 프록시)
            const response = await fetch(
                '/api/auth/kakao/callback',
                {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ code }),
                }
            );

            console.log('[Kakao Callback Client] API 응답 상태:', response.status, response.statusText);

            // 응답이 성공적이지 않으면 에러 텍스트 확인
            if (!response.ok) {
                let errorText = '';
                try {
                    errorText = await response.text();
                    console.error('[Kakao Callback Client] API 오류 응답:', errorText);
                    const errorData = JSON.parse(errorText);
                    console.error('[Kakao Callback Client] 파싱된 에러 데이터:', errorData);
                    
                    if (errorData.redirectUrl) {
                        router.push(errorData.redirectUrl);
                    } else {
                        router.push('/');
                    }
                    return;
                } catch (parseError) {
                    console.error('[Kakao Callback Client] JSON 파싱 실패:', parseError);
                    console.error('[Kakao Callback Client] 원본 에러 텍스트:', errorText);
                    router.push('/');
                    return;
                }
            }

            // 성공적인 응답 파싱
            let data;
            try {
                data = await response.json();
                console.log('[Kakao Callback Client] API 응답 데이터:', data);
            } catch (jsonError) {
                console.error('[Kakao Callback Client] JSON 파싱 오류:', jsonError);
                router.push('/');
                return;
            }

            if (data.success === true || response.ok) {
                const redirectUrl = data.redirectUrl || '/dashboard/kakao';
                console.log('[Kakao Callback Client] 로그인 성공, 리다이렉트:', redirectUrl);
                router.push(redirectUrl);
                return;
            }

            // 실패한 경우
            console.error('[Kakao Callback Client] 로그인 실패:', data);
            if (data.redirectUrl) {
                router.push(data.redirectUrl);
            } else {
                router.push('/');
            }
        } catch (error) {
            console.error('[Kakao Callback Client] 예외 발생:', error);
            console.error('[Kakao Callback Client] 에러 타입:', error instanceof Error ? error.constructor.name : typeof error);
            console.error('[Kakao Callback Client] 에러 메시지:', error instanceof Error ? error.message : String(error));
            console.error('[Kakao Callback Client] 에러 스택:', error instanceof Error ? error.stack : '스택 없음');
            router.push('/');
        }
    }

    return (
        <div className="flex min-h-screen items-center justify-center bg-white">
            <div className="text-center">
                <p className="text-lg text-gray-600">카카오 로그인 처리 중...</p>
            </div>
        </div>
    );
}

