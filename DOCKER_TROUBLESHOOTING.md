# Docker Compose 실행 가이드

## 문제 해결

### Docker Desktop API 오류 (500 Internal Server Error)

이 오류는 Docker Desktop이 제대로 실행되지 않았을 때 발생합니다.

#### 해결 방법:

1. **Docker Desktop 재시작**
   - Docker Desktop을 완전히 종료
   - Docker Desktop을 다시 시작
   - Docker Desktop이 완전히 시작될 때까지 대기 (시스템 트레이 아이콘 확인)

2. **올바른 디렉토리에서 실행**
   ```powershell
   # 프로젝트 루트로 이동
   cd C:\Users\hi\Documents\my_project\minsol.kr
   
   # Gateway 실행
   docker compose -p minsol-gateway -f docker-compose.local.yaml up --build gateway
   ```

3. **Docker Desktop 상태 확인**
   ```powershell
   docker ps
   ```
   - 이 명령이 성공하면 Docker Desktop이 정상 작동 중입니다.
   - 실패하면 Docker Desktop을 재시작하세요.

4. **기존 컨테이너/이미지 정리 (필요시)**
   ```powershell
   # 모든 컨테이너 중지 및 제거
   docker compose -p minsol-gateway -f docker-compose.local.yaml down
   
   # 사용하지 않는 이미지 정리
   docker image prune -a
   ```

## 환경 변수 설정

`.env` 파일이 없으면 환경 변수 경고가 나타납니다. 이는 정상이며, 기본값이 사용됩니다.

필요한 환경 변수를 설정하려면 프로젝트 루트에 `.env` 파일을 생성하세요:

```env
# Spring Boot 설정
SPRING_PROFILES_ACTIVE=default
SPRING_JPA_HIBERNATE_DDL_AUTO=update
SPRING_JPA_SHOW_SQL=true

# Redis 설정 (선택적)
REDIS_ENABLED=false
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# JWT 설정
JWT_SECRET=your-secret-key
JWT_ACCESS_TOKEN_EXPIRATION=3600000
JWT_REFRESH_TOKEN_EXPIRATION=2592000000

# OAuth 설정 (선택적)
KAKAO_REST_API_KEY=
KAKAO_REDIRECT_URI=
KAKAO_CLIENT_SECRET=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
NAVER_REDIRECT_URI=
```

## 실행 명령어

### Gateway만 실행
```powershell
cd C:\Users\hi\Documents\my_project\minsol.kr
docker compose -p minsol-gateway -f docker-compose.local.yaml up --build gateway
```

### 백그라운드 실행
```powershell
docker compose -p minsol-gateway -f docker-compose.local.yaml up -d gateway
```

### 로그 확인
```powershell
docker compose -p minsol-gateway -f docker-compose.local.yaml logs -f gateway
```

### 중지
```powershell
docker compose -p minsol-gateway -f docker-compose.local.yaml down
```

