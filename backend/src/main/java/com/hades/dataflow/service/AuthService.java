package com.hades.dataflow.service;

import com.hades.dataflow.domain.dto.AuthResponse;
import com.hades.dataflow.domain.dto.LoginRequest;
import com.hades.dataflow.domain.dto.RegisterRequest;
import com.hades.dataflow.domain.entity.User;
import com.hades.dataflow.repository.UserRepository;
import com.hades.dataflow.security.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;
import reactor.core.publisher.Mono;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    public Mono<AuthResponse> register(RegisterRequest req) {
        return userRepository.existsByUsername(req.getUsername())
                .flatMap(exists -> {
                    if (exists) {
                        return Mono.error(new ResponseStatusException(
                                HttpStatus.CONFLICT, "Username already taken"));
                    }
                    User user = User.builder()
                            .username(req.getUsername())
                            .passwordHash(passwordEncoder.encode(req.getPassword()))
                            .email(req.getEmail())
                            .build();
                    return userRepository.save(user);
                })
                .map(saved -> new AuthResponse(
                        jwtUtil.generateToken(saved.getUsername(), saved.getId()),
                        saved.getUsername(),
                        saved.getId()));
    }

    public Mono<AuthResponse> login(LoginRequest req) {
        return userRepository.findByUsername(req.getUsername())
                .switchIfEmpty(Mono.error(new ResponseStatusException(
                        HttpStatus.UNAUTHORIZED, "Invalid credentials")))
                .flatMap(user -> {
                    if (!passwordEncoder.matches(req.getPassword(), user.getPasswordHash())) {
                        return Mono.error(new ResponseStatusException(
                                HttpStatus.UNAUTHORIZED, "Invalid credentials"));
                    }
                    return Mono.just(new AuthResponse(
                            jwtUtil.generateToken(user.getUsername(), user.getId()),
                            user.getUsername(),
                            user.getId()));
                });
    }
}
