'use client';

import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  const handleGoogleLogin = async () => {
    // 구글 로그인 로직 추가
    try {
      const data = await callGoogleGateway();
      console.log("구글 로그인 응답:", data);

      // 백엔드에서 구글 인증 URL이 오면 해당 URL로 리다이렉트
      // 콜백 URL이 아닌 구글 인증 URL인지 확인 (accounts.google.com 포함)
      const authUrl = data.redirectUrl || data.url || data.authUrl || data.authorizationUrl;
      if (authUrl && (authUrl.includes('accounts.google.com') || authUrl.includes('oauth.google.com'))) {
        window.location.href = authUrl;
        return;
      }

      // 백엔드에서 로그인 성공 메시지가 오면 대시보드로 이동
      // 다양한 메시지 형식 지원
      const message = data.message || data.msg || data.status;
      if (
        message === "구글 로그인 성공" ||
        message === "로그인 성공" ||
        message === "success" ||
        data.success === true ||
        data.status === "success"
      ) {
        router.push('/dashboard/google');
        return;
      }

      // JSON 응답이 성공적으로 왔지만 메시지가 없는 경우에도 대시보드로 이동
      if (data && typeof data === 'object') {
        router.push('/dashboard/google');
      }
    } catch (error) {
      console.error("구글 로그인 실패:", error);
    }
  };

  async function callGoogleGateway() {
    const res = await fetch("http://localhost:8080/api/auth/google/login", {
      method: "POST",
      credentials: "include", // 쿠키를 쓰면 필요
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}), // 빈 객체 전송 (required = false이므로)
    });

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const data = await res.json();
    return data;
  };

  const handleKakaoLogin = async () => {
    // 카카오 로그인 로직 추가
    try {
      const data = await callGateway();
      console.log("카카오 로그인 응답:", data);

      // 백엔드에서 카카오 인증 URL이 오면 해당 URL로 리다이렉트
      // 콜백 URL이 아닌 카카오 인증 URL인지 확인 (kauth.kakao.com 또는 oauth.kakao.com 포함)
      const authUrl = data.redirectUrl || data.url || data.authUrl || data.authorizationUrl;
      if (authUrl && (authUrl.includes('kauth.kakao.com') || authUrl.includes('oauth.kakao.com'))) {
        window.location.href = authUrl;
        return;
      }

      // 백엔드에서 로그인 성공 메시지가 오면 대시보드로 이동
      // 다양한 메시지 형식 지원
      const message = data.message || data.msg || data.status;
      if (
        message === "카카오 로그인 성공" ||
        message === "로그인 성공" ||
        message === "success" ||
        data.success === true ||
        data.status === "success"
      ) {
        router.push('/dashboard/kakao');
        return;
      }

      // JSON 응답이 성공적으로 왔지만 메시지가 없는 경우에도 대시보드로 이동
      if (data && typeof data === 'object') {
        router.push('/dashboard/kakao');
      }
    } catch (error) {
      console.error("카카오 로그인 실패:", error);
    }
  };

  async function callGateway() {
    const res = await fetch("http://localhost:8080/api/auth/kakao/login", {
      method: "POST",
      credentials: "include", // 쿠키를 쓰면 필요
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}), // 빈 객체 전송 (required = false이므로)
    });

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const data = await res.json();
    return data;
  };

  const handleNaverLogin = async () => {
    // 네이버 로그인 로직 추가
    try {
      const data = await callNaverGateway();
      console.log("네이버 로그인 응답:", data);

      // 백엔드에서 네이버 인증 URL이 오면 해당 URL로 리다이렉트
      // 콜백 URL이 아닌 네이버 인증 URL인지 확인 (nid.naver.com 포함)
      const authUrl = data.redirectUrl || data.url || data.authUrl || data.authorizationUrl;
      if (authUrl && (authUrl.includes('nid.naver.com') || authUrl.includes('oauth.naver.com'))) {
        window.location.href = authUrl;
        return;
      }

      // 백엔드에서 로그인 성공 메시지가 오면 대시보드로 이동
      // 다양한 메시지 형식 지원
      const message = data.message || data.msg || data.status;
      if (
        message === "네이버 로그인 성공" ||
        message === "로그인 성공" ||
        message === "success" ||
        data.success === true ||
        data.status === "success"
      ) {
        router.push('/dashboard/naver');
        return;
      }

      // JSON 응답이 성공적으로 왔지만 메시지가 없는 경우에도 대시보드로 이동
      if (data && typeof data === 'object') {
        router.push('/dashboard/naver');
      }
    } catch (error) {
      console.error("네이버 로그인 실패:", error);
    }
  };

  async function callNaverGateway() {
    const res = await fetch("http://localhost:8080/api/auth/naver/login", {
      method: "POST",
      credentials: "include", // 쿠키를 쓰면 필요
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}), // 빈 객체 전송 (required = false이므로)
    });

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const data = await res.json();
    return data;
  }


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