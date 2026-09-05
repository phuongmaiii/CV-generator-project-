package com.cvrecruitment.cv_recruitment_service.controller;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import com.cvrecruitment.cv_recruitment_service.AuthUtil;
import com.cvrecruitment.cv_recruitment_service.MatchingService;
import com.cvrecruitment.cv_recruitment_service.dto.CandidateApplicationDto;
import com.cvrecruitment.cv_recruitment_service.entity.Account;
import com.cvrecruitment.cv_recruitment_service.entity.Candidate; 
import com.cvrecruitment.cv_recruitment_service.repository.ApplicationMatchRepository;
import com.cvrecruitment.cv_recruitment_service.repository.CandidateRepository;
import com.cvrecruitment.cv_recruitment_service.repository.JobPostingRepository;
import com.cvrecruitment.cv_recruitment_service.service.AiMatchingService; 

@RestController
@RequestMapping("/api/candidates")
@CrossOrigin(origins = "https://cv-generator-project-umber.vercel.app", allowCredentials = "true")
public class CandidateController {

    private static final Logger log = LoggerFactory.getLogger(CandidateController.class);
    
    private final CandidateRepository repository;
    private final MatchingService matchingService;
    private final RestTemplate restTemplate;
    private final AiMatchingService aiMatchingService;
    private final ApplicationMatchRepository applicationMatchRepository;
    private final JobPostingRepository jobPostingRepository;
    private final AuthUtil authUtil;

    @Value("${fastapi.service.base-url}")
    private String fastApiBaseUrl;

    public CandidateController(CandidateRepository repository, 
                               MatchingService matchingService, 
                               RestTemplate restTemplate,
                               AiMatchingService aiMatchingService,
                               ApplicationMatchRepository applicationMatchRepository,
                               JobPostingRepository jobPostingRepository,
                               AuthUtil authUtil) {
        this.repository = repository;
        this.matchingService = matchingService;
        this.restTemplate = restTemplate;
        this.aiMatchingService = aiMatchingService;
        this.applicationMatchRepository = applicationMatchRepository;
        this.jobPostingRepository = jobPostingRepository;
        this.authUtil = authUtil;
    }

    // Xác thực tài khoản qua Token Header — dùng chung AuthUtil (có kiểm tra hạn
    // token) thay vì tự viết verifyToken() riêng như trước, để tránh trùng lặp logic
    // với JobPostingController và dễ sửa 1 chỗ khi cần thay đổi cách xác thực.
    private Account verifyToken(String authHeader) {
        return authUtil.verifyToken(authHeader);
    }

    // ----------------------------------------------------
    // HÀM 1: TẢI CV LÊN VÀ PHÂN TÍCH (LƯU DATABASE)
    // ----------------------------------------------------
    @PostMapping("/upload-cv")
    public ResponseEntity<?> uploadCv(
            @RequestParam("file") MultipartFile file,
            @RequestParam("fullName") String fullName,
            @RequestParam("email") String email,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        if (file.isEmpty()) {
            log.warn("Upload CV that bai: file rong, email={}", email);
            return ResponseEntity.badRequest().body(Map.of("error", "File rỗng, vui lòng chọn file CV"));
        }
        String filename = file.getOriginalFilename();
        if (filename == null || !filename.toLowerCase().endsWith(".pdf")) {
            return ResponseEntity.badRequest().body(Map.of("error", "Chỉ chấp nhận file PDF"));
        }

        Account account = verifyToken(authHeader);
        if (account == null || !"CANDIDATE".equalsIgnoreCase(account.getRole())) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Bạn phải đăng nhập bằng tài khoản ứng viên"));
        }

