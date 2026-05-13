package com.pinewilt.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.pinewilt.entity.User;

/**
 * 用户Service接口
 */
public interface UserService extends IService<User> {

    /**
     * 用户登录
     */
    User login(String username, String password);

    /**
     * 用户注册
     */
    User register(User user);

    /**
     * 根据用户名查询
     */
    User getByUsername(String username);

    /**
     * 修改密码
     */
    boolean changePassword(Long userId, String oldPassword, String newPassword);

    /**
     * 更新用户状态
     */
    boolean updateStatus(Long userId, String status);
}
