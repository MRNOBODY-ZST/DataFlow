package dataflow.enumerate;

import lombok.Data;

@Data
public final class RegexPattern {
    public static final String PASSWORD = "^(?=.*\\d)(?=.*[a-zA-Z])(?=.*[^\\da-zA-Z\\s]).{8,64}$";
}
