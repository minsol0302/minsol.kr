'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function KakaoCallback() {
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
            const response = await fetch(
                `http://localhost:8080/api/auth/kakao/callback?code=${encodeURIComponent(code)}`,
                {
                    method: 'GET',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                }
            );

            if (response.ok) {
                const data = await response.json();
                console.log('카카오 로그인 성공:', data);

                // 성공 메시지 확인 후 대시보드로 이동
                if (
                    data.success === true ||
                    data.message === "카카오 로그인 성공" ||
                    data.message === "로그인 성공"
                ) {
                    router.push('/dashboard/kakao');
                    return;
                }
            }

            // 백엔드 응답이 성공적이면 대시보드로 이동
            router.push('/dashboard/kakao');
        } catch (error) {
            console.error('카카오 콜백 처리 오류:', error);
            // 에러 발생 시에도 대시보드로 이동 시도
            router.push('/dashboard/kakao');
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

