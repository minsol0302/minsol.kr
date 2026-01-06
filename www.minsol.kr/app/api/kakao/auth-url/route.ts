import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    try {
        // 백엔드 서버로 요청 프록시
        // 환경 변수에서 API URL 가져오기 (프로토콜이 없으면 추가)
        let apiUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'https://api.minsol.kr';

        // 프로토콜이 없으면 https:// 추가
        if (!apiUrl.startsWith('http://') && !apiUrl.startsWith('https://')) {
            apiUrl = `https://${apiUrl}`;
        }

        const backendUrl = `${apiUrl}/api/auth/kakao/auth-url`;

        console.log('[Kakao Auth-URL] 백엔드 요청 URL:', backendUrl);

        // 요청 body를 읽어서 백엔드로 전달 (빈 body 허용)
        let body = {};
        try {
            const requestBody = await request.json();
            body = requestBody || {};
        } catch (e) {
            body = {};
        }

        console.log('[Kakao Auth-URL] 백엔드로 요청 전송 시작');

        // 타임아웃 설정 (30초)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);

        try {
            const response = await fetch(backendUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                },
                body: JSON.stringify(body),
                signal: controller.signal,
            });

            clearTimeout(timeoutId);

            console.log('[Kakao Auth-URL] 백엔드 응답 상태:', response.status);

            if (!response.ok) {
                const errorText = await response.text().catch(() => '');
                console.error('[Kakao Auth-URL] 백엔드 오류:', response.status, errorText);
                return NextResponse.json(
                    {
                        success: false,
                        error: `Backend error: ${response.status}`,
                        message: errorText || `백엔드 서버 오류 (${response.status})`
                    },
                    { status: response.status }
                );
            }

            const data = await response.json();
            console.log('[Kakao Auth-URL] 백엔드 응답 성공');
            return NextResponse.json(data);
        } catch (fetchError) {
            clearTimeout(timeoutId);

            if (fetchError instanceof Error && fetchError.name === 'AbortError') {
                return NextResponse.json(
                    {
                        success: false,
                        error: '요청 타임아웃',
                        message: '백엔드 서버 응답 시간이 초과되었습니다.'
                    },
                    { status: 504 }
                );
            }
            throw fetchError;
        }
    } catch (error) {
        console.error('[Kakao Auth-URL] 오류 발생:', error);
        const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류';

        return NextResponse.json(
            {
                success: false,
                error: '백엔드 서버에 연결할 수 없습니다.',
                message: errorMessage
            },
            { status: 500 }
        );
    }
}

