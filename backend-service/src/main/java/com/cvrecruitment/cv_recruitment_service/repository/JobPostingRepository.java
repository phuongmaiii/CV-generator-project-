package com.cvrecruitment.cv_recruitment_service.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.cvrecruitment.cv_recruitment_service.entity.JobPosting;

@Repository
public interface JobPostingRepository extends JpaRepository<JobPosting, Long> {
    List<JobPosting> findByPositionAndStatus(String position, String status);
    List<JobPosting> findByStatus(String status);
    List<JobPosting> findByPostedByOrderByCreatedAtDesc(Long postedBy);
    List<JobPosting> findByCompanyNameContainingIgnoreCaseOrderByIdDesc(String companyName);
}