# news-frontend/Dockerfile
# 1단계: dependencies 설치
FROM node:20-alpine AS deps
WORKDIR /app

# package.json과 package-lock.json만 먼저 복사
COPY package.json package-lock.json ./
RUN npm ci --only=production --ignore-scripts

# 2단계: 코드 복사 및 빌드
FROM node:20-alpine AS builder
WORKDIR /app

# deps 단계에서 설치한 node_modules 복사
COPY --from=deps /app/node_modules ./node_modules
COPY package.json package-lock.json ./

# 개발 dependencies 설치 (빌드용)
RUN npm ci --ignore-scripts

# 소스 코드 복사
COPY . .

# Next.js 빌드
RUN npm run build

# 3단계: 실행 이미지 (더 작은 alpine 이미지 사용)
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV NEXT_TELEMETRY_DISABLED=1

# 시스템 사용자 추가 (보안)
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# 필수 파일들만 복사
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

USER nextjs

EXPOSE 3000

CMD ["npm", "start"]