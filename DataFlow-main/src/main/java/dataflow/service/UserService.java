package dataflow.service;

import com.baomidou.mybatisplus.extension.service.IService;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Pattern;
import dataflow.enumerate.RegexPattern;
import dataflow.pojo.User;

public interface UserService extends IService<User> {

    public void register(String id, String username, @Pattern(regexp = RegexPattern.PASSWORD) String password, @Email String email, String role);
    
    public User getByUsername(String username);
}
