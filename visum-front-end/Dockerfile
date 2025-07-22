FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

RUN npm run build

FROM node:18-alpine

WORKDIR /app

# Copy the standalone output from the build stage
COPY --from=0 /app/.next/standalone ./
COPY --from=0 /app/public ./public
COPY --from=0 /app/.next/static ./.next/static
COPY --from=0 /app/node_modules ./node_modules
COPY --from=0 /app/package.json ./package.json

EXPOSE 3000

CMD ["node", "server.js"]
