package com.video_summarizer.visum;

import com.video_summarizer.visum.config.MinioProperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

@EnableConfigurationProperties(MinioProperties.class)
@SpringBootApplication
public class VisumApplication {

	public static void main(String[] args) {
		SpringApplication.run(VisumApplication.class, args);
	}

}
