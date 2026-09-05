package com.cvrecruitment.cv_recruitment_service.dto;

import java.time.LocalDateTime;

/**
 * 1 dòng trên dashboard "Các vị trí đã ứng tuyển" của ứng viên.
 * Ứng với 1 lần upload CV (1 bản ghi Candidate).
 */
public class CandidateApplicationDto {
    private Long id;
    private String position;
    private String industry;
    private LocalDateTime createdAt;
    private Float topScore;   // điểm match cao nhất đã lưu, null nếu chưa có kết quả nào
    private int matchCount;   // số job được đề xuất cho hồ sơ này

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getPosition() { return position; }
    public void setPosition(String position) { this.position = position; }

    public String getIndustry() { return industry; }
    public void setIndustry(String industry) { this.industry = industry; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public Float getTopScore() { return topScore; }
    public void setTopScore(Float topScore) { this.topScore = topScore; }

    public int getMatchCount() { return matchCount; }
    public void setMatchCount(int matchCount) { this.matchCount = matchCount; }
}
