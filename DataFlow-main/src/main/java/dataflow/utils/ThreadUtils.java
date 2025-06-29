package dataflow.utils;

import io.netty.util.concurrent.FastThreadLocal;

import java.util.Map;

public class ThreadUtils {
    private static final FastThreadLocal THREAD_LOCAL = new FastThreadLocal();

    public static <T> T get() {
        return (T) THREAD_LOCAL.get();
    }

    public static void set(Object object) {
        THREAD_LOCAL.set(object);
    }

    public static void remove() {
        THREAD_LOCAL.remove();
    }

    public static String getUserId() {
        Map<String,Object> claims = get();
        return (String) claims.get("id");
    }
}
