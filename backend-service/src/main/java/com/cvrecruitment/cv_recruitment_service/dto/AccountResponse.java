package com.cvrecruitment.cv_recruitment_service.dto;

import com.cvrecruitment.cv_recruitment_service.entity.Account;

/** Safe representation for account data returned to clients. */
public record AccountResponse(Long id, String email, String role, String fullName, String companyName) {
    public static AccountResponse from(Account account) {
        return new AccountResponse(account.getId(), account.getEmail(), account.getRole(),
                account.getFullName(), account.getCompanyName());
    }
}
