package com.video_summarizer.visum.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.presigner.S3Presigner;

import java.net.URI;

@Configuration
public class S3ClientConfig {
    private final MinioProperties minioProperties;

    public S3ClientConfig(MinioProperties minioProperties) {
        this.minioProperties = minioProperties;
    }

    @Bean
    public S3Presigner se3Presigner() {
        return S3Presigner.builder()
                .endpointOverride(URI.create(minioProperties.getUrl()))
                .credentialsProvider(() -> AwsBasicCredentials.create(
                        minioProperties.getAccessKey(),
                        minioProperties.getSecretKey()
                ))
                .region(Region.of(minioProperties.getRegion()))
                .build();
    }
}
