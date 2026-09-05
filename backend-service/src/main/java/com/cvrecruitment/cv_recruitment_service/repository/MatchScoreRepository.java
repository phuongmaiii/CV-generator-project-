package com.cvrecruitment.cv_recruitment_service.repository;

import java.util.List;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.cvrecruitment.cv_recruitment_service.entity.MatchScore;

@Repository
public interface MatchScoreRepository extends JpaRepository<MatchScore, Long> {
    List<MatchScore> findByJobPostingId(Long jobPostingId);
    Page<MatchScore> findByCandidateIdOrderByScoreDesc(Long candidateId, Pageable pageable);
    Page<MatchScore> findByJobPostingIdOrderByScoreDesc(Long jobPostingId, Pageable pageable);
}