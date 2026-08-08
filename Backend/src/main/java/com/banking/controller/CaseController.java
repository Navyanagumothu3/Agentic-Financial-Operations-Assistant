package com.banking.controller;

import com.banking.model.CaseRequest;
import com.banking.service.CaseService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/cases")
@CrossOrigin(origins = "*")
public class CaseController {
    private final CaseService caseService;

    public CaseController(CaseService caseService) {
        this.caseService = caseService;
    }

    @PostMapping
    public ResponseEntity<CaseRequest> createCase(@RequestBody CaseRequest request) {
        return ResponseEntity.ok(caseService.createCase(request));
    }

    @GetMapping
    public ResponseEntity<List<CaseRequest>> listCases() {
        return ResponseEntity.ok(caseService.listCases());
    }
}
