import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    try {
        // 백엔드 서버로 요청 프록시
        // 서버 측에서는 NEXT_PUBLIC_ 접두사 없이 환경 변수 사용 가능
        const apiUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'https://api.minsol.kr';
        const backendUrl = `${apiUrl}/api/auth/google/auth-url`;

        console.log('[Google Auth-URL] 백엔드 요청 URL:', backendUrl);
        console.log('[Google Auth-URL] API URL 환경 변수:', {
            API_URL: process.env.API_URL,
            NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL
        });

        // 요청 body를 읽어서 백엔드로 전달 (빈 body 허용)
        let body = {};
        try {
            const requestBody = await request.json();
            body = requestBody || {};
        } catch (e) {
            // body가 없거나 잘못된 경우 빈 객체 사용
            body = {};
        }

        console.log('[Google Auth-URL] 백엔드로 요청 전송 시작');

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

            console.log('[Google Auth-URL] 백엔드 응답 상태:', response.status);

            if (!response.ok) {
                const errorText = await response.text().catch(() => '');
                console.error('[Google Auth-URL] 백엔드 오류:', {
                    status: response.status,
                    statusText: response.statusText,
                    errorText: errorText.substring(0, 200)
                });
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
            console.log('[Google Auth-URL] 백엔드 응답 성공');
            return NextResponse.json(data);
        } catch (fetchError) {
            clearTimeout(timeoutId);
            
            if (fetchError instanceof Error && fetchError.name === 'AbortError') {
                console.error('[Google Auth-URL] 요청 타임아웃');
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
        console.error('[Google Auth-URL] 오류 발생:', error);
        const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류';
        const errorName = error instanceof Error ? error.name : 'Unknown';
        const errorStack = error instanceof Error ? error.stack : undefined;
        console.error('[Google Auth-URL] 오류 상세:', { 
            errorName,
            errorMessage, 
            errorStack: errorStack?.substring(0, 500) 
        });
        
        return NextResponse.json(
            {
                success: false,
                error: '백엔드 서버에 연결할 수 없습니다.',
                message: errorMessage,
                details: errorName === 'TypeError' && errorMessage.includes('fetch') 
                    ? '백엔드 서버 URL을 확인해주세요.' 
                    : undefined
            },
            { status: 500 }
        );
    }
}

