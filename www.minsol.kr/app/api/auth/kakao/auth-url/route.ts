import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'api.minsol.kr';

    const backendUrl = `https://${apiUrl}/api/auth/kakao/auth-url`;

    console.log('[Kakao Auth-URL] 시작 - 백엔드 URL:', backendUrl);

    try {
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
            body = {};
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);

        try {
            let response: Response | null = null;
            const maxRetries = 2;
            
            for (let attempt = 0; attempt <= maxRetries; attempt++) {
                try {
                    if (attempt > 0) {
                        console.log(`[Kakao Auth-URL] 재시도 ${attempt}/${maxRetries}...`);
                        await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
                    }

                    response = await fetch(backendUrl, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json',
                            'User-Agent': 'Minsol-Frontend/1.0',
                        },
                        body: JSON.stringify(body),
                        signal: controller.signal,
                    });

                    if (response.ok || (response.status !== 502 && response.status !== 503)) {
                        break;
                    }

                    if (attempt < maxRetries) {
                        console.warn(`[Kakao Auth-URL] 백엔드 오류 (${response.status}), 재시도 예정...`);
                        continue;
                    }
                } catch (fetchError) {
                    const lastError = fetchError instanceof Error ? fetchError : new Error(String(fetchError));
                    
                    if (attempt < maxRetries) {
                        console.warn(`[Kakao Auth-URL] 네트워크 오류, 재시도 예정...`, lastError.message);
                        continue;
                    }
                    
                    throw fetchError;
                }
            }

            clearTimeout(timeoutId);

            if (!response) {
                throw new Error('백엔드 서버에 연결할 수 없습니다.');
            }

            if (!response.ok) {
                let errorText = '';
                try {
                    const contentType = response.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        const errorData = await response.json();
                        errorText = errorData.message || errorData.error || JSON.stringify(errorData);
                    } else {
                        errorText = await response.text().catch(() => '');
                        if (errorText.includes('<html>') || errorText.includes('502')) {
                            errorText = '백엔드 서버에 연결할 수 없습니다.';
                        }
                    }
                } catch (e) {
                    errorText = `백엔드 서버 오류 (${response.status})`;
                }

                const statusCode = response.status === 502 ? 503 : response.status;
                
                return NextResponse.json(
                    {
                        success: false,
                        error: statusCode === 502 ? 'Bad Gateway' : `Backend error: ${response.status}`,
                        message: errorText || `백엔드 서버 오류 (${response.status})`,
                    },
                    { status: statusCode }
                );
            }

            const data = await response.json();
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
        console.error('[Kakao Auth-URL] 예외 발생:', error);
        const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류';

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

