package com.video_summarizer.visum.model;

import lombok.Data;

import java.util.Map;

@Data
public class PresignedUrlRequest {
    private String keyName;
    private Map<String, String> metaData;
}
