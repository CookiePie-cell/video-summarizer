package com.video_summarizer.visum.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.video_summarizer.visum.model.ProcessResponse;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Service
public class SummaryServiceImpl implements SummaryService {
    private final JobService jobService;

    public SummaryServiceImpl(JobService jobService) {
        this.jobService = jobService;
    }

//    @Override
//    public Map<String, String> sendSummaryRequest(String fileName) {
//        Map<String, String> job = new HashMap<>();
//        job.put("jobId", UUID.randomUUID().toString());
//        job.put("fileName", fileName);
//        job.put("status", "PENDING");
//        job.put("errorMessage", null);
//        job.put("createdAt", String.valueOf(System.currentTimeMillis()));
//        job.put("summaryResult", null);
//
//        ObjectMapper objectMapper = new ObjectMapper();
//
//        try {
//            String jobJson = objectMapper.writeValueAsString(job);
//            String key = "job:" + job.get("jobId");
//            jobService.saveData(key, job);
//            rabbitTemplate.convertAndSend(
//                    RabbitConfig.EXCHANGE_NAME,
//                    RabbitConfig.ROUTING_KEY,
//                    jobJson
//            );
//        } catch (JsonProcessingException e) {
//            throw new RuntimeException("Failed to convert job to JSON: " + e.getMessage());
//        }
//
//        Map<String, String> res = new HashMap<>();
//        res.put("jobId", job.get("jobId"));
//        res.put("status", job.get("status"));
//        return res;
//    }

    @Override
    public ProcessResponse sendSummaryRequest(String keyName) {
        Map<String, String> job = new HashMap<>();
        job.put("jobId", UUID.randomUUID().toString());
        job.put("keyName", keyName);
        job.put("status", "PENDING");
        job.put("errorMessage", null);
        job.put("createdAt", String.valueOf(System.currentTimeMillis()));
        job.put("summaryResult", null);

        String key = "job:" + job.get("jobId");
        jobService.saveData(key, job);
        return callSummaryService(keyName, job.get("jobId"), job.get("status"));

    }

    private ProcessResponse callSummaryService(String keyName, String jobId, String status) {
        RestTemplate restTemplate = new RestTemplate();
        String url = "http://fastapi:8000/transcribe-and-summarize";

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        Map<String, String> body = new HashMap<>();
        body.put("object_key", "uploads/" + keyName);
        body.put("job_id", jobId);
        body.put("status", status);

        HttpEntity<Map<String, String>> request = new HttpEntity<>(body, headers);
        ResponseEntity<String> response = restTemplate.postForEntity(url, request, String.class);

        ObjectMapper objectMapper = new ObjectMapper();
        try {
            return objectMapper.readValue(response.getBody(), ProcessResponse.class);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to parse response from summary service: " + e.getMessage());
        }
    }
}
