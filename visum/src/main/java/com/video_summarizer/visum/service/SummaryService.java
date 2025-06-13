package com.video_summarizer.visum.service;

import org.springframework.web.multipart.MultipartFile;

import java.util.Map;

public interface SummaryService {

    Map<String, String> sendSummaryRequest(MultipartFile file);
}
