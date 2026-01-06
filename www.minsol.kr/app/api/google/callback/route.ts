import { NextRequest, NextResponse } from 'next/server';
import { handleLoginSuccess } from '@/services/mainservice';

// POST 핸들러 추가 (클라이언트에서 호출)
export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const code = body.code;
        const error = body.error;

        console.log('[Google Callback POST] 수신:', { code: code?.substring(0, 20) + '...', error });

        if (error) {
            console.error('[Google Callback POST] 인증 에러:', error);
            return NextResponse.json({
                success: false,
                error: error,
                redirectUrl: '/'
            }, { status: 400 });
        }

        if (!code) {
            console.error('[Google Callback POST] 인증 코드가 없습니다.');
            return NextResponse.json({
                success: false,
                error: '인증 코드가 없습니다.',
                redirectUrl: '/'
            }, { status: 400 });
        }

        // 백엔드 콜백 엔드포인트로 프록시
        let apiUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'https://api.minsol.kr';
        if (apiUrl && !apiUrl.startsWith('http://') && !apiUrl.startsWith('https://')) {
            apiUrl = `https://${apiUrl}`;
        }
        const backendUrl = `${apiUrl}/api/auth/google/callback`;

        console.log('[Google Callback POST] 백엔드로 요청 전송:', backendUrl);

        const response = await fetch(backendUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code }),
        });

        console.log('[Google Callback POST] 백엔드 응답 상태:', response.status);

        if (!response.ok) {
            const errorText = await response.text().catch(() => '');
            console.error('[Google Callback POST] 백엔드 오류:', response.status, errorText);
            
            try {
                const errorData = JSON.parse(errorText);
                return NextResponse.json({
                    success: false,
                    error: errorData.error || '백엔드 오류',
                    message: errorData.message,
                    redirectUrl: errorData.redirectUrl || '/'
                }, { status: response.status });
            } catch {
                return NextResponse.json({
                    success: false,
                    error: `백엔드 서버 오류 (${response.status})`,
                    redirectUrl: '/'
                }, { status: response.status });
            }
        }

        const data = await response.json();
        console.log('[Google Callback POST] 백엔드 응답 데이터:', data);

        // Refresh Token을 HttpOnly 쿠키에 저장할 수 있도록 redirectUrl 반환
        const redirectUrl = data.redirectUrl || '/dashboard/google';
        const refreshToken = data.refresh_token || data.refreshToken;

        if (refreshToken) {
            // 쿠키를 설정하기 위해 응답을 생성
            const nextResponse = NextResponse.json({
                success: true,
                message: data.message || '로그인 성공',
                token: data.token,
                redirectUrl: redirectUrl
            });

            return handleLoginSuccess(
                nextResponse,
                refreshToken,
                {
                    maxAge: 30 * 24 * 60 * 60,
                    redirectUrl: redirectUrl
                }
            );
        }

        return NextResponse.json({
            success: true,
            message: data.message || '로그인 성공',
            token: data.token,
            redirectUrl: redirectUrl
        });
    } catch (error) {
        console.error('[Google Callback POST] 예외 발생:', error);
        return NextResponse.json({
            success: false,
            error: error instanceof Error ? error.message : '알 수 없는 오류',
            redirectUrl: '/'
        }, { status: 500 });
    }
}

