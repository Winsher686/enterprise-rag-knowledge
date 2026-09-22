# ---------- 构建阶段 ----------
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json ./
RUN npm install --no-audit --no-fund

COPY . .
RUN npm run build

# ---------- 运行阶段 ----------
FROM nginx:1.25-alpine

# 自定义 nginx 配置（含 /api 反向代理）
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 静态资源
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]