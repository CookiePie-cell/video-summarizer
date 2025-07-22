package com.video_summarizer.visum.service;

import com.video_summarizer.visum.config.MinioProperties;
import com.video_summarizer.visum.model.PresignedUrlRequest;
import com.video_summarizer.visum.model.PresignedUrlResponse;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
import software.amazon.awssdk.services.s3.presigner.S3Presigner;
import software.amazon.awssdk.services.s3.presigner.model.PresignedPutObjectRequest;
import software.amazon.awssdk.services.s3.presigner.model.PutObjectPresignRequest;

import java.time.Duration;
import java.util.Map;
import java.util.UUID;

@Service
public class MinioService implements FileStorageService {
    private final S3Presigner presigner;
    private final MinioProperties props;

    public MinioService(S3Presigner presigner, MinioProperties props) {
        this.presigner = presigner;
        this.props = props;
    }

    @Override
    public PresignedUrlResponse createPresignedUrl(PresignedUrlRequest request) {
        String oriKeyName = request.getKeyName();
        String fileName = UUID.randomUUID() + "_" + oriKeyName;
        String newKeyName = "uploads/" + fileName;
        PutObjectRequest.Builder builder = PutObjectRequest.builder()
                .bucket(props.getBucket())
                .key(newKeyName);

        Map<String, String> metadata = request.getMetaData();
        if (metadata != null && !metadata.isEmpty()) {
            builder.metadata(metadata);
        }

        PutObjectRequest objectRequest = builder.build();

        PutObjectPresignRequest presignRequest = PutObjectPresignRequest.builder()
                .signatureDuration(Duration.ofMinutes(10))
                .putObjectRequest(objectRequest)
                .build();

        PresignedPutObjectRequest presignedRequest = presigner.presignPutObject(presignRequest);
        String myURL = presignedRequest.url().toString();
        System.out.println("Presigned URL to upload a file to: [" + myURL + "]");
        System.out.println("HTTP method: [" + presignedRequest.httpRequest().method() + "]");

        return PresignedUrlResponse.builder().url(presignedRequest.url().toExternalForm()).keyName(fileName).build();
    }
}
