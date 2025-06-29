package dataflow.annotation;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * A custom marker annotation for MyBatis mappers.
 * This helps to distinguish MyBatis mappers from other interfaces (like Spring Data repositories)
 * in the same package during component scanning.
 */
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface MySQLMapper {

} 