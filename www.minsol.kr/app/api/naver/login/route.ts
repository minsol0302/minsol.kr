import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    try {
        // 백엔드 서버로 요청 프록시
        const backendUrl = 'http://localhost:8080/naver/login';

        // 요청 body를 읽어서 백엔드로 전달
        const body = await request.json().catch(() => ({}));

        const response = await fetch(backendUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            const errorText = await response.text().catch(() => '');
            console.error('백엔드 오류:', response.status, errorText);
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
        return NextResponse.json(data);
    } catch (error) {
        console.error('네이버 로그인 API 오류:', error);
        return NextResponse.json(
            {
                success: false,
                error: '백엔드 서버에 연결할 수 없습니다.',
                message: error instanceof Error ? error.message : '알 수 없는 오류'
            },
            { status: 500 }
        );
    }
}

