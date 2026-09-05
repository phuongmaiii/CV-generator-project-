package com.cvrecruitment.cv_recruitment_service.controller;

import java.util.List;
import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.cvrecruitment.cv_recruitment_service.AccountRepository;
import com.cvrecruitment.cv_recruitment_service.AuthUtil;
import com.cvrecruitment.cv_recruitment_service.JobSeederService;
import com.cvrecruitment.cv_recruitment_service.MatchingService;
import com.cvrecruitment.cv_recruitment_service.entity.Account;
import com.cvrecruitment.cv_recruitment_service.entity.JobPosting;
import com.cvrecruitment.cv_recruitment_service.repository.JobPostingRepository;

@RestController
@RequestMapping("/api/jobs") 
@CrossOrigin(origins = {
    "http://localhost:5173", 
    "http://localhost:5174", 
    "https://cv-generator-project-umber.vercel.app"
}, allowCredentials = "true")
public class JobPostingController {

    private final JobPostingRepository repository;
    private final MatchingService matchingService;
    private final JobSeederService jobSeederService;
    private final AccountRepository accountRepository;
    private final AuthUtil authUtil;

    public JobPostingController(JobPostingRepository repository, MatchingService matchingService, JobSeederService jobSeederService, AccountRepository accountRepository, AuthUtil authUtil) {
        this.repository = repository;
        this.matchingService = matchingService; 
        this.jobSeederService = jobSeederService;
        this.accountRepository = accountRepository;
        this.authUtil = authUtil;
    }

    // Xác thực tài khoản qua Token Header — dùng chung AuthUtil (có kiểm tra hạn
    // token, xem AuthUtil.java) thay vì logic riêng bị lặp lại ở mỗi controller.
    private Account verifyToken(String authHeader) {
        return authUtil.verifyToken(authHeader);
    }

    @GetMapping
    public List<JobPosting> getAll() {
        return repository.findAll();
    }

    @GetMapping("/{id}")
    public JobPosting getById(@PathVariable Long id) {
        return repository.findById(id).orElseThrow();
    }

    @PostMapping
    public ResponseEntity<?> create(@RequestBody JobPosting job, @RequestHeader(value = "Authorization", required = false) String authHeader) {
        Account hr = verifyToken(authHeader);
        if (hr == null || !"HR".equalsIgnoreCase(hr.getRole())) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Không có quyền tạo công việc");
        }
        
        job.setPostedBy(hr.getId());
        job.setCompanyName(hr.getCompanyName());
        if (job.getStatus() == null) {
            job.setStatus("OPEN");
        }
        return ResponseEntity.ok(repository.save(job));
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> updateJob(@PathVariable Long id, @RequestBody JobPosting jobDetails, @RequestHeader(value = "Authorization", required = false) String authHeader) {
        Account hr = verifyToken(authHeader);
        if (hr == null || !"HR".equalsIgnoreCase(hr.getRole())) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Phiên đăng nhập không hợp lệ.");
        }

        JobPosting existingJob = repository.findById(id)
                .orElseThrow(() -> new RuntimeException("Không tìm thấy công việc"));
        
        if (!canManageJob(hr, existingJob)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body("Từ chối truy cập!");
        }
        
        existingJob.setTitle(jobDetails.getTitle());
        existingJob.setStatus(jobDetails.getStatus() != null ? jobDetails.getStatus() : "OPEN");
        
        if (jobDetails.getLocation() != null) {
            existingJob.setLocation(jobDetails.getLocation());
        }
        if (jobDetails.getDeadline() != null) {
            existingJob.setDeadline(jobDetails.getDeadline());
        }
        if (jobDetails.getDescription() != null) {
            existingJob.setDescription(jobDetails.getDescription());
        }
        if (jobDetails.getRequirements() != null) {
            existingJob.setRequirements(jobDetails.getRequirements());
        }

        return ResponseEntity.ok(repository.save(existingJob));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteJob(@PathVariable Long id, @RequestHeader(value = "Authorization", required = false) String authHeader) {
        Account hr = verifyToken(authHeader);
        if (hr == null || !"HR".equalsIgnoreCase(hr.getRole())) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Phiên đăng nhập không hợp lệ.");
        }

        JobPosting existingJob = repository.findById(id)
                .orElseThrow(() -> new RuntimeException("Không tìm thấy công việc"));

        // CHỐT CHẶN BẢO MẬT MỚI: Chỉ cần cùng công ty là được phép xóa
        if (!canManageJob(hr, existingJob)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body("Từ chối truy cập!");
        }

        repository.deleteById(id);
        return ResponseEntity.ok(Map.of("message", "Đã xóa công việc thành công!"));
    }

    // (Giữ lại API cũ đề phòng sau này cần dùng)
    @GetMapping("/hr/{hrId}/my-jobs")
    public ResponseEntity<?> getMyJobs(@PathVariable Long hrId,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {
        Account hr = verifyToken(authHeader);
        if (hr == null || !"HR".equalsIgnoreCase(hr.getRole()) || !hr.getId().equals(hrId)) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body("Từ chối truy cập!");
        }
        List<JobPosting> myJobs = repository.findByPostedByOrderByCreatedAtDesc(hrId);
        return ResponseEntity.ok(myJobs);
    }

    private boolean canManageJob(Account hr, JobPosting job) {
        if (hr.getId().equals(job.getPostedBy())) return true;
        return hr.getCompanyName() != null && job.getCompanyName() != null
                && hr.getCompanyName().trim().equalsIgnoreCase(job.getCompanyName().trim());
    }

    // API MỚI: Lấy danh sách Job theo tên công ty (cho Dashboard HR)
    @GetMapping("/hr/my-company-jobs")
    public ResponseEntity<?> getCompanyJobs(@RequestHeader(value = "Authorization", required = false) String authHeader) {
        Account hr = verifyToken(authHeader);
        if (hr == null || !"HR".equalsIgnoreCase(hr.getRole()) || hr.getCompanyName() == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Phiên đăng nhập không hợp lệ.");
        }
        
        // Lấy toàn bộ Job của công ty (Bao gồm Job tự tạo và Job do Python cào về)
        List<JobPosting> companyJobs = repository.findByCompanyNameContainingIgnoreCaseOrderByIdDesc(hr.getCompanyName());
return ResponseEntity.ok(companyJobs);
    }
}
