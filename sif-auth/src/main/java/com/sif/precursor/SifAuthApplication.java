package com.sif.precursor;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.mongodb.config.EnableMongoAuditing;

@SpringBootApplication
@EnableMongoAuditing
public class SifAuthApplication {

    public static void main(String[] args) {
        SpringApplication.run(SifAuthApplication.class, args);
    }
}
