package com.video_summarizer.visum.service;

import java.util.Map;

public interface JobService {
    void saveData(String key, Map<String, String> data);
    Map<Object, Object> getJobResult(String jobId);
}
