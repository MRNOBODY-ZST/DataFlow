package com.hades.dataflow.controller;

import com.hades.dataflow.domain.dto.AuthResponse;
import com.hades.dataflow.domain.dto.LoginRequest;
import com.hades.dataflow.domain.dto.RegisterRequest;
import com.hades.dataflow.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/register")
    public Mono<AuthResponse> register(@RequestBody RegisterRequest req) {
        return authService.register(req);
    }

    @PostMapping("/login")
    public Mono<AuthResponse> login(@RequestBody LoginRequest req) {
        return authService.login(req);
    }
}
