package com.video_summarizer.visum.controller;

import com.video_summarizer.visum.service.SummaryService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
public class SummaryController {
    private final SummaryService summaryService;

     public SummaryController(SummaryService summaryService) {
        this.summaryService = summaryService;
     }

     @PostMapping("/send-summary-request")
    public ResponseEntity<String> sendSummaryRequest(@RequestParam("file") MultipartFile file) {
         String response = summaryService.sendSummaryRequest(file);
         return ResponseEntity.ok(response);
     }
}
