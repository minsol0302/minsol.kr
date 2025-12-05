'use client';

import { useRouter } from 'next/navigation';

export default function Dashboard() {
    const router = useRouter();

    const handleLogout = () => {
        // 로그아웃 로직 추가
        console.log("로그아웃");
        router.push('/');
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-white font-sans">
            <main className="flex w-full max-w-md flex-col items-center gap-8 px-8 py-16">
                <h1 className="text-4xl font-bold text-gray-900 text-center">
                    구글 로그인이 성공했습니다.
                </h1>
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

