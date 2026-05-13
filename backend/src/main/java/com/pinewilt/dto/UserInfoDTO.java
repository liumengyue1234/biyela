package com.pinewilt.dto;

import lombok.Data;

/**
 * 用户信息DTO
 */
@Data
public class UserInfoDTO {

    private Long id;

    private String username;

    private String email;

    private String phone;

    private String role;

    private String status;

    private String avatar;

    private String createTime;
}
