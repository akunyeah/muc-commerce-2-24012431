# 第7天学生项目：电商用户分析Web系统

## 运行方法

```bash
python -m pip install -r requirements.txt
python app.py
```

浏览器访问 `http://127.0.0.1:5000`。

- 用户名：`student`
- 密码：`day07`

## 上午停止线

上午只完成以下内容：

1. 建立并重命名个人项目；
2. 从VS Code终端启动Flask；
3. 测试正确登录、错误登录、访问拦截和退出；
4. 定位`app.py`、`services`、`templates`、`static`和`data`；
5. 核对已有2张指标卡、1张图和“总用户数”问答；
6. 搜索TODO，但暂不修改`TODO 2-1`至`TODO 4-1`。

## 下午核心任务

1. 检查并解释登录、退出和登录访问控制；
2. 完成4张指标卡和2张真实图表；
3. 完成偏好品类筛选；
4. 完成至少4类离线规则问答；
5. 在`screenshots`目录保存4张核心验收截图；
6. 完成一项必选拓展；
7. 修改本文件，填写个人信息、完成功能、拓展说明和未解决问题。

使用编辑器搜索`TODO`即可找到需要完成的位置。

## 必选拓展（三选一）

### A. 导出当前筛选结果

新增CSV下载功能，导出内容必须与当前`category`筛选一致。

### B. 生命周期详情页

新增`/segments`页面，展示各生命周期阶段的用户数、流失人数和流失率。

### C. Flask自动化测试

新增`tests/`目录，至少测试正确登录、未登录访问看板和`/api/ask`。

完成后必须填写下面的拓展信息，并提供`screenshots/05_extension.png`、`test_result.txt`或`tests/`测试文件作为证据。

## 学生信息

- 姓名：钟俊坤
- 学号：24012431
- 专题方向：A 
- 已完成功能：   登录 / 退出 / 登录拦截（app.py:17-23 login_required 装饰器）。  
                4 张指标卡：总用户数、流失用户、总体流失率、平均订单数（services/data_service.py:37-42）。  
                2 张可视化图表：不同偏好品类用户比较、不同阶段用户流失率（templates/dashboard.html:48-50）。  
                偏好品类筛选（services/data_service.py:45-49 + app.py:56-57）。  
                至少 4 类规则问答（services/qa_service.py）。  
                导出当前筛选结果
- 选择的拓展任务：A
- 拓展访问或运行方法：pip install -r requirements.txt 安装依赖。  
                    python app.py 启动服务，访问 http://127.0.0.1:5000 。
                    使用账号 student / day07 登录。  
                    在数据看板的"按偏好品类筛选"卡片中：  
                    选择下拉框中的品类（全部 / Fashion / Electronics / 等）。  
                    点击左侧"下载当前数据"按钮，浏览器会弹出下载框。  
                    文件为 UTF-8-SIG 编码（中文不乱码），文件名为 {品类}_品类分析数据.csv，内容与当前界面表格一致。
- 拓展证据文件：screenshots/05_extension.png
- 尚未解决的问题：未做服务端下载次数 / 频率限制，项目正式上线前需补充简单限流或日志审计
