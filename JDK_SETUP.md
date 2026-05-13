# JDK环境配置指南

## 问题
Maven编译时报错：`No compiler is provided in this environment. Perhaps you are running on a JRE rather than a JDK?`

## 解决方案

### 方法1：安装JDK并配置环境变量

1. **下载安装JDK**
   - 访问：https://www.oracle.com/java/technologies/downloads/
   - 下载JDK 8或JDK 11（推荐JDK 8，与项目兼容）
   - 安装到默认路径，如：`C:\Program Files\Java\jdk1.8.0_391`

2. **配置环境变量**
   - 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
   - 新建系统变量：
     - 变量名：`JAVA_HOME`
     - 变量值：`C:\Program Files\Java\jdk1.8.0_391`（你的JDK安装路径）
   - 编辑系统变量`Path`，添加：`%JAVA_HOME%\bin`

3. **验证配置**
   打开新的命令行窗口，执行：
   ```bash
   java -version
   javac -version
   echo %JAVA_HOME%
   ```

### 方法2：在Maven中指定JDK路径

编辑Maven的`conf/settings.xml`，在`<profiles>`标签内添加：

```xml
<profile>
    <id>jdk-1.8</id>
    <activation>
        <activeByDefault>true</activeByDefault>
        <jdk>1.8</jdk>
    </activation>
    <properties>
        <maven.compiler.source>1.8</maven.compiler.source>
        <maven.compiler.target>1.8</maven.compiler.target>
        <maven.compiler.compilerVersion>1.8</maven.compiler.compilerVersion>
    </properties>
</profile>
```

### 方法3：使用IDE内置Maven

如果使用IntelliJ IDEA或Eclipse：
1. 在IDE中打开项目
2. 配置项目SDK为JDK路径
3. 使用IDE的Maven工具编译运行（IDE会自动使用配置的JDK）

## 验证后端编译

配置完成后，在项目根目录执行：

```bash
cd backend
mvn clean compile
mvn spring-boot:run
```

后端将在 http://localhost:8080 启动
