package dataflow.enumerate;

import lombok.Getter;

@Getter
public enum Role {
    admin(3), teacher(2), student(1), guest(0);

    private final int level;

    Role(int level) {
        this.level = level;
    }

}
