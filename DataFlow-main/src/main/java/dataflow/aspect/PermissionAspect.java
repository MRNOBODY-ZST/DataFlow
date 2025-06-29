package dataflow.aspect;

import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import dataflow.annotation.Permission;
import dataflow.enumerate.Role;
import dataflow.utils.ThreadUtils;

import java.nio.file.AccessDeniedException;
import java.util.Arrays;
import java.util.Map;

@Aspect
public class PermissionAspect {

    @Around("@annotation(permission)")
    public Object checkPermission(ProceedingJoinPoint joinPoint, Permission permission) throws Throwable {
        // 获取方法签名
        String methodName = joinPoint.getSignature().getName();

        // 获取方法所在的类
        Class<?> declaringClass = joinPoint.getSignature().getDeclaringType();

        // // 如果方法被标注为 @AllowAnonymous，跳过权限检查
        // if (declaringClass.getMethod(methodName).isAnnotationPresent(AllowAnonymous.class)) {
        //     return joinPoint.proceed();
        // }

        Map<String, Object> claims = ThreadUtils.get();
        Object roleClaim = claims.get("role");

        if (roleClaim == null) {
            throw new AccessDeniedException("Role Not Found");
        }

        Role userRole;
        if (roleClaim instanceof Role) {
            userRole = (Role) roleClaim;
        } else {
            userRole = Role.valueOf(roleClaim.toString().toLowerCase());
        }

        boolean hasRequiredRole = permission.roles().length == 0 || Arrays.asList(permission.roles()).contains(userRole);

        boolean hasRequiredLevel = userRole.getLevel() >= permission.minimum().getLevel();

        if (hasRequiredRole && hasRequiredLevel) {
            return joinPoint.proceed();
        }

        throw new AccessDeniedException("Permission Denied");
    }
}