        try {
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", new ByteArrayResource(file.getBytes()) {
                @Override
                public String getFilename() { return file.getOriginalFilename(); }
            });

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);
            HttpEntity<MultiValueMap<String, Object>> request = new HttpEntity<>(body, headers);

            ResponseEntity<Map> response = restTemplate.postForEntity(
                    fastApiBaseUrl + "/parse-cv", request, Map.class);
            @SuppressWarnings("unchecked")
            Map<String, Object> parsed = response.getBody();
            if (parsed == null) {
                throw new IllegalStateException("FastAPI tra ve body rong");
            }

            // BUG CŨ: trước đây dòng dưới tìm candidate theo email và GHI ĐÈ lên hồ sơ cũ
            // nếu email đã tồn tại (repository.findByEmail(email).orElse(new Candidate())).
            // Hệ quả là 1 người chỉ có thể có DUY NHẤT 1 hồ sơ ứng tuyển tại 1 thời điểm —
            // upload CV lần 2 (cho vị trí khác) sẽ XOÁ MẤT dữ liệu + kết quả match của lần 1.
            // Sửa: mỗi lần upload luôn tạo 1 hồ sơ (application) MỚI, để 1 ứng viên có thể
            // ứng tuyển nhiều vị trí cùng lúc và xem lại từng vị trí trên dashboard.
            Candidate candidate = new Candidate();

            candidate.setAccountId(account.getId());
            // Do not trust identity fields supplied by the browser.
            candidate.setFullName(account.getFullName());
            candidate.setEmail(account.getEmail());
            candidate.setIndustry((String) parsed.get("industry"));
            candidate.setPosition((String) parsed.get("position"));
            candidate.setCvText((String) parsed.get("text"));

            Candidate saved = repository.save(candidate); 
            matchingService.autoMatchForNewCandidate(saved);

            return ResponseEntity.status(HttpStatus.CREATED).body(saved);

        } catch (ResourceAccessException e) {
            log.error("Goi FastAPI that bai (timeout/khong ket noi): {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.GATEWAY_TIMEOUT)
                    .body(Map.of("error", "Khong ket noi duoc dich vu AI, vui long thu lai sau"));

        } catch (HttpClientErrorException | HttpServerErrorException e) {
            log.error("FastAPI tra loi {}: {}", e.getStatusCode(), e.getResponseBodyAsString());
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                    .body(Map.of("error", "Loi tu dich vu AI: " + e.getResponseBodyAsString()));

        } catch (IOException e) {
            log.error("Loi doc file upload: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Khong doc duoc file da upload"));

        } catch (Exception e) {
            log.error("Loi khong xac dinh khi xu ly upload CV: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Da xay ra loi khi xu ly CV"));
        }
    }

    // ----------------------------------------------------
    // HÀM MỚI: DANH SÁCH CÁC VỊ TRÍ ĐÃ ỨNG TUYỂN (DASHBOARD ỨNG VIÊN)
    // ----------------------------------------------------
    // Mỗi bản ghi Candidate giờ là 1 lần upload CV = 1 vị trí đã ứng tuyển.
    // Trả về kèm điểm match cao nhất đã lưu được, để dashboard hiển thị ngay
    // mà không cần mở từng trang chi tiết.
    @GetMapping("/my-applications")
    public ResponseEntity<?> getMyApplications(
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        Account account = verifyToken(authHeader);
        if (account == null || !"CANDIDATE".equalsIgnoreCase(account.getRole())) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("error", "Bạn phải đăng nhập bằng tài khoản ứng viên"));
        }

        List<Candidate> applications = repository.findByAccountIdOrderByCreatedAtDesc(account.getId());
        List<CandidateApplicationDto> result = new java.util.ArrayList<>();

        for (Candidate c : applications) {
            CandidateApplicationDto dto = new CandidateApplicationDto();
            dto.setId(c.getId());
            dto.setPosition(c.getPosition());
            dto.setIndustry(c.getIndustry());
            dto.setCreatedAt(c.getCreatedAt());

            var matches = applicationMatchRepository.findByCandidateIdOrderByScoreDesc(c.getId());
            dto.setMatchCount(matches.size());
            dto.setTopScore(matches.isEmpty() ? null : matches.get(0).getScore());

            result.add(dto);
        }

        return ResponseEntity.ok(result);
    }

    // ----------------------------------------------------
    // HÀM 2: LẤY CHI TIẾT ỨNG VIÊN BẰNG ID
    // ----------------------------------------------------
    @GetMapping("/{id}")
    public ResponseEntity<?> getCandidateById(
            @PathVariable Long id,
            @RequestParam(required = false) Long jobPostingId,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {
        Optional<Candidate> candidateOpt = repository.findById(id);
        
        if (candidateOpt.isEmpty()) {
            log.warn("Khong tim thay ung vien voi ID = {}", id);
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("error", "Không tìm thấy ứng viên với ID = " + id));
        }

        Account account = verifyToken(authHeader);
        Candidate candidate = candidateOpt.get();
        boolean ownsCandidate = account != null && "CANDIDATE".equalsIgnoreCase(account.getRole())
                && account.getId().equals(candidate.getAccountId());
        boolean ownsJob = account != null && "HR".equalsIgnoreCase(account.getRole()) && jobPostingId != null
                && jobPostingRepository.findById(jobPostingId)
                    .map(job -> account.getId().equals(job.getPostedBy())
                        || (account.getCompanyName() != null && job.getCompanyName() != null
                            && account.getCompanyName().trim().equalsIgnoreCase(job.getCompanyName().trim())))
                    .orElse(false);
        if (!ownsCandidate && !ownsJob) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Bạn không có quyền xem hồ sơ này"));
        }

        return ResponseEntity.ok(Map.of(
                "id", candidate.getId(), "fullName", candidate.getFullName(),
                "email", candidate.getEmail(), "industry", candidate.getIndustry() == null ? "" : candidate.getIndustry(),
                "position", candidate.getPosition() == null ? "" : candidate.getPosition(),
                "cvText", candidate.getCvText() == null ? "" : candidate.getCvText()));
    }

    // ----------------------------------------------------
    // HÀM 3: SO KHỚP NHANH CV VÀ YÊU CẦU CÔNG VIỆC (HR)
    // ----------------------------------------------------
    @PostMapping("/match-jd")
    public ResponseEntity<?> matchCvWithJd(
            @RequestParam("cv_file") MultipartFile cvFile,
            @RequestParam("jd_text") String jdText,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {
        
        if (cvFile.isEmpty() || jdText == null || jdText.trim().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Vui lòng cung cấp đủ file CV và JD"));
        }
        Account account = verifyToken(authHeader);
        if (account == null || !"HR".equalsIgnoreCase(account.getRole())) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("error", "Chỉ HR được phép so khớp CV"));
        }

        try {
            Double matchScore = aiMatchingService.calculateMatchScore(cvFile, jdText);

            return ResponseEntity.ok(Map.of(
                "status", "success",
                "filename", cvFile.getOriginalFilename(),
                "match_score", matchScore
            ));

        } catch (Exception e) {
            log.error("Lỗi khi tính điểm AI: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Lỗi xử lý AI Engine: " + e.getMessage()));
        }
    }
}
