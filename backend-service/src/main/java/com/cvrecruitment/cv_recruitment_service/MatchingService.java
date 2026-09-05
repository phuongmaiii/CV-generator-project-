package com.cvrecruitment.cv_recruitment_service;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import com.cvrecruitment.cv_recruitment_service.entity.ApplicationMatch;
import com.cvrecruitment.cv_recruitment_service.entity.Candidate;
import com.cvrecruitment.cv_recruitment_service.entity.JobPosting;
import com.cvrecruitment.cv_recruitment_service.repository.ApplicationMatchRepository;

@Service
public class MatchingService {

    private static final Logger logger = LoggerFactory.getLogger(MatchingService.class);

    private final RestTemplate restTemplate;
    private final ApplicationMatchRepository applicationMatchRepository;

    @Value("${fastapi.service.base-url:http://localhost:8000}")
    private String fastApiBaseUrl;

    public MatchingService(RestTemplate restTemplate,
                           ApplicationMatchRepository applicationMatchRepository) {
        this.restTemplate = restTemplate;
        this.applicationMatchRepository = applicationMatchRepository;
    }

    // GHI CHÚ: đã xoá processCvMatching() cũ — nó gọi sang FastAPI endpoint "/match"
    // (nhận file CV + toàn bộ jobs_data) nhưng endpoint này KHÔNG hề tồn tại trong
    // ai-service/main.py (chỉ có /parse-cv, /match-score, /match-topcv, /classify/...),
    // nên hàm đó luôn trả lỗi 404 nếu bị gọi tới. Vì frontend chưa từng gọi route
    // /api/matches/upload-cv gắn với hàm này, nó là dead code — xoá cho đỡ gây nhầm lẫn
    // thay vì để lại 1 chức năng "trông như chạy được nhưng chắc chắn lỗi".

    /**
     * Cào TopCV + tính điểm match cho 1 hồ sơ ứng tuyển (candidate = 1 lần upload CV),
     * rồi LƯU LẠI kết quả vào bảng application_matches.
     *
     * Trước đây bước "auto match lúc upload" (autoMatchForNewCandidate) chỉ log ra
     * console chứ không lưu gì cả, còn trang xem kết quả lại tự cào lại TopCV một lần
     * nữa mỗi khi mở trang — 2 luồng độc lập, không liên quan tới nhau, kết quả có thể
     * khác nhau mỗi lần xem. Giờ chỉ có 1 chỗ duy nhất thực hiện việc cào + lưu, các nơi
     * khác (dashboard, trang xem chi tiết) chỉ đọc lại dữ liệu đã lưu.
     */
    @SuppressWarnings("unchecked")
    @Transactional
    public List<ApplicationMatch> refreshTopCvMatches(Candidate candidate) {
        String searchKeyword = candidate.getPosition() != null ? candidate.getPosition() : "IT";
        String cvText = candidate.getCvText() != null ? candidate.getCvText() : "";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        Map<String, String> payload = Map.of(
            "keyword", searchKeyword,
            "cv_text", cvText,
            "candidate_id", String.valueOf(candidate.getId())
        );

        HttpEntity<Map<String, String>> request = new HttpEntity<>(payload, headers);

        List<ApplicationMatch> saved = new ArrayList<>();
        try {
            ResponseEntity<Map> response = restTemplate.postForEntity(
                fastApiBaseUrl + "/match-topcv", request, Map.class
            );

            Map<String, Object> body = response.getBody();
            if (body != null && body.get("content") instanceof List) {
                List<Map<String, Object>> jobs = (List<Map<String, Object>>) body.get("content");

                // Xoá kết quả cũ của hồ sơ này trước khi lưu kết quả mới, tránh tích luỹ
                // dữ liệu trùng/lỗi thời qua mỗi lần "làm mới".
                applicationMatchRepository.deleteByCandidateId(candidate.getId());

                for (Map<String, Object> job : jobs) {
                    ApplicationMatch match = new ApplicationMatch();
                    match.setCandidateId(candidate.getId());
                    match.setJobTitle((String) job.get("jobTitle"));
                    match.setCompanyName((String) job.get("companyName"));
                    match.setJobUrl((String) job.get("url"));

                    Object scoreObj = job.get("score");
                    match.setScore(scoreObj instanceof Number ? ((Number) scoreObj).floatValue() : 0f);

                    // "TOPCV" = job cào thật; "DEMO" = dữ liệu fallback giả lập khi crawl lỗi
                    // (xem ai-service/main.py, hàm match_topcv). Trước đây phần này bị trả về
                    // lẫn với job thật mà không có cờ đánh dấu gì — người dùng không biết đâu
                    // là job thật, đâu là demo.
                    Object sourceObj = job.get("source");
                    match.setSource(sourceObj != null ? sourceObj.toString() : "TOPCV");

                    saved.add(applicationMatchRepository.save(match));
                }
            }

            logger.info("Da luu {} ket qua match cho candidate id={}", saved.size(), candidate.getId());
        } catch (Exception e) {
            logger.error("Loi khi cao/luu TopCV cho candidate id={}: {}", candidate.getId(), e.getMessage(), e);
        }

        return saved;
    }

    public void autoMatchForNewCandidate(Candidate candidate) {
        refreshTopCvMatches(candidate);
    }

    public void autoMatchForNewJobPosting(JobPosting jobPosting) {
        // TODO: chiều "HR tạo job mới -> match với candidate có sẵn" vẫn chưa cài đặt
    }
}
