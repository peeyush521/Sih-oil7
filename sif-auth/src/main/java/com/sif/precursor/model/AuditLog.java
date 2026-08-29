package com.sif.precursor.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "audit_logs")
public class AuditLog {

    @Id
    private String id;

    private String userId;
    private String email;

    /** e.g. LOGIN, REGISTER, VIEW_REPORT, SUBMIT_REPORT, SIMULATE, EXPORT */
    private String action;

    /** Free-text detail about the action */
    private String details;

    private String ipAddress;

    private boolean success;

    @CreatedDate
    private LocalDateTime timestamp;
}
