package com.video_summarizer.visum.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class TestController {

    public TestController() {
    }

    @GetMapping("/test")
    public String test() {
        return "System running";
    }

    @PostMapping("/send-message")
    public ResponseEntity<String> sendMessage(@RequestBody String message) {
        return ResponseEntity.ok("Job submitted!");
    }
}
