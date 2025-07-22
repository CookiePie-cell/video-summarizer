package com.video_summarizer.visum.service;

import com.video_summarizer.visum.model.PresignedUrlRequest;
import com.video_summarizer.visum.model.PresignedUrlResponse;

import java.util.Map;

public interface FileStorageService {
    PresignedUrlResponse createPresignedUrl(PresignedUrlRequest request);
}