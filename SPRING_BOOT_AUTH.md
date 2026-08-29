# Spring Boot Auth & Audit Service — Java Team Guide

This document provides the full implementation blueprint for the Java/Spring Boot authentication and audit logging service that sits in front of the Python FastAPI backend.

---

## Architecture

```
Browser → Spring Boot (Auth + Audit) → FastAPI (AI Engine)
  │              │
  │         JWT Token
  │              │
  └──────────────┘
```

- **Spring Boot** handles: user registration/login, JWT tokens, role-based access, audit logging
- **FastAPI** handles: NLP processing, risk scoring, knowledge graph

---

## Step 1: Create the Spring Boot Project

```bash
# Using Spring CLI or start.spring.io
# Dependencies: Spring Web, Spring Security, Spring Data MongoDB, JJWT, Lombok
```

Or use [start.spring.io](https://start.spring.io) with:
- **Group:** `com.sif.precursor`
- **Artifact:** `sif-auth`
- **Dependencies:** Spring Web, Spring Security, Spring Data MongoDB, Validation, Lombok

---

## Step 2: Project Structure

```
src/main/java/com/sif/precursor/
├── SifAuthApplication.java
├── config/
│   ├── SecurityConfig.java
│   └── JwtConfig.java
├── controller/
│   └── AuthController.java
├── model/
│   ├── User.java
│   └── AuditLog.java
├── repository/
│   ├── UserRepository.java
│   └── AuditLogRepository.java
├── service/
│   ├── AuthService.java
│   ├── JwtService.java
│   └── AuditService.java
└── security/
    ├── JwtAuthFilter.java
    └── CustomUserDetailsService.java
```

---

## Step 3: Key Models

### User.java
```java
@Data @NoArgsConstructor @AllArgsConstructor
@Document(collection = "users")
public class User {
    @Id
    private String id;
    
    @Indexed(unique = true)
    private String email;
    
    private String password;
    private String fullName;
    private String role; // "SAFETY_OFFICER", "PLANT_MANAGER", "ADMIN"
    private String plant; // "OIL_INDIA_DULIAJAN", etc.
    private LocalDateTime createdAt;
    private boolean active;
}
```

### AuditLog.java
```java
@Data @NoArgsConstructor @AllArgsConstructor
@Document(collection = "audit_logs")
public class AuditLog {
    @Id
    private String id;
    
    private String userId;
    private String email;
    private String action; // "LOGIN", "VIEW_REPORT", "SUBMIT_REPORT", "SIMULATE_INTERVENTION"
    private String details;
    private String ipAddress;
    private LocalDateTime timestamp;
    private boolean success;
}
```

---

## Step 4: Security Configuration

### SecurityConfig.java
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Autowired
    private JwtAuthFilter jwtAuthFilter;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .cors(cors -> cors.configurationSource(corsConfigurationSource()))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/health").permitAll()
                .requestMatchers(HttpMethod.OPTIONS, "/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated()
            )
            .sessionManagement(session -> 
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
    
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(List.of("http://localhost:5173"));
        config.setAllowedMethods(List.of("*"));
        config.setAllowedHeaders(List.of("*"));
        config.setAllowCredentials(true);
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }
}
```

---

## Step 5: JWT Service

### JwtService.java
```java
@Service
public class JwtService {
    
    @Value("${jwt.secret:your-secret-key-change-in-production}")
    private String secret;
    
    @Value("${jwt.expiration:86400000}") // 24 hours
    private long expiration;
    
    public String generateToken(User user) {
        return Jwts.builder()
            .subject(user.getEmail())
            .claim("role", user.getRole())
            .claim("fullName", user.getFullName())
            .issuedAt(new Date())
            .expiration(new Date(System.currentTimeMillis() + expiration))
            .signWith(Keys.hmacShaKeyFor(secret.getBytes()))
            .compact();
    }
    
