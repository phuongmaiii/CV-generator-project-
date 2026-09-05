package com.cvrecruitment.cv_recruitment_service.controller;

import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.server.ResponseStatusException;

import com.cvrecruitment.cv_recruitment_service.MatchingService;
import com.cvrecruitment.cv_recruitment_service.AuthUtil;
import com.cvrecruitment.cv_recruitment_service.dto.MatchResultDto;
import com.cvrecruitment.cv_recruitment_service.entity.ApplicationMatch;
import com.cvrecruitment.cv_recruitment_service.entity.Account;
import com.cvrecruitment.cv_recruitment_service.entity.Candidate;
import com.cvrecruitment.cv_recruitment_service.entity.JobPosting;
import com.cvrecruitment.cv_recruitment_service.entity.MatchScore;
import com.cvrecruitment.cv_recruitment_service.repository.ApplicationMatchRepository;
import com.cvrecruitment.cv_recruitment_service.repository.CandidateRepository;
import com.cvrecruitment.cv_recruitment_service.repository.JobPostingRepository;
import com.cvrecruitment.cv_recruitment_service.repository.MatchScoreRepository;

@RestController
@RequestMapping("/api/match")
public class MatchScoreController {

    private static final Logger logger = LoggerFactory.getLogger(MatchScoreController.class);

    private final MatchScoreRepository matchRepository;
    private final CandidateRepository candidateRepository;
    private final JobPostingRepository jobPostingRepository;
    private final ApplicationMatchRepository applicationMatchRepository;
    private final MatchingService matchingService;
    private final RestTemplate restTemplate;
    private final AuthUtil authUtil;

    @Value("${fastapi.service.base-url}")
    private String fastApiBaseUrl;

    public MatchScoreController(MatchScoreRepository matchRepository, 
                                CandidateRepository candidateRepository, 
                                JobPostingRepository jobPostingRepository, 
                                 ApplicationMatchRepository applicationMatchRepository,
                                 MatchingService matchingService,
                                 RestTemplate restTemplate,
                                 AuthUtil authUtil) {
        this.matchRepository = matchRepository;
        this.candidateRepository = candidateRepository;
        this.jobPostingRepository = jobPostingRepository;
        this.applicationMatchRepository = applicationMatchRepository;
        this.matchingService = matchingService;
        this.restTemplate = restTemplate;
        this.authUtil = authUtil;
    }

    private Account requireAccount(String authHeader) {
        Account account = authUtil.verifyToken(authHeader);
        if (account == null) throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Phiên đăng nhập không hợp lệ");
        return account;
    }

