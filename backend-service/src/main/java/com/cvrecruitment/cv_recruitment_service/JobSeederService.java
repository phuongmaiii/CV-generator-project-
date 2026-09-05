package com.cvrecruitment.cv_recruitment_service;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import com.cvrecruitment.cv_recruitment_service.entity.JobPosting;
import com.cvrecruitment.cv_recruitment_service.repository.JobPostingRepository;

@Service
public class JobSeederService {

    private static final Logger log = LoggerFactory.getLogger(JobSeederService.class);

    private static final Set<String> IT_KEYWORDS = Set.of(
            "developer", "engineer", "analyst", "scientist", "architect",
            "devops", "sre", "reliability", "qa", "test", "tester",
            "mobile", "android", "ios", "cloud", "administrator", "sysadmin",
            "security", "cybersecurity", "machine learning", "ai ", " ai,", "data",
            "software", "backend", "frontend", "full-stack", "fullstack",
            "database", "dba", "embedded", "project manager", "business analyst"
    );

    private final JobPostingRepository jobPostingRepository;
    private final MatchingService matchingService;
    private final RestTemplate restTemplate;

    @Value("${fastapi.service.base-url}")
    private String fastApiBaseUrl;

    public JobSeederService(JobPostingRepository jobPostingRepository,
                             MatchingService matchingService,
                             RestTemplate restTemplate) {
        this.jobPostingRepository = jobPostingRepository;
        this.matchingService = matchingService;
        this.restTemplate = restTemplate;
    }

    public void seedJobsFromApi() {
        String apiUrl = "https://www.arbeitnow.com/api/job-board-api";

        try {
            log.info("Dang lay du lieu viec lam tu Internet...");
            Map<String, Object> response = restTemplate.getForObject(apiUrl, Map.class);

            if (response == null || !response.containsKey("data")) {
                log.warn("API khong tra ve du lieu hop le.");
                return;
            }

            @SuppressWarnings("unchecked")
            List<Map<String, Object>> jobs = (List<Map<String, Object>>) response.get("data");

            int count = 0;
            for (Map<String, Object> jobData : jobs) {
                if (count >= 100) break;

                String title = (String) jobData.get("title");
                if (title == null || !isItRole(title)) {
                    continue;
                }

                JobPosting job = new JobPosting();
                job.setTitle(title);
                job.setCompanyName((String) jobData.get("company_name"));
                job.setPostedBy(1L);
                job.setStatus("open");

                String description = (String) jobData.get("description");
                if (description != null) {
                    description = description.replaceAll("<[^>]*>", "");
                }
                job.setDescription(description);

                classifyPosition(job);

                JobPosting savedJob = jobPostingRepository.save(job);
                matchingService.autoMatchForNewJobPosting(savedJob);
                count++;
            }

            log.info("Da them thanh cong {} cong viec IT vao he thong!", count);

        } catch (Exception e) {
            log.error("Loi khi lay du lieu: ", e);
        }
    }

    private boolean isItRole(String title) {
        String titleLower = title.toLowerCase();
        return IT_KEYWORDS.stream().anyMatch(titleLower::contains);
    }

    private void classifyPosition(JobPosting job) {
        try {
            Map<String, String> body = Map.of(
                    "text", job.getTitle() + " " + (job.getDescription() != null ? job.getDescription() : "")
            );
            ResponseEntity<Map> aiResponse = restTemplate.postForEntity(
                    fastApiBaseUrl + "/classify/position", body, Map.class);
            job.setPosition((String) aiResponse.getBody().get("predicted_label"));
        } catch (Exception e) {
            log.warn("FastAPI khong phan loai duoc position cho job '{}': {}", job.getTitle(), e.getMessage());
        }
    }
}