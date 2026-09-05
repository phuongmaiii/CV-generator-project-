package com.cvrecruitment.cv_recruitment_service.service;

import java.io.IOException;
import java.util.Map;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

@Service
public class AiMatchingService {

    private final RestTemplate restTemplate = new RestTemplate();

    // BUG CŨ: URL này trước đây bị hardcode cứng "http://127.0.0.1:8000/match", trong khi
    // mọi nơi khác trong dự án (CandidateController, MatchingService, MatchScoreController...)
    // đều đọc từ config fastapi.service.base-url. Hệ quả: chạy trên Render (production) thì
    // class này vẫn cố gọi về localhost của chính server Java, luôn luôn lỗi kết nối.
    // Đồng thời "/match" cũng không tồn tại bên FastAPI (chỉ có /parse-cv, /match-score,
    // /match-topcv) — nên trước đây endpoint /api/candidates/match-jd chắc chắn lỗi 100%
    // nếu bị gọi tới. Sửa: dùng đúng base URL từ config, và ghép lại đúng quy trình 2 bước
    // mà FastAPI thực sự hỗ trợ: (1) /parse-cv để trích text từ file CV, (2) /match-score
    // để tính điểm giữa text đó và JD.
    @Value("${fastapi.service.base-url}")
    private String fastApiBaseUrl;

    public Double calculateMatchScore(MultipartFile cvFile, String jdText) throws IOException {
        String cvText = extractCvText(cvFile);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        Map<String, String> payload = Map.of(
                "cv_text", cvText,
                "job_description", jdText
        );
        HttpEntity<Map<String, String>> request = new HttpEntity<>(payload, headers);

        ResponseEntity<Map> response = restTemplate.postForEntity(
                fastApiBaseUrl + "/match-score", request, Map.class);

        if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
            Object scoreObj = response.getBody().get("match_percent");
            if (scoreObj == null) scoreObj = response.getBody().get("match_score");
            if (scoreObj != null) {
                return Double.valueOf(scoreObj.toString());
            }
        }

        throw new RuntimeException("AI Engine phản hồi lỗi hoặc không có dữ liệu!");
    }

    private String extractCvText(MultipartFile cvFile) throws IOException {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        ByteArrayResource fileAsResource = new ByteArrayResource(cvFile.getBytes()) {
            @Override
            public String getFilename() {
                return cvFile.getOriginalFilename();
            }
        };

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", fileAsResource);

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
        ResponseEntity<Map> response = restTemplate.postForEntity(
                fastApiBaseUrl + "/parse-cv", requestEntity, Map.class);

        if (response.getBody() == null || response.getBody().get("text") == null) {
            throw new RuntimeException("Không trích xuất được nội dung CV để so khớp với JD!");
        }
        return response.getBody().get("text").toString();
    }
}
