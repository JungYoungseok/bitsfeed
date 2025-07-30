# 🚀 .NET Core 8 Sample API with Datadog APM

이 프로젝트는 **Datadog APM 모니터링 검증**을 위한 .NET Core 8 기반 샘플 애플리케이션입니다.

## 📋 **프로젝트 개요**

### **주요 목적**
- .NET Core 8 애플리케이션의 Datadog APM 통합 검증
- MySQL 데이터베이스 연결 및 성능 모니터링
- 커스텀 메트릭 및 트레이싱 구현
- Kubernetes 환경에서의 APM 동작 테스트

### **기술 스택**
- **.NET Core 8.0** - 최신 .NET 플랫폼
- **Entity Framework Core** - ORM 및 데이터베이스 액세스
- **MySQL 8.0** - 관계형 데이터베이스
- **Datadog APM** - 애플리케이션 성능 모니터링
- **Docker & Kubernetes** - 컨테이너 오케스트레이션
- **Swagger/OpenAPI** - API 문서화

## 🏗️ **아키텍처**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │────│  .NET Core API   │────│     MySQL       │
│  (Next.js)      │    │   (Port 5000)    │    │   (Port 3306)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                               │
                       ┌──────────────────┐
                       │   Datadog Agent  │
                       │   (APM + Logs)   │
                       └──────────────────┘
```

## 🔧 **주요 기능**

### **1. Health Check Endpoints**
- `GET /api/health` - 기본 헬스 체크
- `GET /api/health/detailed` - 상세 헬스 체크 (DB 포함)
- `GET /api/health/database` - 데이터베이스 연결 상태
- `GET /api/health/metrics` - 시스템 메트릭 조회

### **2. User Management API**
- `GET /api/users` - 모든 사용자 조회
- `GET /api/users/{id}` - 특정 사용자 조회
- `POST /api/users` - 새 사용자 생성
- `PUT /api/users/{id}` - 사용자 정보 업데이트
- `DELETE /api/users/{id}` - 사용자 삭제
- `GET /api/users/count` - 사용자 수 조회
- `POST /api/users/bulk` - 대량 사용자 생성 (성능 테스트용)

### **3. APM 테스트 Endpoints**
- `GET /api/health/slow?delayMs=1000` - 의도적 지연 (성능 테스트)
- `GET /api/health/error?type=database` - 의도적 에러 (에러 추적)

## 📊 **Datadog APM 통합**

### **추적되는 메트릭**
- **HTTP 요청/응답** - 응답 시간, 상태 코드, 처리량
- **데이터베이스 쿼리** - SQL 실행 시간, 연결 수
- **커스텀 스팬** - 비즈니스 로직별 성능 추적
- **시스템 메트릭** - 메모리, CPU, GC 정보
- **에러 추적** - 예외 발생 및 스택 트레이스

### **커스텀 태그**
```csharp
scope.Span.SetTag("user.id", userId);
scope.Span.SetTag("operation.duration_ms", elapsed);
scope.Span.SetTag("database.status", "connected");
```

## 🚀 **실행 방법**

### **1. Docker Compose로 실행**
```bash
# 전체 서비스 시작 (MySQL + .NET API + Frontend)
docker-compose up --build -d

# .NET API 로그 확인
docker-compose logs -f dotnet-sample

# MySQL 로그 확인
docker-compose logs -f mysql
```

### **2. 개별 실행 (개발 환경)**
```bash
# MySQL 시작
docker run -d --name mysql-dev \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=dotnet_sample \
  -p 3306:3306 mysql:8.0

# .NET API 실행
cd dotnet-sample
dotnet restore
dotnet run
```

### **3. Kubernetes 배포**
```bash
# MySQL 배포
kubectl apply -f k8s/mysql-deployment.yaml

# .NET API 배포
kubectl apply -f k8s/dotnet-deployment.yaml

# 서비스 상태 확인
kubectl get pods -l app=dotnet-sample
kubectl get pods -l app=mysql
```

## 🔍 **API 테스트**

### **Health Check**
```bash
# 기본 헬스 체크
curl http://localhost:5000/api/health

# 상세 헬스 체크 (DB 포함)
curl http://localhost:5000/api/health/detailed

# 시스템 메트릭
curl http://localhost:5000/api/health/metrics
```

### **User API**
```bash
# 사용자 목록
curl http://localhost:5000/api/users

# 새 사용자 생성
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com"}'

# 대량 사용자 생성 (성능 테스트)
curl -X POST "http://localhost:5000/api/users/bulk?count=50"
```

### **APM 테스트**
```bash
# 지연 시뮬레이션 (3초)
curl "http://localhost:5000/api/health/slow?delayMs=3000"

# 에러 시뮬레이션
curl "http://localhost:5000/api/health/error?type=database"
```

## 📱 **Frontend 통합**

Next.js 프론트엔드에서 다음 URL로 접근 가능:

- **Health Check**: `http://localhost:3000/api/dotnet/health`
- **User API**: `http://localhost:3000/api/dotnet/users`
- **Swagger UI**: `http://localhost:5000/swagger`

## 🔧 **환경 변수**

### **Docker Compose**
```env
ASPNETCORE_ENVIRONMENT=Development
ConnectionStrings__DefaultConnection=Server=mysql;Database=dotnet_sample;...
DD_SERVICE=dotnet-sample
DD_ENV=dev
DD_VERSION=1.0.0
```

### **Kubernetes**
```yaml
- name: DD_AGENT_HOST
  valueFrom:
    fieldRef:
      fieldPath: status.hostIP
- name: DD_TRACE_SAMPLE_RATE
  value: "1.0"
```

## 📈 **모니터링 대시보드**

Datadog에서 확인 가능한 메트릭:

1. **서비스 맵** - `dotnet-sample` 서비스와 MySQL 연결
2. **APM 트레이스** - 각 API 호출의 상세 추적
3. **인프라 모니터링** - 컨테이너 리소스 사용량
4. **로그 집계** - 구조화된 로그 수집
5. **커스텀 메트릭** - 비즈니스 로직별 성능 지표

## 🐛 **트러블슈팅**

### **일반적인 문제**

1. **MySQL 연결 실패**
   ```bash
   # MySQL 컨테이너 상태 확인
   docker-compose ps mysql
   docker-compose logs mysql
   ```

2. **.NET API 시작 실패**
   ```bash
   # 의존성 확인
   docker-compose logs dotnet-sample
   ```

3. **Datadog Agent 연결 실패**
   ```bash
   # Agent 상태 확인
   kubectl get pods -n datadog
   ```

## 📚 **추가 자료**

- [Datadog .NET APM 설정 가이드](https://docs.datadoghq.com/tracing/setup_overview/setup/dotnet-core/)
- [Entity Framework Core 문서](https://docs.microsoft.com/en-us/ef/core/)
- [.NET Core 8 릴리스 노트](https://docs.microsoft.com/en-us/dotnet/core/whats-new/dotnet-8)

---

🚀 **이 샘플 프로젝트는 .NET Core 애플리케이션의 Datadog APM 통합을 완벽하게 검증할 수 있도록 설계되었습니다!**

### 📝 **최근 업데이트**
- 2025-01-30: GitHub Actions build-dotnet job ARM64 호환성 개선
- 2025-01-30: deploy-dotnet job EKS 연결 디버깅 강화 