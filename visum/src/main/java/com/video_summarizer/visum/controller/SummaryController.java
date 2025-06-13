package com.video_summarizer.visum.controller;

import com.video_summarizer.visum.service.JobService;
import com.video_summarizer.visum.service.SummaryService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;

@CrossOrigin(origins = "http://localhost:3000")
@RestController
public class SummaryController {
    private final SummaryService summaryService;
    private final JobService jobService;

     public SummaryController(SummaryService summaryService, JobService jobService) {
         this.jobService = jobService;
         this.summaryService = summaryService;
     }

     @PostMapping("/send-summary-request")
    public ResponseEntity<Map<String, String>> sendSummaryRequest(@RequestParam("file") MultipartFile file) {
         Map<String, String> response = summaryService.sendSummaryRequest(file);
         System.out.println("SUMMARY_RESPONSE: " + response.toString());
         return ResponseEntity.ok(response);
     }

     @GetMapping("/result")
    public ResponseEntity<Map<Object, Object>> getJobResult(@RequestParam("jobId") String jobId) {
            Map<Object, Object> result = jobService.getJobResult(jobId);
            System.out.println("POLLING_RESPONSE: " + result.toString());
            if (result == null || result.isEmpty()) {
                return ResponseEntity.notFound().build();
            }
            return ResponseEntity.ok(result);
     }
}
