package com.sif.precursor.service;

import com.sif.precursor.model.AuditLog;
import com.sif.precursor.repository.AuditLogRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.List;

@Slf4j
@Service
@RequiredArgsConstructor
public class AuditService {

    private final AuditLogRepository auditLogRepository;

    @Async
    public void log(String userId, String email, String action, String details, String ipAddress, boolean success) {
        try {
            AuditLog entry = new AuditLog();
            entry.setUserId(userId);
            entry.setEmail(email);
            entry.setAction(action);
            entry.setDetails(details);
            entry.setIpAddress(ipAddress);
            entry.setSuccess(success);

            auditLogRepository.save(entry);
            log.debug("Audit: {} | {} | {} | success={}", email, action, details, success);
        } catch (Exception e) {
            log.error("Failed to write audit log: {}", e.getMessage());
        }
    }

    public List<AuditLog> getLogsForUser(String userId) {
        return auditLogRepository.findByUserIdOrderByTimestampDesc(userId);
    }

    public List<AuditLog> getFailedLogins() {
        return auditLogRepository.findBySuccessFalseOrderByTimestampDesc("LOGIN");
    }

    public List<AuditLog> getAllByAction(String action) {
        return auditLogRepository.findByActionOrderByTimestampDesc(action);
    }
}
