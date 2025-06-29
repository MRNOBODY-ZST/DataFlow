package dataflow.pojo;

import com.fasterxml.jackson.annotation.JsonIgnore;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;


@Data
@NoArgsConstructor
@AllArgsConstructor
public class User {
    //String id, String uuid, String username, String encryptPassword, String email, String role, Integer status
    private String id;
    private String uuid;
    private String username;
    private String userpict;
    @JsonIgnore
    private String password;
    private String email;
    private String role;
    private String status;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;

}
