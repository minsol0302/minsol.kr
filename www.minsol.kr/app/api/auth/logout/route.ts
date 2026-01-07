import { NextResponse } from 'next/server';

/**
 * 로그아웃 API
 * - HttpOnly 쿠키에 저장된 Refresh Token 제거
 */
export async function POST() {
  try {
    const response = NextResponse.json(
      { message: '로그아웃 성공' },
      { status: 200 }
    );

    // HttpOnly 쿠키 제거
    response.cookies.set('refreshToken', '', {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 0, // 즉시 만료
      path: '/',
    });

    return response;
  } catch (error) {
    console.error('[Logout API] 오류:', error);
    return NextResponse.json(
      { error: '로그아웃 처리 중 오류가 발생했습니다' },
      { status: 500 }
    );
  }
}

