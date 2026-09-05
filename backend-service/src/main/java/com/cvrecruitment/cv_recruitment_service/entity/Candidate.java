package com.cvrecruitment.cv_recruitment_service.entity;

import java.time.LocalDateTime;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "candidates")
public class Candidate {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "full_name", nullable = false)
    private String fullName;

    // Không còn unique: 1 tài khoản/email có thể tạo NHIỀU hồ sơ ứng tuyển
    // (mỗi lần upload CV = 1 "application" riêng, ứng với 1 vị trí khác nhau).
    @Column(nullable = false, length = 255)
    private String email;

    // Liên kết tới accounts.id của người dùng đã đăng nhập (nếu có token hợp lệ khi upload).
    // Dùng để lọc "các vị trí đã ứng tuyển" của đúng ứng viên đang đăng nhập,
    // thay vì chỉ dựa vào email (email không còn là khoá duy nhất nữa).
    @Column(name = "account_id")
    private Long accountId;

    @Column(length = 50)
    private String phone;

    @Column(columnDefinition = "TEXT")
    private String skills;

    @Column(name = "resume_url", length = 500)
    private String resumeUrl;

    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    @Column(length = 100)
    private String industry;

    @Column(length = 100)
    private String position;

    @Column(name = "cv_text", columnDefinition = "TEXT")
    private String cvText;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getFullName() {
        return fullName;
    }

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public Long getAccountId() {
        return accountId;
    }

    public void setAccountId(Long accountId) {
        this.accountId = accountId;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getSkills() {
        return skills;
    }

    public void setSkills(String skills) {
        this.skills = skills;
    }

    public String getResumeUrl() {
        return resumeUrl;
    }

    public void setResumeUrl(String resumeUrl) {
        this.resumeUrl = resumeUrl;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public String getIndustry() {
        return industry;
    }

    public void setIndustry(String industry) {
        this.industry = industry;
    }

    public String getPosition() {
        return position;
    }

    public void setPosition(String position) {
        this.position = position;
    }

    @JsonIgnore
    public String getCvText() {
        return cvText;
    }

    public void setCvText(String cvText) {
        this.cvText = cvText;
    }
}
