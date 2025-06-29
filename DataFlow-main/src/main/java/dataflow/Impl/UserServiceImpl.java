package dataflow.Impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Pattern;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import dataflow.enumerate.RegexPattern;
import dataflow.mapper.UserMapper;
import dataflow.pojo.User;
import dataflow.service.UserService;
import dataflow.utils.CryptoUtils;

import java.util.UUID;

@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {

    private final UserMapper userMapper;

    @Autowired
    public UserServiceImpl(UserMapper userMapper) {
        this.userMapper = userMapper;
    }

    @Override
    public void register(String id, String username, @Pattern(regexp = RegexPattern.PASSWORD) String password, @Email String email, String role) {

        User user = new User();
        user.setUuid(UUID.randomUUID().toString());
        user.setUsername(username);
        user.setPassword(CryptoUtils.md5Encryption(password));
        user.setEmail(email);
        user.setRole(role);
        user.setStatus("1");
        userMapper.insert(user);
    }

    @Override
    public User getByUsername(String username) {
        return userMapper.selectOne(new QueryWrapper<User>().eq("username", username));
    }
}
