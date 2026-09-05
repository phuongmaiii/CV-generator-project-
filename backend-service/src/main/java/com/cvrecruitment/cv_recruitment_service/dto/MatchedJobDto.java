package com.cvrecruitment.cv_recruitment_service.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class MatchedJobDto {

    // Ép Spring Boot lấy đúng trường "job_id" (hoặc "jobId") từ JSON Python
    @JsonProperty("job_id") 
    private Long jobId;

    // Ép Spring Boot lấy đúng trường "score" từ JSON Python, thay vì tìm chữ "matchScore"
    @JsonProperty("score")  
    private Double matchScore;

    public Long getJobId() {
        return jobId;
    }

    public void setJobId(Long jobId) {
        this.jobId = jobId;
    }

    public Double getMatchScore() {
        return matchScore;
    }

    public void setMatchScore(Double matchScore) {
        this.matchScore = matchScore;
    }
}