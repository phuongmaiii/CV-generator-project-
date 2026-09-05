package com.cvrecruitment.cv_recruitment_service.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.cvrecruitment.cv_recruitment_service.entity.Candidate;

@Repository
public interface CandidateRepository extends JpaRepository<Candidate, Long> {
    // Giữ lại cho các chỗ cũ còn dùng (vd tra cứu nhanh theo email); từ nay email KHÔNG unique
    // nữa nên hàm này chỉ trả về 1 kết quả bất kỳ khớp email, không đại diện "toàn bộ hồ sơ".
    Optional<Candidate> findByEmail(String email);

    // Danh sách TẤT CẢ hồ sơ ứng tuyển (mỗi lần upload CV) của 1 tài khoản, mới nhất trước
    // -> dùng cho trang Dashboard "các vị trí đã ứng tuyển"
    List<Candidate> findByAccountIdOrderByCreatedAtDesc(Long accountId);
}