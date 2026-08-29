package com.sif.precursor.controller;

import com.sif.precursor.model.AuthRequest;
import com.sif.precursor.model.User;
import com.sif.precursor.service.AuditService;
import com.sif.precursor.service.AuthService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;
    private final AuditService auditService;

    @PostMapping("/register")
    public ResponseEntity<?> register(@Valid @RequestBody AuthRequest.Register req,
                                      HttpServletRequest request) {
        try {
            User user = authService.register(req);
            auditService.log(user.getId(), user.getEmail(), "REGISTER",
                "New user registered: " + user.getFullName(),
                request.getRemoteAddr(), true);

            return ResponseEntity.ok(Map.of(
                "message", "Registration successful",
                "user", Map.of(
                    "email", user.getEmail(),
                    "fullName", user.getFullName(),
                    "role", user.getRole()
                )
            ));
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@Valid @RequestBody AuthRequest.Login req,
                                   HttpServletRequest request) {
        try {
            Map<String, Object> result = authService.login(req);
            String email = req.email();
            auditService.log(null, email, "LOGIN",
                "Successful login",
                request.getRemoteAddr(), true);

            return ResponseEntity.ok(result);
        } catch (RuntimeException e) {
            auditService.log(null, req.email(), "LOGIN",
                "Failed login: " + e.getMessage(),
                request.getRemoteAddr(), false);

            return ResponseEntity.status(401).body(Map.of("error", "Invalid credentials"));
        }
    }

    @GetMapping("/me")
    public ResponseEntity<?> getCurrentUser(@AuthenticationPrincipal User user) {
        return ResponseEntity.ok(Map.of(
            "email", user.getEmail(),
            "fullName", user.getFullName(),
            "role", user.getRole(),
            "plant", user.getPlant()
        ));
    }
}
