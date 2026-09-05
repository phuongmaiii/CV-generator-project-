package com.cvrecruitment.cv_recruitment_service.controller;

import com.cvrecruitment.cv_recruitment_service.JobSeederService;   // sửa dòng này
import com.cvrecruitment.cv_recruitment_service.AuthUtil;
import com.cvrecruitment.cv_recruitment_service.entity.Account;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/admin")
public class SeederController {

    private final JobSeederService jobSeederService;
    private final AuthUtil authUtil;

    public SeederController(JobSeederService jobSeederService, AuthUtil authUtil) {
        this.jobSeederService = jobSeederService;
        this.authUtil = authUtil;
    }

    @PostMapping("/seed-jobs")
    public ResponseEntity<String> seedJobs(@RequestHeader(value = "Authorization", required = false) String authHeader) {
        Account account = authUtil.verifyToken(authHeader);
        if (account == null || !"ADMIN".equalsIgnoreCase(account.getRole())) {
            return ResponseEntity.status(403).body("Từ chối truy cập");
        }
        jobSeederService.seedJobsFromApi();
        return ResponseEntity.ok("Da kich hoat seed job. Kiem tra log de xem ket qua.");
    }
}
