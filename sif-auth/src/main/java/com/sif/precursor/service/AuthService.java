package com.sif.precursor.service;

import com.sif.precursor.model.User;
import com.sif.precursor.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public User register(AuthRequest.Register req) {
        if (userRepository.existsByEmail(req.email())) {
            throw new RuntimeException("Email already registered");
        }

        User user = new User();
        user.setEmail(req.email());
        user.setPassword(passwordEncoder.encode(req.password()));
        user.setFullName(req.fullName());
        user.setRole(req.role() != null ? req.role() : "SAFETY_OFFICER");
        user.setPlant(req.plant() != null ? req.plant() : "OIL_INDIA_DULIAJAN");
        user.setActive(true);
        user.setCreatedAt(LocalDateTime.now());

        return userRepository.save(user);
    }

    public Map<String, Object> login(AuthRequest.Login req) {
        User user = userRepository.findByEmail(req.email())
            .orElseThrow(() -> new RuntimeException("Invalid credentials"));

        if (!passwordEncoder.matches(req.password(), user.getPassword())) {
            throw new RuntimeException("Invalid credentials");
        }

        if (!user.isActive()) {
            throw new RuntimeException("Account is deactivated");
        }

        String token = jwtService.generateToken(user);

        return Map.of(
            "token", token,
            "email", user.getEmail(),
            "fullName", user.getFullName(),
            "role", user.getRole(),
            "plant", user.getPlant()
        );
    }
}
