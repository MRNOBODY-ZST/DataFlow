package com.hades.dataflow.controller;

import com.hades.dataflow.domain.dto.*;
import com.hades.dataflow.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
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

    @GetMapping("/profile")
    public Mono<UserProfileResponse> getProfile(Authentication auth) {
        return authService.getProfile(getUserId(auth));
    }

    @PutMapping("/profile")
    public Mono<UserProfileResponse> updateProfile(@RequestBody UpdateProfileRequest req, Authentication auth) {
        return authService.updateProfile(getUserId(auth), req);
    }

    @PutMapping("/password")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public Mono<Void> changePassword(@RequestBody ChangePasswordRequest req, Authentication auth) {
        return authService.changePassword(getUserId(auth), req);
    }

    private Long getUserId(Authentication auth) {
        return (Long) auth.getDetails();
    }
}
