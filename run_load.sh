#!/usr/bin/env bash
# run_all.sh: Chạy metadata.sql (tạo bảng) rồi load_all.sql (nạp dữ liệu)

# 1) Cấu hình Database
DB_HOST="dw-btl-hk242-dw-btl-hk241.k.aivencloud.com"
DB_PORT="15152"
DB_NAME="test"
DB_USER="avnadmin"
DB_PASS="AVNS_C9d4wybaKUzyAQ9ZxMs"

# 2) Export password để psql đọc
export PGPASSWORD="$DB_PASS"

# 3) Đường dẫn file .sql
META_SQL="metadata.sql"
LOAD_SQL="load_all.sql"

# 4) Kết nối SSL (nếu cần) – Tùy Aiven, 
#    Thường sslmode=require đã đủ.
#    Dùng --set=sslmode=require => 1 trong 2
# psql options chung, cho gọn
PSQL_CMD="psql --host=$DB_HOST --port=$DB_PORT --username=$DB_USER --dbname=$DB_NAME --no-psqlrc"

# 5) Chạy file metadata.sql => tạo bảng
echo "=== Running $META_SQL ==="
$PSQL_CMD -f "$META_SQL" || { echo "metadata.sql failed!"; exit 1; }

# 6) Chạy file load_all.sql => nạp dữ liệu
echo "=== Running $LOAD_SQL ==="
$PSQL_CMD -f "$LOAD_SQL" || { echo "load_all.sql failed!"; exit 1; }

echo "=== All Done! ==="

