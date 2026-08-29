package com.sif.precursor.repository;

import com.sif.precursor.model.AuditLog;
import org.springframework.data.mongodb.repository.MongoRepository;

import java.util.List;

public interface AuditLogRepository extends MongoRepository<AuditLog, String> {

    List<AuditLog> findByUserIdOrderByTimestampDesc(String userId);

    List<AuditLog> findByEmailOrderByTimestampDesc(String email);

    List<AuditLog> findByActionOrderByTimestampDesc(String action);

    List<AuditLog> findBySuccessFalseOrderByTimestampDesc(String action);
}
