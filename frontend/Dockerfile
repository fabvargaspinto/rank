FROM node:22-alpine AS base

RUN corepack enable && corepack prepare pnpm@11.2.2 --activate
WORKDIR /app

FROM base AS deps

COPY package.json pnpm-lock.yaml  pnpm-workspace.yaml ./ 
RUN pnpm install --frozen-lockfile

FROM deps AS dev

COPY . .
EXPOSE 3000
CMD ["pnpm", "dev", "--hostname", "0.0.0.0", "--port", "3000"]

FROM deps AS builder

COPY . .
RUN pnpm build

FROM node:22-alpine AS prod

WORKDIR /app
ENV NODE_ENV=production
ENV HOSTNAME=0.0.0.0
ENV PORT=3000

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
