package com.cvrecruitment.cv_recruitment_service.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import com.cvrecruitment.cv_recruitment_service.entity.ApplicationMatch;

@Repository
public interface ApplicationMatchRepository extends JpaRepository<ApplicationMatch, Long> {
    List<ApplicationMatch> findByCandidateIdOrderByScoreDesc(Long candidateId);

    @Transactional
    void deleteByCandidateId(Long candidateId);
}
