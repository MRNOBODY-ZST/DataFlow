package dataflow.mapper;


import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import dataflow.pojo.User;
import dataflow.annotation.MySQLMapper;

@MySQLMapper
public interface UserMapper extends BaseMapper<User> {

}
