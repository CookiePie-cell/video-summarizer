package com.video_summarizer.visum.service;

import org.springframework.data.redis.RedisConnectionFailureException;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Retryable;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
public class JobServiceImpl implements JobService {
    private final RedisTemplate<String, String> redisTemplate;

    public JobServiceImpl(RedisTemplate<String, String> redisTemplate) {
        this.redisTemplate = redisTemplate;
    }

    @Retryable(
        retryFor = RedisConnectionFailureException.class,
        maxAttempts = 5,
        backoff = @Backoff(delay = 3000)
    )
    @Override
    public void saveData(String key, Map<String, String> data) {
        redisTemplate.opsForHash().putAll(key, data);
    }

    @Override
    public Map<Object, Object> getJobResult(String jobId) {
        return redisTemplate.opsForHash().entries("job:" + jobId);
    }
}
