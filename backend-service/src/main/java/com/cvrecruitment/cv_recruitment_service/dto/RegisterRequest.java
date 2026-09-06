package com.cvrecruitment.cv_recruitment_service.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class RegisterRequest {
    @NotBlank @Email
    private String email;
    @NotBlank (message = "Password is required") 
    @Size(min = 6, max = 50, message = "Password must be between 6 and 50 characters")
    private String password;
    @NotBlank @Size(max = 100)
    private String fullName;
    @NotBlank
    private String role;
    private String companyName;

    // Getters
    public String getEmail() { return email; }
    public String getPassword() { return password; }
    public String getFullName() { return fullName; }
    public String getRole() { return role; }
    public String getCompanyName() { return companyName; }

    // Setters
    public void setEmail(String email) { this.email = email; }
    public void setPassword(String password) { this.password = password; }
    public void setFullName(String fullName) { this.fullName = fullName; }
    public void setRole(String role) { this.role = role; }
    public void setCompanyName(String companyName) { this.companyName = companyName; }
}