    private void requireCandidateOwner(Account account, Candidate candidate) {
        if (!"CANDIDATE".equalsIgnoreCase(account.getRole()) || !account.getId().equals(candidate.getAccountId())) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Bạn không có quyền truy cập hồ sơ này");
        }
    }

    private void requireHrOwner(Account account, JobPosting job) {
        boolean ownsJob = account.getId().equals(job.getPostedBy());
        // Existing seeded records may have an obsolete postedBy.  A same-company HR
        // can still use those records, but substring matching is intentionally avoided.
        boolean sameCompany = account.getCompanyName() != null && job.getCompanyName() != null
                && account.getCompanyName().trim().equalsIgnoreCase(job.getCompanyName().trim());
        if (!"HR".equalsIgnoreCase(account.getRole()) || (!ownsJob && !sameCompany)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Bạn không có quyền truy cập tin tuyển dụng này");
        }
    }

    @PostMapping("/{candidateId}/{jobPostingId}")
    public ResponseEntity<?> computeMatch(@PathVariable Long candidateId, @PathVariable Long jobPostingId,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {
        Candidate candidate = candidateRepository.findById(candidateId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Khong tim thay candidate id=" + candidateId));
        
        JobPosting job = jobPostingRepository.findById(jobPostingId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Khong tim thay job posting id=" + jobPostingId));

        Account account = requireAccount(authHeader);
        if ("CANDIDATE".equalsIgnoreCase(account.getRole())) {
            requireCandidateOwner(account, candidate);
        } else {
            requireHrOwner(account, job);
        }

        if (candidate.getCvText() == null || candidate.getCvText().isBlank()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Candidate chua co cv_text, vui long upload lai CV"));
        }

        String jobText = buildJobText(job);
        Map<String, String> body = Map.of(
                "cv_text", candidate.getCvText(),
                "job_description", jobText
        );

        ResponseEntity<Map> response = restTemplate.postForEntity(
                fastApiBaseUrl + "/match-score", body, Map.class);

        Number matchScoreObj = (Number) response.getBody().get("match_percent");
        if (matchScoreObj == null) matchScoreObj = (Number) response.getBody().get("match_score");
        Float matchScore = matchScoreObj != null ? matchScoreObj.floatValue() : 0f;
        if (matchScore <= 1f) matchScore *= 100f;

        MatchScore entity = new MatchScore();
        entity.setCandidateId(candidateId);
        entity.setJobPostingId(jobPostingId);
        entity.setScore(matchScore);

        return ResponseEntity.ok(matchRepository.save(entity));
    }

    @GetMapping("/job/{jobPostingId}")
    public List<MatchScore> getMatchesForJob(@PathVariable Long jobPostingId,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {
        JobPosting job = jobPostingRepository.findById(jobPostingId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Không tìm thấy tin tuyển dụng"));
        requireHrOwner(requireAccount(authHeader), job);
        return matchRepository.findByJobPostingId(jobPostingId);
    }
    
    // Trước đây endpoint này CÀO LẠI TopCV real-time mỗi lần người dùng mở trang xem
    // kết quả (khác với lần cào lúc upload), nên 2 lần xem cùng 1 hồ sơ có thể ra kết
    // quả khác nhau. Giờ đây chỉ ĐỌC LẠI kết quả đã được lưu (từ lúc upload, hoặc từ
    // lần bấm "Làm mới" gần nhất) — xem thêm MatchingService#refreshTopCvMatches.
    // Nếu hồ sơ chưa có kết quả nào được lưu (vd. bước tự động match lúc upload bị lỗi),
    // tự động cào + lưu 1 lần cho lần xem đầu tiên này để trang không bị trống trơn.
    @GetMapping("/candidate/{candidateId}")
    public Page<MatchResultDto> getMatchesForCandidate(
            @PathVariable Long candidateId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {

        Candidate candidate = candidateRepository.findById(candidateId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Không tìm thấy ứng viên"));
        requireCandidateOwner(requireAccount(authHeader), candidate);

        List<ApplicationMatch> saved = applicationMatchRepository.findByCandidateIdOrderByScoreDesc(candidateId);
        if (saved.isEmpty()) {
            saved = matchingService.refreshTopCvMatches(candidate);
        }

        List<MatchResultDto> resultList = new java.util.ArrayList<>();
        for (ApplicationMatch match : saved) {
            MatchResultDto dto = new MatchResultDto();
            dto.setMatchId(match.getId());
            dto.setCandidateId(candidateId);
            dto.setCandidateName(candidate.getFullName());
            dto.setJobTitle(match.getJobTitle());
            dto.setCompanyName(match.getCompanyName());
            dto.setJobUrl(match.getJobUrl());
            dto.setScore(match.getScore());
            dto.setCreatedAt(match.getCreatedAt());
            dto.setSource(match.getSource());
            resultList.add(dto);
        }

        return new org.springframework.data.domain.PageImpl<>(resultList);
    }

    // Nút "Làm mới" ở trang xem kết quả / dashboard: cào lại TopCV theo yêu cầu thay vì
    // tự động cào lại mỗi lần mở trang (điều gây ra sự không nhất quán trước đây).
    @PostMapping("/candidate/{candidateId}/refresh")
    public Page<MatchResultDto> refreshMatchesForCandidate(@PathVariable Long candidateId,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {
        Candidate candidate = candidateRepository.findById(candidateId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Không tìm thấy ứng viên"));
        requireCandidateOwner(requireAccount(authHeader), candidate);

        List<ApplicationMatch> saved = matchingService.refreshTopCvMatches(candidate);

        List<MatchResultDto> resultList = new java.util.ArrayList<>();
        for (ApplicationMatch match : saved) {
            MatchResultDto dto = new MatchResultDto();
            dto.setMatchId(match.getId());
            dto.setCandidateId(candidateId);
            dto.setCandidateName(candidate.getFullName());
            dto.setJobTitle(match.getJobTitle());
            dto.setCompanyName(match.getCompanyName());
            dto.setJobUrl(match.getJobUrl());
            dto.setScore(match.getScore());
            dto.setCreatedAt(match.getCreatedAt());
            dto.setSource(match.getSource());
            resultList.add(dto);
        }
        return new org.springframework.data.domain.PageImpl<>(resultList);
    }
    @GetMapping("/job/{jobPostingId}/ranked")
    public Page<Map<String, Object>> getRankedCandidatesForJob(
            @PathVariable Long jobPostingId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestHeader(value = "Authorization", required = false) String authHeader) {
        
        JobPosting job = jobPostingRepository.findById(jobPostingId).orElse(null);
        if (job == null) {
            return new org.springframework.data.domain.PageImpl<>(java.util.Collections.emptyList());
        }
        requireHrOwner(requireAccount(authHeader), job);

        List<Candidate> allCandidates = candidateRepository.findAll();
        List<Map<String, Object>> batchCandidates = new java.util.ArrayList<>();
        for (Candidate candidate : allCandidates) {
            if (candidate.getCvText() != null && !candidate.getCvText().isBlank()) {
                batchCandidates.add(Map.of("candidate_id", candidate.getId(), "cv_text", candidate.getCvText()));
            }
        }

        Map<Long, Float> scoresByCandidateId = new java.util.HashMap<>();
        if (!batchCandidates.isEmpty()) {
            try {
                Map<String, Object> payload = Map.of(
                        "job_description", buildJobText(job),
                        "candidates", batchCandidates);
                org.springframework.http.HttpHeaders headers = new org.springframework.http.HttpHeaders();
                headers.setContentType(org.springframework.http.MediaType.APPLICATION_JSON);
                ResponseEntity<Map> response = restTemplate.postForEntity(
                        fastApiBaseUrl + "/match-scores",
                        new org.springframework.http.HttpEntity<>(payload, headers), Map.class);

                Object rawScores = response.getBody() == null ? null : response.getBody().get("scores");
                if (!(rawScores instanceof List<?>)) {
                    throw new IllegalStateException("AI service không trả danh sách điểm");
                }
                for (Object rawScore : (List<?>) rawScores) {
                    if (!(rawScore instanceof Map<?, ?> scoreMap)) continue;
                    Object rawId = scoreMap.get("candidate_id");
                    Object rawPercent = scoreMap.get("match_percent");
                    if (rawId instanceof Number && rawPercent instanceof Number) {
                        scoresByCandidateId.put(((Number) rawId).longValue(), ((Number) rawPercent).floatValue());
                    }
                }
            } catch (Exception e) {
                logger.error("Không thể gọi AI batch cho job id={}: {}", jobPostingId, e.getMessage());
                throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE,
                        "Dịch vụ AI đang bận; vui lòng thử lại sau");
            }
        }

        List<Map<String, Object>> resultList = new java.util.ArrayList<>();

        for (Candidate candidate : allCandidates) {
            if (candidate.getCvText() == null || candidate.getCvText().isBlank()) continue;

            Map<String, Object> dto = new java.util.HashMap<>();
            dto.put("matchId", candidate.getId()); 
            dto.put("candidateId", candidate.getId());
            dto.put("candidateName", candidate.getFullName());
            dto.put("email", candidate.getEmail());
            
            float score = scoresByCandidateId.getOrDefault(candidate.getId(), 0f);

            dto.put("score", Math.round(score * 10.0) / 10.0);
            resultList.add(dto);
        }

        // Sắp xếp giảm dần theo điểm AI
        resultList.sort((a, b) -> Float.compare(((Number) b.get("score")).floatValue(), ((Number) a.get("score")).floatValue()));

        return new org.springframework.data.domain.PageImpl<>(resultList);
    }

    private String buildJobText(JobPosting job) {
        return String.join("\n",
                job.getTitle() == null ? "" : job.getTitle(),
                job.getDescription() == null ? "" : job.getDescription(),
                job.getRequirements() == null ? "" : job.getRequirements());
    }
}
