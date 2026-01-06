/**
 * 인증 서비스 유틸리티
 * 
 * 🔒 Refresh Token을 HttpOnly 쿠키로 관리
 * - XSS 공격으로부터 보호
 * - JavaScript에서 직접 접근 불가능
 */

import { NextResponse } from 'next/server';

/**
 * Refresh Token을 HttpOnly 쿠키에 저장
 * 
 * ⚠️ 주의: 이 함수는 Next.js API Route (서버 사이드)에서만 사용 가능합니다.
 * 클라이언트 컴포넌트에서는 사용할 수 없습니다.
 * 
 * @param response - NextResponse 객체
 * @param refreshToken - 저장할 refresh token
 * @param maxAge - 쿠키 만료 시간 (초 단위, 기본값: 30일)
 * @returns 쿠키가 설정된 NextResponse 객체
 */
export function setRefreshTokenCookie(
    response: NextResponse,
    refreshToken: string,
    maxAge: number = 30 * 24 * 60 * 60 // 기본값: 30일
): NextResponse {
    // HttpOnly, Secure, SameSite 설정으로 보안 강화
    const cookieOptions = [
        `refresh_token=${refreshToken}`,
        `HttpOnly`, // JavaScript 접근 방지 (XSS 공격 방어)
        `Secure`, // HTTPS에서만 전송 (프로덕션 환경)
        `SameSite=Strict`, // CSRF 공격 방어
        `Path=/`, // 모든 경로에서 접근 가능
        `Max-Age=${maxAge}`, // 만료 시간 (초 단위)
    ];

    // 로컬 개발 환경에서는 Secure 옵션 제거 (HTTP 사용)
    const isProduction = process.env.NODE_ENV === 'production';
    if (!isProduction) {
        // 로컬 개발 환경: Secure 옵션 제거
        const cookieWithoutSecure = cookieOptions.filter(opt => opt !== 'Secure').join('; ');
        response.headers.set('Set-Cookie', cookieWithoutSecure);
    } else {
        // 프로덕션 환경: 모든 보안 옵션 적용
        response.headers.set('Set-Cookie', cookieOptions.join('; '));
    }

    console.log('[TokenService] Refresh Token을 HttpOnly 쿠키에 저장 완료');
    return response;
}

/**
 * HttpOnly 쿠키에서 Refresh Token을 가져오기
 * 
 * ⚠️ 주의: 이 함수는 Next.js API Route (서버 사이드)에서만 사용 가능합니다.
 * 클라이언트 컴포넌트에서는 사용할 수 없습니다.
 * 
 * @param request - NextRequest 객체 (Request 객체도 가능)
 * @returns Refresh Token 또는 null
 */
export function getRefreshTokenFromCookie(request: Request): string | null {
    const cookies = request.headers.get('cookie');
    if (!cookies) {
        return null;
    }

    // 쿠키 문자열 파싱
    const cookieArray = cookies.split(';').map(cookie => cookie.trim());
    const refreshTokenCookie = cookieArray.find(cookie => cookie.startsWith('refresh_token='));

    if (!refreshTokenCookie) {
        return null;
    }

    // 'refresh_token=' 이후의 값 추출
    const token = refreshTokenCookie.split('=')[1];
    return token || null;
}

/**
 * HttpOnly 쿠키에서 Refresh Token 삭제
 * 
 * ⚠️ 주의: 이 함수는 Next.js API Route (서버 사이드)에서만 사용 가능합니다.
 * 클라이언트 컴포넌트에서는 사용할 수 없습니다.
 * 
 * @param response - NextResponse 객체
 * @returns 쿠키가 삭제된 NextResponse 객체
 */
export function clearRefreshTokenCookie(response: NextResponse): NextResponse {
    // 쿠키 만료 시키기 (Max-Age=0 또는 Expires를 과거로 설정)
    response.headers.set(
        'Set-Cookie',
        'refresh_token=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0'
    );

    console.log('[TokenService] Refresh Token 쿠키 삭제 완료');
    return response;
}

/**
 * 로그인 성공 시 Refresh Token을 HttpOnly 쿠키에 저장하는 헬퍼 함수
 * 
 * 이 함수는 API Route의 응답 객체를 받아서 refresh token을 쿠키에 설정합니다.
 * 
 * @param response - NextResponse 객체
 * @param refreshToken - 저장할 refresh token
 * @param options - 추가 옵션
 * @returns 쿠키가 설정된 NextResponse 객체
 */
export function handleLoginSuccess(
    response: NextResponse,
    refreshToken: string | null | undefined,
    options?: {
        maxAge?: number;
        redirectUrl?: string;
    }
): NextResponse {
    if (!refreshToken) {
        console.warn('[TokenService] Refresh Token이 없어 쿠키에 저장하지 않습니다.');
        return response;
    }

    // Refresh Token을 HttpOnly 쿠키에 저장
    const maxAge = options?.maxAge || 30 * 24 * 60 * 60; // 기본값: 30일
    setRefreshTokenCookie(response, refreshToken, maxAge);

    // 리다이렉트 URL이 있으면 리다이렉트
    if (options?.redirectUrl) {
        return NextResponse.redirect(options.redirectUrl);
    }

    return response;
}

/**
 * 로그아웃 시 Refresh Token 쿠키를 삭제하는 헬퍼 함수
 * 
 * @param response - NextResponse 객체
 * @param redirectUrl - 로그아웃 후 이동할 URL (선택사항)
 * @returns 쿠키가 삭제된 NextResponse 객체
 */
export function handleLogout(
    response: NextResponse,
    redirectUrl?: string
): NextResponse {
    // Refresh Token 쿠키 삭제
    clearRefreshTokenCookie(response);

    // 리다이렉트 URL이 있으면 리다이렉트
    if (redirectUrl) {
        return NextResponse.redirect(redirectUrl);
    }

    return response;
}

