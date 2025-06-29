package dataflow.controller;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Pattern;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import dataflow.enumerate.RegexPattern;
import dataflow.enumerate.ResponseCode;
import dataflow.pojo.Response;
import dataflow.pojo.User;
import dataflow.service.UserService;
import dataflow.utils.CryptoUtils;
import dataflow.utils.JWTUtils;
import dataflow.utils.ThreadUtils;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/user")
public class UserController {

    private final UserService userService;
    
    @Autowired
    private UserController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping
    // @AllowAnonymous
    public Response<Void> register(String id, String username, @Pattern(regexp = RegexPattern.PASSWORD) String password, @Email String email, String role) {
        User user = userService.getById(id);
        if (user == null) {
            userService.register(id, username, password, email, role);
            return Response.success(ResponseCode.SUCCESS, "success", null);
        } else {
            return Response.error(ResponseCode.ERROR, "User Already Exists");
        }
    }

    @PostMapping(value = "/login")
    public Response<String> login(String username, String password) {
        User user = userService.getByUsername(username);
        if (user == null || !user.getPassword().equals(CryptoUtils.md5Encryption(password))) {
            return Response.error(ResponseCode.INVALID_CREDENTIALS, "Incorrect username or password");
        } else {
            Map<String, Object> claims = new HashMap<>();
            claims.put("id", user.getId());
            claims.put("role", user.getRole());
            return Response.success(ResponseCode.SUCCESS, "success", JWTUtils.encode(claims));
        }
    }

    @GetMapping
    public Response<User> getUserInfo() {
        Map<String, Object> claims = ThreadUtils.get();
        String id = (String) claims.get("id");
        return Response.success(ResponseCode.SUCCESS, "success", userService.getById(id));
    }

    @PatchMapping
    public Response<Void> updateUserInfo(@RequestBody User user) {
        Map<String, Object> claims = ThreadUtils.get();
        String id = (String) claims.get("id");
        if (id == null) {
            return Response.error(ResponseCode.INVALID_CREDENTIALS, "Invalid token");
        } else if (userService.getById(id) == null) {
            return Response.error(ResponseCode.ERROR, "Invalid user");
        } else if (id.equals(user.getId())) {
            userService.updateById(user);
            return Response.success(ResponseCode.SUCCESS, "success", null);
        } else {
            return Response.error(ResponseCode.ERROR, "Invalid user");
        }
    }
}
