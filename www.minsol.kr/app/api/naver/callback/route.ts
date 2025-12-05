import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
    try {
        // URL에서 code 파라미터 추출
        const searchParams = request.nextUrl.searchParams;
        const code = searchParams.get('code');
        const error = searchParams.get('error');

        console.log('네이버 콜백 수신:', { code: code?.substring(0, 20) + '...', error });

        // 에러가 있으면 로그인 페이지로 리다이렉트
        if (error) {
            console.error('네이버 인증 에러:', error);
            return NextResponse.redirect(new URL('/', request.url));
        }

        // code가 없으면 에러
        if (!code) {
            console.error('네이버 인증 코드가 없습니다.');
            return NextResponse.redirect(new URL('/', request.url));
        }

        // 백엔드 콜백 엔드포인트로 프록시
        const backendUrl = `http://localhost:8080`;
        console.log('백엔드로 요청 전송:', backendUrl.substring(0, 80) + '...');

        const response = await fetch(backendUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
        });

        console.log('백엔드 응답 상태:', response.status);

        if (!response.ok) {
            const errorText = await response.text().catch(() => '');
            console.error('백엔드 콜백 오류:', response.status, errorText);

            // 백엔드가 500 에러를 반환하더라도, 쿠키에 세션이 저장되었을 수 있으므로
            // 대시보드로 이동 시도
            return NextResponse.redirect(new URL('/dashboard/naver', request.url));
        }

        try {
            const data = await response.json();
            console.log('백엔드 응답 데이터:', data);

            // 백엔드에서 로그인 성공 메시지가 오면 대시보드로 리다이렉트
            // 다양한 메시지 형식 지원
            const message = data.message || data.msg || data.status;
            if (
                message === "네이버 로그인 성공" ||
                message === "로그인 성공" ||
                message === "success" ||
                data.success === true ||
                data.status === "success"
            ) {
                return NextResponse.redirect(new URL('/dashboard/naver', request.url));
            }
        } catch (jsonError) {
            console.error('JSON 파싱 오류:', jsonError);
            // JSON 파싱 실패해도 대시보드로 이동
        }

        // 기본적으로 대시보드로 리다이렉트 (백엔드가 성공적으로 응답했으면)
        return NextResponse.redirect(new URL('/dashboard/naver', request.url));
    } catch (error) {
        console.error('네이버 콜백 API 오류:', error);
        // 에러 발생 시에도 대시보드로 이동 시도
        return NextResponse.redirect(new URL('/dashboard/naver', request.url));
    }
}

