package com.pinewilt.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.pinewilt.entity.User;
import com.pinewilt.service.UserService;
import com.pinewilt.util.JwtUtil;
import com.pinewilt.util.Result;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import javax.servlet.http.HttpServletRequest;
import java.util.HashMap;
import java.util.Map;

/**
 * 用户控制器
 */
@Slf4j
@RestController
@RequestMapping("/api/user")
public class UserController {

    @Autowired
    private UserService userService;

    @Autowired
    private JwtUtil jwtUtil;

    /**
     * 用户登录
     */
    @PostMapping("/login")
    public Result<?> login(@RequestBody Map<String, String> params) {
        String username = params.get("username");
        String password = params.get("password");

        User user = userService.login(username, password);
        if (user == null) {
            return Result.error("用户名或密码错误");
        }

        // 生成JWT Token
        String token = jwtUtil.generateToken(user.getId(), user.getUsername(), user.getRole());

        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("user", user);

        return Result.success(data);
    }

    /**
     * 用户注册
     */
    @PostMapping("/register")
    public Result<?> register(@RequestBody User user) {
        try {
            User newUser = userService.register(user);
            return Result.success(newUser);
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    /**
     * 获取用户信息
     */
    @GetMapping("/profile")
    public Result<?> getProfile(HttpServletRequest request) {
        Long userId = jwtUtil.getUserIdFromRequest(request);
        User user = userService.getById(userId);
        if (user == null) {
            return Result.error("用户不存在");
        }
        user.setPassword(null); // 不返回密码
        return Result.success(user);
    }

    /**
     * 更新个人信息
     */
    @PutMapping("/profile")
    public Result<?> updateProfile(@RequestBody User user, HttpServletRequest request) {
        Long userId = jwtUtil.getUserIdFromRequest(request);
        user.setId(userId);
        user.setPassword(null); // 不允许通过此接口修改密码
        userService.updateById(user);
        return Result.success("更新成功");
    }

    /**
     * 修改密码
     */
    @PutMapping("/password")
    public Result<?> changePassword(@RequestBody Map<String, String> params, HttpServletRequest request) {
        Long userId = jwtUtil.getUserIdFromRequest(request);
        try {
            userService.changePassword(userId, params.get("oldPassword"), params.get("newPassword"));
            return Result.success("密码修改成功");
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    /**
     * 获取用户列表（管理员）
     */
    @GetMapping("/list")
    public Result<?> list(
            @RequestParam(defaultValue = "1") Integer pageNum,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) String username,
            @RequestParam(required = false) String role) {

        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        if (username != null && !username.isEmpty()) {
            wrapper.like(User::getUsername, username);
        }
        if (role != null && !role.isEmpty()) {
            wrapper.eq(User::getRole, role);
        }
        wrapper.orderByDesc(User::getCreateTime);

        Page<User> page = userService.page(new Page<>(pageNum, pageSize), wrapper);
        // 隐藏密码
        page.getRecords().forEach(u -> u.setPassword(null));

        return Result.success(page);
    }

    /**
     * 添加用户（管理员）
     */
    @PostMapping
    public Result<?> create(@RequestBody User user) {
        try {
            userService.register(user);
            return Result.success("添加成功");
        } catch (RuntimeException e) {
            return Result.error(e.getMessage());
        }
    }

    /**
     * 更新用户
     */
    @PutMapping
    public Result<?> update(@RequestBody User user) {
        user.setPassword(null);
        userService.updateById(user);
        return Result.success("更新成功");
    }

    /**
     * 更新用户状态
     */
    @PutMapping("/{id}/status/{status}")
    public Result<?> updateStatus(@PathVariable Long id, @PathVariable String status) {
        userService.updateStatus(id, status);
        return Result.success("状态更新成功");
    }

    /**
     * 删除用户
     */
    @DeleteMapping("/{id}")
    public Result<?> delete(@PathVariable Long id) {
        userService.removeById(id);
        return Result.success("删除成功");
    }
}
