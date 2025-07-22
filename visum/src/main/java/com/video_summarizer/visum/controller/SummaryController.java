package com.video_summarizer.visum.controller;

import com.video_summarizer.visum.model.PresignedUrlRequest;
import com.video_summarizer.visum.model.PresignedUrlResponse;
import com.video_summarizer.visum.model.ProcessResponse;
import com.video_summarizer.visum.service.FileStorageService;
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
    private final FileStorageService fileStorageService;

     public SummaryController(SummaryService summaryService, JobService jobService, FileStorageService fileStorageService) {
         this.jobService = jobService;
         this.summaryService = summaryService;
         this.fileStorageService = fileStorageService;
     }

//     @PostMapping("/send-summary-request")
//    public ResponseEntity<ProcessResponse> sendSummaryRequest(@RequestParam("file") MultipartFile file) {
//         ProcessResponse response = summaryService.sendSummaryRequest(file);
//         System.out.println("SUMMARY_RESPONSE: " + response.toString());
//         return ResponseEntity.ok(response);
//     }

    @PostMapping("/send-summary-request")
    public ResponseEntity<ProcessResponse> sendSummaryRequest(String file) {
        ProcessResponse response = summaryService.sendSummaryRequest(file);
        System.out.println("SUMMARY_RESPONSE: " + response.toString());
        return ResponseEntity.ok(response);
    }

     @GetMapping("/result")
    public ResponseEntity<Map<Object, Object>> getJobResult(@RequestParam("jobId") String jobId) {
            Map<Object, Object> result = jobService.getJobResult(jobId);
            System.out.println("POLLING_RESPONSE FOR JOB_ID [" + jobId + "]" + ": " + result.toString());
            if (result == null || result.isEmpty()) {
                return ResponseEntity.notFound().build();
            }
            return ResponseEntity.ok(result);
     }

     @PostMapping("/get-presigned-url")
    public ResponseEntity<PresignedUrlResponse> getPresignedUrl(@RequestBody PresignedUrlRequest request) {
             PresignedUrlResponse presignedUrl = fileStorageService.createPresignedUrl(request);
            if (presignedUrl == null) {
                return ResponseEntity.notFound().build();
            }
            return ResponseEntity.ok(presignedUrl);
     }
}
