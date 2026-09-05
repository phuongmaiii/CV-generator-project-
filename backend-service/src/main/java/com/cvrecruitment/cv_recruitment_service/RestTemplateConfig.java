package com.cvrecruitment.cv_recruitment_service;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;

@Configuration
public class RestTemplateConfig {

    @Bean
    public RestTemplate restTemplate() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        
        // Thiết lập timeout trực tiếp bằng mili-giây (5000ms = 5 giây)
        factory.setConnectTimeout(10000); 
        factory.setReadTimeout(120000); 
        
        return new RestTemplate(factory);
    }
}