import { NextRequest, NextResponse } from 'next/server';

/**
 * Access Token 갱신 API
 * - HttpOnly 쿠키에서 Refresh Token을 읽어 백엔드에 전달
 * - 새로운 Access Token을 반환
 */
export async function POST(request: NextRequest) {
  try {
    // HttpOnly 쿠키에서 Refresh Token 가져오기
    const refreshToken = request.cookies.get('refreshToken')?.value;

    if (!refreshToken) {
      return NextResponse.json(
        { error: 'Refresh Token이 없습니다' },
        { status: 401 }
      );
    }

    // 백엔드 API URL
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'api.minsol.kr';
    const backendUrl = apiUrl.startsWith('http') ? apiUrl : `https://${apiUrl}`;

    // 백엔드에 Refresh Token 전달하여 새로운 Access Token 요청
    const response = await fetch(`${backendUrl}/api/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refreshToken }),
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Access Token 갱신 실패' },
        { status: response.status }
      );
    }

    const data = await response.json();

    return NextResponse.json({
      accessToken: data.accessToken,
    });
  } catch (error) {
    console.error('[Refresh API] 오류:', error);
    return NextResponse.json(
      { error: 'Access Token 갱신 중 오류가 발생했습니다' },
      { status: 500 }
    );
  }
}

