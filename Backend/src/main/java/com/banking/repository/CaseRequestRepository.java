package com.banking.repository;

import com.banking.model.CaseRequest;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CaseRequestRepository extends JpaRepository<CaseRequest, Long> {
}
