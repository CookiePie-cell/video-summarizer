package com.video_summarizer.visum.service;

import com.video_summarizer.visum.model.ProcessResponse;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;

public interface SummaryService {

    ProcessResponse sendSummaryRequest(String keyName);
//    Map<String, String> sendSummaryRequest(String fileName);

}

