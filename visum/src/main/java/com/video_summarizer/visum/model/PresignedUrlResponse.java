package com.video_summarizer.visum.model;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class PresignedUrlResponse {
    private String keyName;
    private String url;
}
