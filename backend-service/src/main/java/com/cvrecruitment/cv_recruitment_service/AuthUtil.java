package com.cvrecruitment.cv_recruitment_service;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;

import org.springframework.stereotype.Component;

import com.cvrecruitment.cv_recruitment_service.entity.Account;

/**
 * BUG CŨ: verifyToken() bị copy-paste giống hệt nhau ở CandidateController và
 * JobPostingController (vi phạm DRY — thêm 1 route mới rất dễ quên copy đúng logic
 * xác thực, hoặc quên cập nhật cả 2 nơi khi sửa). Đồng thời token trước đây KHÔNG
 * có hạn sử dụng — tồn tại vĩnh viễn cho tới lần đăng nhập kế tiếp.
 *
 * Class này gom logic xác thực về 1 chỗ duy nhất và thêm kiểm tra hạn token
 * (mặc định 24h kể từ lúc đăng nhập). Đây chưa phải giải pháp lý tưởng (Spring
 * Security với 1 filter tập trung sẽ chuẩn hơn), nhưng là bước cải thiện thực tế
 * trong phạm vi thời gian của capstone, không phá vỡ cấu trúc controller hiện có.
 */
@Component
public class AuthUtil {

    private static final long TOKEN_TTL_HOURS = 24;

    private final AccountRepository accountRepository;

    public AuthUtil(AccountRepository accountRepository) {
        this.accountRepository = accountRepository;
    }

    /**
     * Trả về Account nếu token hợp lệ VÀ chưa hết hạn, ngược lại trả về null.
     */
    public Account verifyToken(String authHeader) {
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            return null;
        }
        String token = authHeader.substring(7);

        return accountRepository.findByToken(token)
                .filter(this::isTokenStillValid)
                .orElse(null);
    }

    private boolean isTokenStillValid(Account account) {
        // Tài khoản cũ (đăng nhập trước khi có tính năng này) sẽ không có
        // tokenIssuedAt — coi như hợp lệ 1 lần cuối, token mới sau đó sẽ luôn có hạn.
        if (account.getTokenIssuedAt() == null) {
            return true;
        }
        long hoursSinceIssued = ChronoUnit.HOURS.between(account.getTokenIssuedAt(), LocalDateTime.now());
        return hoursSinceIssued < TOKEN_TTL_HOURS;
    }
}
