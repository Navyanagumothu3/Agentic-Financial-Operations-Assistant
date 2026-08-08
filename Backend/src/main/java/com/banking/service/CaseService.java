package com.banking.service;

import com.banking.model.CaseRequest;
import com.banking.repository.CaseRequestRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
public class CaseService {
    private final CaseRequestRepository repository;

    public CaseService(CaseRequestRepository repository) {
        this.repository = repository;
    }

    public CaseRequest createCase(CaseRequest request) {
        if (request.getCaseId() == null || request.getCaseId().isBlank()) {
            request.setCaseId("CASE-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase());
        }
        return repository.save(request);
    }

    public List<CaseRequest> listCases() {
        return repository.findAll();
    }
}
