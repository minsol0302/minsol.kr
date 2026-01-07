import { NextRequest, NextResponse } from 'next/server';

/**
 * Access Token 유효성 검증 API
 * - Authorization 헤더에서 Access Token을 읽어 백엔드에 전달
 * - 토큰이 유효한지 확인
 */
export async function POST(request: NextRequest) {
  try {
    // Authorization 헤더에서 Access Token 가져오기
    const authHeader = request.headers.get('authorization');
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json(
        { error: 'Access Token이 없습니다' },
        { status: 401 }
      );
    }

    const accessToken = authHeader.substring(7); // "Bearer " 제거

    // 백엔드 API URL
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'http://localhost:8080';
    const backendUrl = apiUrl.startsWith('http') ? apiUrl : `https://${apiUrl}`;

    // 백엔드에 Access Token 전달하여 유효성 검증
    const response = await fetch(`${backendUrl}/api/auth/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`,
      },
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: 'Access Token이 유효하지 않습니다' },
        { status: response.status }
      );
    }

    const data = await response.json();

    return NextResponse.json({
      valid: true,
      user: data.user,
    });
  } catch (error) {
    console.error('[Validate API] 오류:', error);
    return NextResponse.json(
      { error: 'Access Token 검증 중 오류가 발생했습니다' },
      { status: 500 }
    );
  }
}

