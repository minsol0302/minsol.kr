import { Suspense } from 'react';
import GoogleCallbackClient from './GoogleCallbackClient';

// Force dynamic rendering to prevent static generation
export const dynamic = 'force-dynamic';

export default function GoogleCallback() {
    return (
        <Suspense fallback={
            <div className="flex min-h-screen items-center justify-center bg-white">
                <div className="text-center">
                    <p className="text-lg text-gray-600">구글 로그인 처리 중...</p>
                </div>
            </div>
        }>
            <GoogleCallbackClient />
        </Suspense>
    );
}

