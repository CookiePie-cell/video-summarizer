package com.video_summarizer.visum.controller;

import com.video_summarizer.visum.config.RabbitConfig;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class TestController {

    private final RabbitTemplate rabbitTemplate;

    @Autowired
    public TestController(RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    @GetMapping("/test")
    public String test() {
        return "System running";
    }

    @PostMapping("/send-message")
    public ResponseEntity<String> sendMessage(@RequestBody String message) {
        System.out.println("Sending message: " + message);
        rabbitTemplate.convertAndSend(
                RabbitConfig.EXCHANGE_NAME,
                RabbitConfig.ROUTING_KEY,
                message
        );
        return ResponseEntity.ok("Job submitted!");
    }
}
