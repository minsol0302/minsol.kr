'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function Home() {
  const router = useRouter();

  // URL 파라미터에서 에러 확인 및 콘솔에 출력 (클라이언트 사이드에서만)
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      const error = urlParams.get('error');
      if (error) {
        console.error('[로그인 페이지] URL 파라미터에서 에러 감지:', decodeURIComponent(error));
        console.error('[로그인 페이지] 전체 URL:', window.location.href);
        // URL에서 에러 파라미터 제거
        urlParams.delete('error');
        const newUrl = window.location.pathname + (urlParams.toString() ? '?' + urlParams.toString() : '');
        router.replace(newUrl);
      }
    }
  }, [router]);

  const handleGoogleLogin = async () => {
    // 구글 로그인 로직 추가
    try {
      console.log('[구글 로그인] 시작');
      // 백엔드 API 직접 호출
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'api.minsol.kr';

      if (!apiUrl) {
        alert('API URL이 설정되지 않았습니다. 환경 변수를 확인해주세요.');
        return;
      }

      const authUrlResponse = await fetch(`https://${apiUrl}/api/auth/google/auth-url`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });

      console.log('[구글 로그인] API 응답 상태:', authUrlResponse.status);

      if (!authUrlResponse.ok) {
        let errorMessage = `HTTP 오류 (${authUrlResponse.status})`;
        let errorData: any = {};

        try {
          const contentType = authUrlResponse.headers.get('content-type');
          if (contentType && contentType.includes('application/json')) {
            errorData = await authUrlResponse.json();
            errorMessage = errorData.message || errorData.error || errorMessage;
          } else {
            // HTML 응답인 경우 (502 Bad Gateway 등)
            const text = await authUrlResponse.text();
            if (text.includes('502 Bad Gateway') || text.includes('<html>')) {
              errorMessage = '백엔드 서버에 연결할 수 없습니다. 서버 상태를 확인 중이니 잠시 후 다시 시도해주세요.';
            } else {
              errorMessage = text.substring(0, 200) || errorMessage;
            }
          }
        } catch (parseError) {
          console.error('[구글 로그인] 응답 파싱 오류:', parseError);
          errorMessage = `서버 응답 오류 (${authUrlResponse.status})`;
        }

        console.error('[구글 로그인] 오류 상세:', {
          status: authUrlResponse.status,
          statusText: authUrlResponse.statusText,
          error: errorData,
          message: errorMessage
        });

        // 502, 503 오류는 서버 연결 문제
        if (authUrlResponse.status === 502 || authUrlResponse.status === 503) {
          alert('백엔드 서버에 연결할 수 없습니다.\n서버 관리자에게 문의하거나 잠시 후 다시 시도해주세요.');
        } else {
          alert(`구글 로그인 실패: ${errorMessage}`);
        }
        return;
      }

      const authUrlData = await authUrlResponse.json();
      console.log('[구글 로그인] 응답 데이터:', authUrlData);
      const authUrl = authUrlData.auth_url;

      if (authUrl) {
        console.log('[구글 로그인] 인증 URL로 리다이렉트:', authUrl);
        // 인증 URL로 리다이렉트
        window.location.href = authUrl;
      } else {
        console.error('[구글 로그인] 인증 URL이 응답에 없습니다:', authUrlData);
        alert('구글 인증 URL을 받을 수 없습니다.');
      }
    } catch (error) {
      console.error('[구글 로그인] 예외 발생:', error);
      console.error('[구글 로그인] 에러 스택:', error instanceof Error ? error.stack : '스택 없음');
      alert(`구글 로그인 중 오류가 발생했습니다. 콘솔을 확인하세요.`);
    }
  };

  const handleKakaoLogin = async () => {
    // 카카오 로그인 로직 추가
    try {
      console.log('[카카오 로그인] 시작');
      // 백엔드 API 직접 호출
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'api.minsol.kr';

      if (!apiUrl) {
        alert('API URL이 설정되지 않았습니다. 환경 변수를 확인해주세요.');
        return;
      }

      const authUrlResponse = await fetch(`https://${apiUrl}/api/auth/kakao/auth-url`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });

      console.log('[카카오 로그인] API 응답 상태:', authUrlResponse.status);

      if (!authUrlResponse.ok) {
        const errorData = await authUrlResponse.json().catch(() => ({}));
        const errorMessage = errorData.message || errorData.error || `HTTP error! status: ${authUrlResponse.status}`;
        console.error('[카카오 로그인] 오류 상세:', {
          status: authUrlResponse.status,
          statusText: authUrlResponse.statusText,
          error: errorData,
          message: errorMessage
        });
        alert(`카카오 로그인 실패: ${errorMessage}`);
        return;
      }

      const authUrlData = await authUrlResponse.json();
      console.log('[카카오 로그인] 응답 데이터:', authUrlData);
      const authUrl = authUrlData.auth_url;

      if (authUrl) {
        console.log('[카카오 로그인] 인증 URL로 리다이렉트:', authUrl);
        // 인증 URL로 리다이렉트
        window.location.href = authUrl;
      } else {
        console.error('[카카오 로그인] 인증 URL이 응답에 없습니다:', authUrlData);
        alert('카카오 인증 URL을 받을 수 없습니다.');
      }
    } catch (error) {
      console.error('[카카오 로그인] 예외 발생:', error);
      console.error('[카카오 로그인] 에러 스택:', error instanceof Error ? error.stack : '스택 없음');
      alert(`카카오 로그인 중 오류가 발생했습니다. 콘솔을 확인하세요.`);
    }
  };

  const handleNaverLogin = async () => {
    // 네이버 로그인 로직 추가
    try {
      console.log('[네이버 로그인] 시작');
      // 백엔드 API 직접 호출
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'api.minsol.kr';

      if (!apiUrl) {
        alert('API URL이 설정되지 않았습니다. 환경 변수를 확인해주세요.');
        return;
      }

      const authUrlResponse = await fetch(`https://${apiUrl}/api/auth/naver/auth-url`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({}),
      });

      console.log('[네이버 로그인] API 응답 상태:', authUrlResponse.status);

      if (!authUrlResponse.ok) {
        const errorData = await authUrlResponse.json().catch(() => ({}));
        const errorMessage = errorData.message || errorData.error || `HTTP error! status: ${authUrlResponse.status}`;
        console.error('[네이버 로그인] 오류 상세:', {
          status: authUrlResponse.status,
          statusText: authUrlResponse.statusText,
          error: errorData,
          message: errorMessage
        });
        alert(`네이버 로그인 실패: ${errorMessage}`);
        return;
      }

      const authUrlData = await authUrlResponse.json();
      console.log('[네이버 로그인] 응답 데이터:', authUrlData);
      const authUrl = authUrlData.auth_url;

      if (authUrl) {
        console.log('[네이버 로그인] 인증 URL로 리다이렉트:', authUrl);
        // 인증 URL로 리다이렉트
        window.location.href = authUrl;
      } else {
        console.error('[네이버 로그인] 인증 URL이 응답에 없습니다:', authUrlData);
        alert('네이버 인증 URL을 받을 수 없습니다.');
      }
    } catch (error) {
      console.error('[네이버 로그인] 예외 발생:', error);
      console.error('[네이버 로그인] 에러 스택:', error instanceof Error ? error.stack : '스택 없음');
      alert(`네이버 로그인 중 오류가 발생했습니다. 콘솔을 확인하세요.`);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-white font-sans">
      <main className="flex w-full max-w-md flex-col items-center gap-8 px-8 py-16">
        <h1 className="text-3xl font-bold text-gray-900">로그인</h1>
        <div className="flex w-full flex-col gap-4">
          <button
            onClick={handleGoogleLogin}
            className="flex h-14 w-full items-center justify-center gap-3 rounded-lg border border-gray-300 bg-white px-6 text-base font-medium text-gray-700 transition-colors hover:bg-gray-50"
          >
            <svg
              className="h-5 w-5"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                fill="#4285F4"
              />
              <path
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                fill="#34A853"
              />
              <path
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                fill="#FBBC05"
              />
              <path
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                fill="#EA4335"
              />
            </svg>
            구글 로그인
          </button>
          <button
            onClick={handleKakaoLogin}
            className="flex h-14 w-full items-center justify-center gap-3 rounded-lg bg-[#FEE500] px-6 text-base font-medium text-gray-900 transition-colors hover:bg-[#FDD835]"
          >
            <svg
              className="h-5 w-5"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M12 3C6.48 3 2 6.48 2 11c0 2.4 1.06 4.57 2.75 6.04L3 21l4.28-1.35C8.5 20.5 10.17 21 12 21c5.52 0 10-3.48 10-8s-4.48-10-10-10z"
                fill="#000000"
              />
            </svg>
            카카오 로그인
          </button>
          <button
            onClick={handleNaverLogin}
            className="flex h-14 w-full items-center justify-center gap-3 rounded-lg bg-[#03C75A] px-6 text-base font-medium text-white transition-colors hover:bg-[#02B350]"
          >
            <svg
              className="h-5 w-5"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M16.273 12.845L7.376 0H0v24h7.726V11.156L16.624 24H24V0h-7.727v12.845z"
                fill="#FFFFFF"
              />
            </svg>
            네이버 로그인
          </button>
        </div>
      </main>
    </div>
  );
}