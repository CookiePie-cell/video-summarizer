package com.video_summarizer.visum.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.video_summarizer.visum.config.RabbitConfig;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Service
public class SummaryServiceImpl implements SummaryService {
    private final RabbitTemplate rabbitTemplate;
    private final JobService jobService;

    public SummaryServiceImpl(RabbitTemplate rabbitTemplate, JobService jobService) {
        this.rabbitTemplate = rabbitTemplate;
        this.jobService = jobService;
    }

    @Override
    public Map<String, String> sendSummaryRequest(MultipartFile file) {
        String tempDir = System.getProperty("java.io.tmpdir");
        String filePath = UUID.randomUUID() + "_" + file.getOriginalFilename();
        File tempFile = new File(tempDir + File.separator + filePath);
        System.out.println("Temp file path: " + tempFile.getAbsolutePath());
        try {
            file.transferTo(tempFile);
        } catch (Exception e) {
            throw new RuntimeException(e.getMessage());
        }

        Map<String, String> job = new HashMap<>();
        job.put("jobId", UUID.randomUUID().toString());
        job.put("filePath", tempFile.getAbsolutePath());
        job.put("status", "PENDING");
        job.put("errorMessage", null);
        job.put("createdAt", String.valueOf(System.currentTimeMillis()));
        job.put("summaryResult", null);

        ObjectMapper objectMapper = new ObjectMapper();
        try {
            String jobJson = objectMapper.writeValueAsString(job);
            String key = "job:" + job.get("jobId");
            jobService.saveData(key, job);
            rabbitTemplate.convertAndSend(
                    RabbitConfig.EXCHANGE_NAME,
                    RabbitConfig.ROUTING_KEY,
                    jobJson
            );
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to convert job to JSON: " + e.getMessage());
        }

        Map<String, String> res = new HashMap<>();
        res.put("jobId", job.get("jobId"));
        res.put("status", job.get("status"));
        return res;
    }
}
