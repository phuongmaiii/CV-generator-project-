package com.cvrecruitment.cv_recruitment_service.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * Kết quả match đã được TÍNH VÀ LƯU LẠI cho một hồ sơ ứng tuyển (Candidate = 1 lần upload CV).
 *
 * Trước đây MatchScoreController#getMatchesForCandidate cào TopCV lại "real-time" mỗi lần
 * người dùng mở trang xem kết quả, nên kết quả có thể khác nhau giữa 2 lần xem cùng 1 hồ sơ.
 * Giờ đây việc cào + tính điểm chỉ chạy 1 lần (lúc upload, hoặc khi bấm "Làm mới"), và được
 * lưu vào bảng này để trang dashboard / trang xem chi tiết chỉ cần đọc lại, không cào lại.
 */
@Entity
@Table(name = "application_matches")
public class ApplicationMatch {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Trỏ tới candidates.id (tức 1 hồ sơ ứng tuyển / 1 lần upload CV cụ thể)
    @Column(name = "candidate_id", nullable = false)
    private Long candidateId;

    @Column(name = "job_title")
    private String jobTitle;

    @Column(name = "company_name")
    private String companyName;

    @Column(name = "job_url", length = 1000)
    private String jobUrl;

    @Column(nullable = false)
    private Float score;

    // "TOPCV" nếu cào được job thật, "DEMO" nếu là dữ liệu fallback giả lập khi cào lỗi.
    // Frontend dựa vào đây để cảnh báo người dùng biết đây là dữ liệu minh hoạ, không phải job thật.
    @Column(length = 20)
    private String source;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public Long getCandidateId() { return candidateId; }
    public void setCandidateId(Long candidateId) { this.candidateId = candidateId; }

    public String getJobTitle() { return jobTitle; }
    public void setJobTitle(String jobTitle) { this.jobTitle = jobTitle; }

    public String getCompanyName() { return companyName; }
    public void setCompanyName(String companyName) { this.companyName = companyName; }

    public String getJobUrl() { return jobUrl; }
    public void setJobUrl(String jobUrl) { this.jobUrl = jobUrl; }

    public Float getScore() { return score; }
    public void setScore(Float score) { this.score = score; }

    public String getSource() { return source; }
    public void setSource(String source) { this.source = source; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
}
