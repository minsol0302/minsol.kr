import { NextRequest, NextResponse } from 'next/server';
import { handleLoginSuccess } from '@/services/mainservice';

// POST 핸들러 추가 (클라이언트에서 호출)
export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const code = body.code;
        const state = body.state;
        const error = body.error;

        console.log('[Naver Callback POST] 수신:', { code: code?.substring(0, 20) + '...', state, error });

        if (error) {
            console.error('[Naver Callback POST] 인증 에러:', error);
            return NextResponse.json({
                success: false,
                error: error,
                redirectUrl: '/'
            }, { status: 400 });
        }

        if (!code) {
            console.error('[Naver Callback POST] 인증 코드가 없습니다.');
            return NextResponse.json({
                success: false,
                error: '인증 코드가 없습니다.',
                redirectUrl: '/'
            }, { status: 400 });
        }

        // 백엔드 콜백 엔드포인트로 프록시
        const apiUrl = process.env.NEXT_PUBLIC_API_URL;
        const backendUrl = `https://${apiUrl}/api/auth/naver/callback`;

        console.log('[Naver Callback POST] 백엔드로 요청 전송:', backendUrl);

        let response;
        try {
            response = await fetch(backendUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code, state }),
            });
        } catch (fetchError) {
            console.error('[Naver Callback POST] Fetch 에러:', fetchError);
            return NextResponse.json({
                success: false,
                error: '백엔드 서버에 연결할 수 없습니다.',
                message: fetchError instanceof Error ? fetchError.message : '네트워크 오류',
                redirectUrl: '/'
            }, { status: 503 });
        }

        if (!response.ok) {
            const errorText = await response.text().catch(() => '');
            console.error('[Naver Callback POST] 백엔드 오류:', response.status, errorText);
            
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
        console.log('[Naver Callback POST] 백엔드 응답 데이터:', data);

        // 백엔드에서 받은 토큰과 사용자 정보 추출
        const accessToken = data.token || data.accessToken;
        const refreshToken = data.refresh_token || data.refreshToken;
        const redirectUrl = data.redirectUrl || '/dashboard/naver';

        // 사용자 정보 추출 (백엔드 응답에서)
        const user = data.user || {
            id: data.userId || data.id || '',
            email: data.email,
            nickname: data.nickname || data.name,
            profileImage: data.profileImage || data.picture,
            provider: 'naver' as const,
        };

        // 응답 생성
        const nextResponse = NextResponse.json({
            success: true,
            message: data.message || '로그인 성공',
            accessToken: accessToken,
            user: user,
            redirectUrl: redirectUrl
        });

        // Refresh Token을 HttpOnly 쿠키에 저장
        if (refreshToken) {
            return handleLoginSuccess(
                nextResponse,
                refreshToken,
                {
                    maxAge: 30 * 24 * 60 * 60, // 30일
                }
            );
        }

        return nextResponse;
    } catch (error) {
        console.error('[Naver Callback POST] 예외 발생:', error);
        return NextResponse.json({
            success: false,
            error: error instanceof Error ? error.message : '알 수 없는 오류',
            redirectUrl: '/'
        }, { status: 500 });
    }
}

export async function GET(request: NextRequest) {
    try {
        const searchParams = request.nextUrl.searchParams;
        const code = searchParams.get('code');
        const state = searchParams.get('state');
        const error = searchParams.get('error');

        console.log('네이버 콜백 수신:', { code: code?.substring(0, 20) + '...', state, error });

        if (error) {
            console.error('네이버 인증 에러:', error);
            return NextResponse.redirect(new URL('/', request.url));
        }

        if (!code) {
            console.error('네이버 인증 코드가 없습니다.');
            return NextResponse.redirect(new URL('/', request.url));
        }

        const apiUrl = process.env.NEXT_PUBLIC_API_URL;
        const backendUrl = `https://${apiUrl}/api/auth/naver/callback?code=${encodeURIComponent(code)}${state ? `&state=${encodeURIComponent(state)}` : ''}`;

        const response = await fetch(backendUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            redirect: 'manual',
        });

        if (response.status >= 300 && response.status < 400) {
            const redirectUrl = response.headers.get('Location');
            if (redirectUrl) {
                const redirectUrlObj = new URL(redirectUrl);
                const refreshToken = redirectUrlObj.searchParams.get('refresh_token');
                const errorParam = redirectUrlObj.searchParams.get('error');

                if (errorParam) {
                    return NextResponse.redirect(new URL('/', request.url));
                }

                const nextResponse = NextResponse.redirect(new URL('/dashboard/naver', request.url));
                
                if (refreshToken) {
                    return handleLoginSuccess(
                        nextResponse,
                        refreshToken,
                        {
                            maxAge: 30 * 24 * 60 * 60,
                            redirectUrl: new URL('/dashboard/naver', request.url).toString(),
                        }
                    );
                }

                return nextResponse;
            }
        }

        if (!response.ok) {
            return NextResponse.redirect(new URL('/dashboard/naver', request.url));
        }

        try {
            const data = await response.json();
            const refreshToken = data.refresh_token || data.refreshToken;
            if (refreshToken) {
                const nextResponse = NextResponse.redirect(new URL('/dashboard/naver', request.url));
                return handleLoginSuccess(
                    nextResponse,
                    refreshToken,
                    {
                        maxAge: 30 * 24 * 60 * 60,
                        redirectUrl: new URL('/dashboard/naver', request.url).toString(),
                    }
                );
            }
        } catch (jsonError) {
            console.error('JSON 파싱 오류:', jsonError);
        }

        return NextResponse.redirect(new URL('/dashboard/naver', request.url));
    } catch (error) {
        console.error('네이버 콜백 API 오류:', error);
        return NextResponse.redirect(new URL('/dashboard/naver', request.url));
    }
}

