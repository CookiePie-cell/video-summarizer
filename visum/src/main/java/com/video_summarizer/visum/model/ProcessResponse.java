package com.video_summarizer.visum.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class ProcessResponse {
    private String message;
    @JsonProperty("job_id")
    private String jobId;
    private String status;
}
