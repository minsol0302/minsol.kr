/**
 * API 설정 유틸리티
 * 환경 변수에서 API URL을 가져옵니다.
 */

export function getApiUrl(): string {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL;

    if (!apiUrl) {
        // 개발 환경에서는 localhost 사용
        if (process.env.NODE_ENV === 'development') {
            return 'api.minsol.kr';
        }
        throw new Error('NEXT_PUBLIC_API_URL 환경 변수가 설정되지 않았습니다.');
    }

    return apiUrl;
}

export const API_BASE_URL = getApiUrl();

