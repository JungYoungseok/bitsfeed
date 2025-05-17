# news-frontend/Dockerfile
# 1단계: dependencies 설치
FROM node:20 AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install

# 2단계: 코드 복사 및 빌드
FROM node:20 AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# 3단계: 실행 이미지
FROM node:20 AS runner
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules ./node_modules
ENV PORT 3000
EXPOSE 3000
CMD ["npm", "start"]