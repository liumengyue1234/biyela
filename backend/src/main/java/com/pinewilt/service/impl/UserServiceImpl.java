package com.pinewilt.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.pinewilt.entity.User;
import com.pinewilt.mapper.UserMapper;
import com.pinewilt.service.UserService;
import org.springframework.stereotype.Service;

/**
 * 用户Service实现类
 */
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {

    @Override
    public User login(String username, String password) {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(User::getUsername, username)
               .eq(User::getPassword, password)
               .eq(User::getStatus, "active");
        return getOne(wrapper);
    }

    @Override
    public User register(User user) {
        // 检查用户名是否已存在
        User existUser = getByUsername(user.getUsername());
        if (existUser != null) {
            throw new RuntimeException("用户名已存在");
        }
        // 设置默认值
        user.setStatus("active");
        user.setRole("user");
        save(user);
        return user;
    }

    @Override
    public User getByUsername(String username) {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(User::getUsername, username);
        return getOne(wrapper);
    }

    @Override
    public boolean changePassword(Long userId, String oldPassword, String newPassword) {
        User user = getById(userId);
        if (user == null || !user.getPassword().equals(oldPassword)) {
            throw new RuntimeException("原密码错误");
        }
        user.setPassword(newPassword);
        return updateById(user);
    }

    @Override
    public boolean updateStatus(Long userId, String status) {
        User user = getById(userId);
        if (user == null) {
            return false;
        }
        user.setStatus(status);
        return updateById(user);
    }
}
