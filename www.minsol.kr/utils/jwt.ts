/**
 * JWT 토큰 유틸리티
 * - JWT 토큰 디코딩 (클라이언트 사이드)
 * - 사용자 정보 추출
 */

export interface JWTPayload {
  sub: string; // user ID
  provider?: string;
  email?: string;
  nickname?: string;
  profile_image?: string;
  [key: string]: any;
}

/**
 * JWT 토큰 디코딩 (Base64 URL 디코딩)
 * ⚠️ 주의: 서명 검증 없이 디코딩만 수행합니다.
 * 실제 인증은 서버에서 검증해야 합니다.
 */
export function decodeJWT(token: string): JWTPayload | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    // Payload 부분 디코딩 (두 번째 부분)
    const payload = parts[1];
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(decoded) as JWTPayload;
  } catch (error) {
    console.error('[JWT Utils] 토큰 디코딩 실패:', error);
    return null;
  }
}

/**
 * JWT 토큰에서 사용자 정보 추출
 */
export function extractUserFromToken(token: string): {
  id: string;
  email?: string;
  nickname?: string;
  profileImage?: string;
  provider: 'google' | 'kakao' | 'naver';
} | null {
  const payload = decodeJWT(token);
  if (!payload || !payload.sub) {
    return null;
  }

  // Provider 추출
  const provider = (payload.provider || 'google') as 'google' | 'kakao' | 'naver';

  return {
    id: payload.sub,
    email: payload.email,
    nickname: payload.nickname || payload.name,
    profileImage: payload.profile_image || payload.picture,
    provider: provider,
  };
}

