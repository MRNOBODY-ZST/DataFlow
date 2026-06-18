package com.hades.dataflow.service;

import com.hades.dataflow.domain.dto.*;
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

    public Mono<UserProfileResponse> getProfile(Long userId) {
        return userRepository.findById(userId)
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.NOT_FOUND, "User not found")))
                .map(user -> new UserProfileResponse(user.getId(), user.getUsername(), user.getEmail(), user.getCreatedAt()));
    }

    public Mono<UserProfileResponse> updateProfile(Long userId, UpdateProfileRequest req) {
        return userRepository.findById(userId)
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.NOT_FOUND, "User not found")))
                .flatMap(user -> {
                    user.setEmail(req.getEmail());
                    return userRepository.save(user);
                })
                .map(user -> new UserProfileResponse(user.getId(), user.getUsername(), user.getEmail(), user.getCreatedAt()));
    }

    public Mono<Void> changePassword(Long userId, ChangePasswordRequest req) {
        return userRepository.findById(userId)
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.NOT_FOUND, "User not found")))
                .flatMap(user -> {
                    if (!passwordEncoder.matches(req.getCurrentPassword(), user.getPasswordHash())) {
                        return Mono.error(new ResponseStatusException(HttpStatus.BAD_REQUEST, "Current password is incorrect"));
                    }
                    user.setPasswordHash(passwordEncoder.encode(req.getNewPassword()));
                    return userRepository.save(user);
                })
                .then();
    }
}
