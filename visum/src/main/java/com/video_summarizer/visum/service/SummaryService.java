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
public class SummaryService {
    private final RabbitTemplate rabbitTemplate;

    public SummaryService(RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public String sendSummaryRequest(MultipartFile file) {
        String tempDir = System.getProperty("java.io.tmpdir");
        String filePath = UUID.randomUUID() + "_" + file.getOriginalFilename();
        File tempFile = new File(tempDir + File.separator + filePath);
        System.out.println("Temp file path: " + tempFile.getAbsolutePath());
        try {
            file.transferTo(tempFile);
        } catch (Exception e) {
            return "Error saving file: " + e.getMessage();
        }

        Map<String, String> job = new HashMap<>();
        job.put("filePath", tempFile.getAbsolutePath());
        job.put("jobId", UUID.randomUUID().toString());

        ObjectMapper objectMapper = new ObjectMapper();
        try {
            String jobJson = objectMapper.writeValueAsString(job);
            rabbitTemplate.convertAndSend(
                    RabbitConfig.EXCHANGE_NAME,
                    RabbitConfig.ROUTING_KEY,
                    jobJson
            );
        } catch (JsonProcessingException e) {
            return "Error converting job to JSON: " + e.getMessage();
        }

        return "Summary request sent for file: " + file.getOriginalFilename();
    }
}