    public boolean validateToken(String token) {
        try {
            Jwts.parser()
                .verifyWith(Keys.hmacShaKeyFor(secret.getBytes()))
                .build()
                .parseSignedClaims(token);
            return true;
        } catch (JwtException e) {
            return false;
        }
    }
    
    public String extractEmail(String token) {
        return Jwts.parser()
            .verifyWith(Keys.hmacShaKeyFor(secret.getBytes()))
            .build()
            .parseSignedClaims(token)
            .getPayload()
            .getSubject();
    }
}
```

---

## Step 6: Auth Controller

### AuthController.java
```java
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Autowired private AuthService authService;
    @Autowired private AuditService auditService;

    @PostMapping("/register")
    public ResponseEntity<?> register(@Valid @RequestBody RegisterRequest req) {
        try {
            User user = authService.register(req);
            auditService.log(user.getId(), user.getEmail(), "REGISTER", 
                "New user registered: " + req.getFullName(), null, true);
            return ResponseEntity.ok(Map.of(
                "message", "Registration successful",
                "user", Map.of("email", user.getEmail(), "role", user.getRole())
            ));
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@Valid @RequestBody LoginRequest req) {
        try {
            var result = authService.login(req);
            auditService.log(result.userId(), req.email(), "LOGIN", 
                "User logged in", null, true);
            return ResponseEntity.ok(result);
        } catch (RuntimeException e) {
            auditService.log(null, req.email(), "LOGIN", 
                "Failed login attempt", null, false);
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

// Request DTOs
record RegisterRequest(
    @NotBlank String email,
    @NotBlank @Size(min = 8) String password,
    @NotBlank String fullName,
    String role
) {}

record LoginRequest(
    @NotBlank String email,
    @NotBlank String password
) {}
```

---

## Step 7: Audit Interceptor

For every API call that goes through the proxy, log it:

```java
@Component
public class AuditInterceptor implements HandlerInterceptor {

    @Autowired
    private AuditService auditService;

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
            Object handler, Exception ex) {
        
        String email = "anonymous";
        String userId = null;
        
        // Extract from JWT if present
        String authHeader = request.getHeader("Authorization");
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            // Decode JWT to get user info
            email = jwtService.extractEmail(authHeader.substring(7));
        }
        
        auditService.log(
            userId, email,
            request.getMethod() + " " + request.getRequestURI(),
            "Status: " + response.getStatus(),
            request.getRemoteAddr(),
            response.getStatus() < 400
        );
    }
}
```

---

## Step 8: application.properties

```properties
server.port=8081

# MongoDB
spring.data.mongodb.uri=mongodb://localhost:27017/sif_precursor

# JWT
jwt.secret=your-super-secret-key-at-least-32-characters-long
jwt.expiration=86400000

# Proxy to FastAPI
proxy.target=http://127.0.0.1:8000
```

---

## Step 9: Run Both Services

```bash
# Terminal 1: Spring Boot Auth (port 8081)
cd sif-auth
./mvnw spring-boot:run

# Terminal 2: FastAPI AI Engine (port 8000)
python -m uvicorn main:app --host 127.0.0.1 --port 8000

# Terminal 3: React Frontend (port 5173)
cd frontend
npm run dev
```

---

## Roles & Permissions

| Role | Can Do |
|---|---|
| `SAFETY_OFFICER` | View reports, submit reports, simulate interventions |
| `PLANT_MANAGER` | Everything + view analytics dashboard, export reports |
| `ADMIN` | Everything + user management, audit log access |

---

## Key Interview Points

1. **Why JWT?** Stateless auth — no server-side session storage. Scales horizontally.
2. **Why audit logs?** Regulatory compliance (Oil India requirement). Every action is traceable.
3. **Why separate services?** Separation of concerns. Auth is a cross-cutting concern; AI is the core product.
4. **How does it proxy?** Spring Boot sits in front, validates JWT, then forwards to FastAPI with user context in headers.
