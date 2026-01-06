import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    // 환경 변수에서 API URL 가져오기 (프로토콜이 없으면 추가)
    let apiUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'https://api.minsol.kr';

    // 프로토콜이 없으면 https:// 추가
    if (apiUrl && !apiUrl.startsWith('http://') && !apiUrl.startsWith('https://')) {
        apiUrl = `https://${apiUrl}`;
    }

    const backendUrl = `${apiUrl}/api/auth/google/auth-url`;

    console.log('[Google Auth-URL] 시작 - 백엔드 URL:', backendUrl);

    try {
        // 요청 body를 읽어서 백엔드로 전달 (빈 body 허용)
        let body = {};
        try {
            const contentType = request.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const text = await request.text();
                if (text) {
                    body = JSON.parse(text);
                }
            }
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
        console.error('[Google Auth-URL] 예외 발생:', error);
        const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류';
        const errorName = error instanceof Error ? error.name : 'Unknown';

        // 네트워크 에러와 기타 에러 구분
        if (errorName === 'TypeError' && errorMessage.includes('fetch')) {
            console.error('[Google Auth-URL] 네트워크 에러 - 백엔드 서버에 연결할 수 없습니다:', backendUrl);
            return NextResponse.json(
                {
                    success: false,
                    error: '네트워크 에러',
                    message: `백엔드 서버에 연결할 수 없습니다. (${backendUrl})`,
                },
                { status: 503 }
            );
        }

        console.error('[Google Auth-URL] 예상치 못한 에러:', { errorName, errorMessage });
        return NextResponse.json(
            {
                success: false,
                error: '서버 오류',
                message: errorMessage || '알 수 없는 오류가 발생했습니다.'
            },
            { status: 500 }
        );
    }
}

