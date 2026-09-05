-- Migration cần chạy TAY 1 lần trên Supabase/PostgreSQL sau khi deploy code mới.
-- (Dự án hiện không dùng Flyway/Liquibase, Hibernate ddl-auto không tự xoá được
--  ràng buộc UNIQUE cũ, nên phải chạy thủ công.)

-- 1) Bỏ ràng buộc UNIQUE trên candidates.email — 1 tài khoản giờ có thể có
--    nhiều hồ sơ ứng tuyển (nhiều lần upload CV) với cùng 1 email.
--    Tên constraint có thể khác tuỳ Postgres tự đặt, kiểm tra lại bằng:
--    SELECT conname FROM pg_constraint WHERE conrelid = 'candidates'::regclass;
ALTER TABLE candidates DROP CONSTRAINT IF EXISTS candidates_email_key;

-- 2) Thêm cột account_id để biết hồ sơ ứng tuyển này thuộc tài khoản nào
ALTER TABLE candidates ADD COLUMN IF NOT EXISTS account_id BIGINT;
ALTER TABLE candidates ADD CONSTRAINT fk_candidates_account
    FOREIGN KEY (account_id) REFERENCES accounts(id);

-- 3) Với dữ liệu cũ đã có sẵn (trước khi có account_id), gán account_id theo email
--    trùng khớp với accounts.email, để các hồ sơ cũ vẫn hiện lên dashboard.
UPDATE candidates c
SET account_id = a.id
FROM accounts a
WHERE c.account_id IS NULL AND lower(c.email) = lower(a.email);

-- 4) Bảng mới lưu kết quả match đã tính (thay vì cào lại TopCV mỗi lần xem trang)
CREATE TABLE IF NOT EXISTS application_matches (
    id BIGSERIAL PRIMARY KEY,
    candidate_id BIGINT NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    job_title VARCHAR(255),
    company_name VARCHAR(255),
    job_url VARCHAR(1000),
    score REAL NOT NULL,
    source VARCHAR(20),
    created_at TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_application_matches_candidate_id
    ON application_matches (candidate_id);

-- 5) Thêm cột lưu thời điểm cấp token, để token có thể tự hết hạn (24h) thay vì
--    tồn tại vĩnh viễn như trước. Tài khoản cũ (giá trị NULL) vẫn đăng nhập lại
--    bình thường và sẽ có token_issued_at kể từ lần đăng nhập tiếp theo.
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS token_issued_at TIMESTAMP;
