package com.cvrecruitment.cv_recruitment_service.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;

@Entity
@Table(name = "accounts")
public class Account {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String email;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false)
    private String role; // "CANDIDATE" hoặc "HR"

    @Column(name = "full_name")
    private String fullName;

    @Column(name = "company_name")
    private String companyName;

    @Column(unique = true)
    private String token; // Lưu UUID token khi đăng nhập

    // BUG CŨ: token trước đây không có hạn sử dụng — 1 lần đăng nhập là token tồn tại
    // vĩnh viễn cho tới lần đăng nhập kế tiếp (ghi đè). Nếu token bị lộ (log, lịch sử
    // trình duyệt, máy dùng chung...), kẻ tấn công có thể dùng vô thời hạn. Thêm cột
    // này để verifyToken() có thể từ chối token đã quá hạn (xem AccountRepository).
    @Column(name = "token_issued_at")
    private java.time.LocalDateTime tokenIssuedAt;

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    @JsonIgnore
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
    public String getRole() { return role; }
    public void setRole(String role) { this.role = role; }
    public String getFullName() { return fullName; }
    public void setFullName(String fullName) { this.fullName = fullName; }
    public String getCompanyName() { return companyName; }
    public void setCompanyName(String companyName) { this.companyName = companyName; }
    @JsonIgnore
    public String getToken() { return token; }
    public void setToken(String token) { this.token = token; }
    public java.time.LocalDateTime getTokenIssuedAt() { return tokenIssuedAt; }
    public void setTokenIssuedAt(java.time.LocalDateTime tokenIssuedAt) { this.tokenIssuedAt = tokenIssuedAt; }
}
