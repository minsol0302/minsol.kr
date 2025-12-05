# npm run dev 에러 해결

## 🔍 문제

```
'next'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다.
```

## 📋 원인

- `package.json`은 존재하지만 `node_modules` 디렉토리가 없었음
- Next.js 및 기타 의존성이 설치되지 않았음
- `npm install`을 실행하지 않아서 발생한 문제

## ✅ 해결 방법

### 1. 의존성 설치
```powershell
cd admin.labzang.com
npm install
```

### 2. 개발 서버 실행
```powershell
npm run dev
```

## 🎯 해결 완료

**실행 결과:**
```
added 428 packages, and audited 429 packages in 58s
found 0 vulnerabilities
```

## 💡 앞으로 사용법

### 초기 설정 (처음 한 번만)
```powershell
cd admin.labzang.com
npm install
```

### 개발 서버 실행
```powershell
npm run dev
```

서버가 `http://localhost:4000`에서 실행됩니다.

## 📝 참고

- **npm install**: `package.json`에 정의된 모든 의존성을 설치
- **node_modules**: 설치된 패키지들이 저장되는 디렉토리
- **package-lock.json**: 설치된 패키지의 정확한 버전을 기록 (자동 생성)
- **pnpm-lock.yaml**: pnpm을 사용한 경우 생성되는 파일 (npm과 함께 사용 가능)

## ⚠️ 주의사항

- `node_modules` 디렉토리는 `.gitignore`에 포함되어 있어 Git에 커밋되지 않음
- 새로운 환경에서 프로젝트를 클론한 경우 항상 `npm install`을 먼저 실행해야 함
- `package.json`이 변경된 경우에도 `npm install`을 다시 실행해야 함

