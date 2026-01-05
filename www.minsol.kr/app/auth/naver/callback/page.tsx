import { Suspense } from 'react';
import NaverCallbackClient from './NaverCallbackClient';

// Force dynamic rendering to prevent static generation
export const dynamic = 'force-dynamic';

export default function NaverCallback() {
    return (
        <Suspense fallback={
            <div className="flex min-h-screen items-center justify-center bg-white">
                <div className="text-center">
                    <p className="text-lg text-gray-600">네이버 로그인 처리 중...</p>
                </div>
            </div>
        }>
            <NaverCallbackClient />
        </Suspense>
    );
}

