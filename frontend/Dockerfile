# Sửa phiên bản Node.js lên 20
FROM node:20-alpine

# Thư mục làm việc trong container
WORKDIR /app

# Copy các file quản lý thư viện vào trước để cài đặt
COPY package*.json ./
RUN npm install --legacy-peer-deps

# Copy toàn bộ code vào
COPY . .

# Mở port 5173 cho React/Vite
EXPOSE 5173

# Lệnh chạy dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]