import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    // 환경 변수에서 API URL 가져오기 (프로토콜이 없으면 추가)
    // 커밋을 위한 더미
    let apiUrl = process.env.NEXT_PUBLIC_API_URL;

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
            // 백엔드 연결 시도 (재시도 로직 포함)
            let response: Response | null = null;
            const maxRetries = 2;

            for (let attempt = 0; attempt <= maxRetries; attempt++) {
                try {
                    if (attempt > 0) {
                        console.log(`[Google Auth-URL] 재시도 ${attempt}/${maxRetries}...`);
                        await new Promise(resolve => setTimeout(resolve, 1000 * attempt)); // 지수 백오프
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

                    // 502, 503 오류가 아닌 경우 재시도 중단
                    if (response.ok || (response.status !== 502 && response.status !== 503)) {
                        break;
                    }

                    // 마지막 시도가 아니면 재시도
                    if (attempt < maxRetries) {
                        console.warn(`[Google Auth-URL] 백엔드 오류 (${response.status}), 재시도 예정...`);
                        continue;
                    }
                } catch (fetchError) {
                    const lastError = fetchError instanceof Error ? fetchError : new Error(String(fetchError));

                    // 마지막 시도가 아니면 재시도
                    if (attempt < maxRetries) {
                        console.warn(`[Google Auth-URL] 네트워크 오류, 재시도 예정...`, lastError.message);
                        continue;
                    }

                    throw fetchError;
                }
            }

            clearTimeout(timeoutId);

            // response가 null인 경우 처리
            if (!response) {
                throw new Error('백엔드 서버에 연결할 수 없습니다.');
            }

            console.log('[Google Auth-URL] 백엔드 응답 상태:', response.status);

            if (!response.ok) {
                let errorText = '';
                try {
                    const contentType = response.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        const errorData = await response.json();
                        errorText = errorData.message || errorData.error || JSON.stringify(errorData);
                    } else {
                        // HTML 응답인 경우 (502 Bad Gateway 등)
                        errorText = await response.text().catch(() => '');
                        // HTML 태그 제거
                        if (errorText.includes('<html>') || errorText.includes('502')) {
                            errorText = '백엔드 서버에 연결할 수 없습니다. 서버가 다운되었거나 네트워크 문제가 있을 수 있습니다.';
                        }
                    }
                } catch (e) {
                    errorText = `백엔드 서버 오류 (${response.status})`;
                }

                console.error('[Google Auth-URL] 백엔드 오류:', {
                    status: response.status,
                    statusText: response.statusText,
                    errorText: errorText.substring(0, 200)
                });

                // 502 Bad Gateway는 서버 연결 문제이므로 503으로 변경하여 처리
                const statusCode = response.status === 502 ? 503 : response.status;

                return NextResponse.json(
                    {
                        success: false,
                        error: statusCode === 502 ? 'Bad Gateway' : `Backend error: ${response.status}`,
                        message: errorText || `백엔드 서버 오류 (${response.status})`,
                        status: response.status
                    },
                    { status: statusCode }
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

