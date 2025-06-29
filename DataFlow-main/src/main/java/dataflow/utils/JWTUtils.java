package dataflow.utils;

import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import lombok.extern.slf4j.Slf4j;

import java.util.Date;
import java.util.Map;

@Slf4j
public class JWTUtils {
    private static final String JWT_SECRET = "123";  // Consider using a more secure secret in production
    private static final String TOKEN_PREFIX = "Bearer ";

    public static String encode(Map<String, Object> claims) {
        log.info("Using secret key: {}", JWT_SECRET);
        return JWT.create().withClaim("claims", claims).withExpiresAt(new Date(System.currentTimeMillis() + 1000 * 60 * 60 * 24)).sign(Algorithm.HMAC512(JWT_SECRET));
    }

    public static Map<String, Object> decode(String token) {
        // Remove "Bearer " prefix if present
        String actualToken = token;
        if (token != null && token.regionMatches(true, 0, TOKEN_PREFIX, 0, TOKEN_PREFIX.length())){
            actualToken = token.substring(TOKEN_PREFIX.length());
        }
        assert actualToken != null;
        return JWT.require(Algorithm.HMAC512(JWT_SECRET)).build().verify(actualToken).getClaim("claims").asMap();
    }
}