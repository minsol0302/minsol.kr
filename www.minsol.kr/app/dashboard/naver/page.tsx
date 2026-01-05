'use client';

import { useRouter } from 'next/navigation';

export default function Dashboard() {
    const router = useRouter();

    const handleLogout = () => {
        // 로그아웃 로직 추가
        console.log("로그아웃");
        router.push('/');
    };

    const handleChatbot = () => {
        router.push('/auth/chatbot');
    };

    const handlePortfolio = () => {
        router.push('/portpolio');
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-white font-sans">
            <main className="flex w-full max-w-md flex-col items-center gap-8 px-8 py-16">
                <h1 className="text-4xl font-bold text-gray-900 text-center">
                    네이버 로그인이 성공했습니다.
                </h1>
                <p className="text-gray-600 text-center">
                    사용할 서비스를 선택해주세요.
                </p>
                <div className="flex w-full flex-col gap-4">
                    <button
                        onClick={handleChatbot}
                        className="flex h-16 w-full items-center justify-center gap-3 rounded-lg bg-blue-500 px-6 text-base font-medium text-white transition-colors hover:bg-blue-600"
                    >
                        <svg
                            className="w-6 h-6"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                            />
                        </svg>
                        챗봇
                    </button>
                    <button
                        onClick={handlePortfolio}
                        className="flex h-16 w-full items-center justify-center gap-3 rounded-lg bg-green-500 px-6 text-base font-medium text-white transition-colors hover:bg-green-600"
                    >
                        <svg
                            className="w-6 h-6"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                            />
                        </svg>
                        포트폴리오
                    </button>
                </div>
                <button
                    onClick={handleLogout}
                    className="flex h-14 w-full items-center justify-center gap-3 rounded-lg border border-gray-300 bg-white px-6 text-base font-medium text-gray-700 transition-colors hover:bg-gray-50"
                >
                    로그아웃
                </button>
            </main>
        </div>
    );
}
