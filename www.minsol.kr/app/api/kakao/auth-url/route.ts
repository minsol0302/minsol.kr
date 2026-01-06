import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    try {
        // 백엔드 서버로 요청 프록시
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.minsol.kr';
        const backendUrl = `${apiUrl}/api/auth/kakao/auth-url`;

        console.log('[Kakao Auth-URL] 백엔드 요청 URL:', backendUrl);

        // 요청 body를 읽어서 백엔드로 전달 (빈 body 허용)
        let body = {};
        try {
            const requestBody = await request.json();
            body = requestBody || {};
        } catch (e) {
            // body가 없거나 잘못된 경우 빈 객체 사용
            body = {};
        }

        console.log('[Kakao Auth-URL] 백엔드로 요청 전송 시작');

        const response = await fetch(backendUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

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
    } catch (error) {
        console.error('[Kakao Auth-URL] 오류 발생:', error);
        const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류';
        const errorStack = error instanceof Error ? error.stack : undefined;
        console.error('[Kakao Auth-URL] 오류 상세:', { errorMessage, errorStack });

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

