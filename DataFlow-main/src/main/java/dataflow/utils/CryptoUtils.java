package dataflow.utils;

import lombok.extern.slf4j.Slf4j;
import org.springframework.util.DigestUtils;


@Slf4j
public class CryptoUtils {
    public static String md5Encryption(String text) {
        String result = "";
        try {
            result = DigestUtils.md5DigestAsHex(text.getBytes("utf-8"));
        } catch (Exception e) {
            log.error(e.getMessage());
        }
        return result;
    }
}
