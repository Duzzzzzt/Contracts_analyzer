# Frontend (Vite + React) — образ для РАЗРАБОТКИ с автоперезапуском (HMR).
# Образ собирается один раз (ставит зависимости из package-lock.json).
# Исходники монтируются из проекта в контейнер, поэтому правки видны
# в браузере сразу, без пересборки.
# Продакшен-сборка (статический сайт на nginx) — см. Dockerfile.prod.
FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

EXPOSE 5173

# --host нужен, чтобы Vite слушал все интерфейсы внутри контейнера
CMD ["npm", "run", "dev", "--", "--host"]