export async function GET(request: NextRequest) {
    try {
        // URL에서 code 파라미터 추출
        const searchParams = request.nextUrl.searchParams;
        const code = searchParams.get('code');
        const error = searchParams.get('error');

        console.log('구글 콜백 수신:', { code: code?.substring(0, 20) + '...', error });

        // 에러가 있으면 로그인 페이지로 리다이렉트
        if (error) {
            console.error('구글 인증 에러:', error);
            return NextResponse.redirect(new URL('/', request.url));
        }

        // code가 없으면 에러
        if (!code) {
            console.error('구글 인증 코드가 없습니다.');
            return NextResponse.redirect(new URL('/', request.url));
        }

        // 백엔드 콜백 엔드포인트로 프록시
        let apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.minsol.kr';
        // 프로토콜이 없으면 https:// 추가
        if (!apiUrl.startsWith('http://') && !apiUrl.startsWith('https://')) {
            apiUrl = `https://${apiUrl}`;
        }
        const backendUrl = `${apiUrl}/api/auth/google/callback?code=${encodeURIComponent(code)}`;
        console.log('백엔드로 요청 전송:', backendUrl.substring(0, 80) + '...');

        const response = await fetch(backendUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            redirect: 'manual', // 리다이렉트를 자동으로 따라가지 않음
        });

        console.log('백엔드 응답 상태:', response.status);

        // 백엔드가 리다이렉트(3xx)를 반환하는 경우
        if (response.status >= 300 && response.status < 400) {
            const redirectUrl = response.headers.get('Location');
            if (redirectUrl) {
                console.log('백엔드 리다이렉트 URL:', redirectUrl);
                
                // 리다이렉트 URL에서 토큰 파라미터 추출
                const redirectUrlObj = new URL(redirectUrl);
                const token = redirectUrlObj.searchParams.get('token');
                const refreshToken = redirectUrlObj.searchParams.get('refresh_token');
                const errorParam = redirectUrlObj.searchParams.get('error');

                if (errorParam) {
                    console.error('백엔드 에러:', errorParam);
                    return NextResponse.redirect(new URL('/', request.url));
                }

                // 🔒 Refresh Token을 HttpOnly 쿠키에 저장
                const nextResponse = NextResponse.redirect(new URL('/dashboard/google', request.url));
                
                if (refreshToken) {
                    return handleLoginSuccess(
                        nextResponse,
                        refreshToken,
                        {
                            maxAge: 30 * 24 * 60 * 60, // 30일
                            redirectUrl: new URL('/dashboard/google', request.url).toString(),
                        }
                    );
                }

                return nextResponse;
            }
        }

        if (!response.ok) {
            const errorText = await response.text().catch(() => '');
            console.error('백엔드 콜백 오류:', response.status, errorText);

            // 백엔드가 500 에러를 반환하더라도, 쿠키에 세션이 저장되었을 수 있으므로
            // 대시보드로 이동 시도
            return NextResponse.redirect(new URL('/dashboard/google', request.url));
        }

        try {
            const data = await response.json();
            console.log('백엔드 응답 데이터:', data);

            // 🔒 백엔드에서 refresh_token을 JSON으로 반환하는 경우
            const refreshToken = data.refresh_token || data.refreshToken;
            if (refreshToken) {
                const nextResponse = NextResponse.redirect(new URL('/dashboard/google', request.url));
                return handleLoginSuccess(
                    nextResponse,
                    refreshToken,
                    {
                        maxAge: 30 * 24 * 60 * 60, // 30일
                        redirectUrl: new URL('/dashboard/google', request.url).toString(),
                    }
                );
            }

            // 백엔드에서 로그인 성공 메시지가 오면 대시보드로 리다이렉트
            // 다양한 메시지 형식 지원
            const message = data.message || data.msg || data.status;
            if (
                message === "구글 로그인 성공" ||
                message === "로그인 성공" ||
                message === "success" ||
                data.success === true ||
                data.status === "success"
            ) {
                return NextResponse.redirect(new URL('/dashboard/google', request.url));
            }
        } catch (jsonError) {
            console.error('JSON 파싱 오류:', jsonError);
            // JSON 파싱 실패해도 대시보드로 이동
        }

        // 기본적으로 대시보드로 리다이렉트 (백엔드가 성공적으로 응답했으면)
        return NextResponse.redirect(new URL('/dashboard/google', request.url));
    } catch (error) {
        console.error('구글 콜백 API 오류:', error);
        // 에러 발생 시에도 대시보드로 이동 시도
        return NextResponse.redirect(new URL('/dashboard/google', request.url));
    }
}

