# Service Layer

이 디렉토리는 비즈니스 로직을 담당하는 마이크로서비스들을 포함합니다.

## 구조

이 프로젝트는 **멀티 프로젝트 구조**로 구성되어 있습니다:

```
core.labzang.com/
├── build.gradle          # 루트 빌드 설정 (공통 의존성 관리)
├── settings.gradle       # 멀티 프로젝트 설정
├── oauthservice/        # OAuth 인증 서비스 (8081)
└── userservice/         # 사용자 관리 서비스 (8082)
```

## 빌드 방법

### 전체 서비스 빌드
```bash
cd core.labzang.com
./gradlew build
```

### 개별 서비스 빌드
```bash
# OAuth 서비스만 빌드
cd core.labzang.com/oauthservice
./gradlew build

# User 서비스만 빌드
cd core.labzang.com/userservice
./gradlew build
```

## 공통 설정

- **Java 버전**: 21
- **Spring Boot**: 3.5.7
- **Spring Cloud**: 2025.0.0
- **공통 의존성**: Lombok, Spring Boot DevTools, JUnit

## 서비스별 특수 의존성

### oauthservice
- Spring WebFlux
- Spring Data Redis
- JWT (jjwt)

### userservice
- Spring Web

## Docker 빌드

각 서비스는 독립적으로 Docker 이미지를 빌드할 수 있습니다:

```bash
# OAuth 서비스
docker build -t oauthservice:latest ./core.labzang.com/oauthservice

# User 서비스
docker build -t userservice:latest ./core.labzang.com/userservice
```

또는 `docker-compose.local.yaml`을 사용하여 전체 스택을 실행할 수 있습니다.

