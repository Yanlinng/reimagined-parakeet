# 古焱玲个人主页

这是一个纯静态网站，网站入口文件为 `index.html`，不需要构建工具或服务器。

## 发布后的网址

本网站对应的 GitHub Pages 地址为：

```text
https://Yanlinng.github.io/reimagined-parakeet/
```

GitHub 仓库名请使用 `reimagined-parakeet`。网址路径中使用连字符，不要使用空格。

## 发布步骤

1. 登录 GitHub，新建一个公开仓库，仓库名填写 `reimagined-parakeet`。
2. 将本目录中的 `index.html` 和 `README.md` 上传到仓库根目录。
3. 打开仓库的 `Settings`，进入 `Pages`。
4. 在 `Build and deployment` 中选择 `Deploy from a branch`。
5. 选择 `main` 分支和 `/(root)` 目录，然后保存。
6. 等待约 1 到 3 分钟，GitHub 会生成可访问的个人主页网址。

## 使用 Git 推送

```bash
git init
git add .
git commit -m "Add personal website"
git branch -M main
git remote add origin https://github.com/Yanlinng/reimagined-parakeet.git
git push -u origin main
```

推送完成后，再到仓库的 `Settings > Pages` 中启用 GitHub Pages。

## Git 基础概念

- **分支**：分支是从主线代码中分离出来的独立开发线，可以在不影响主分支的情况下修改、试验和开发新功能。
- **合并**：合并是把一条分支上的修改整合回另一条分支的过程，用于让不同开发线上的内容重新汇合。

## 命令行与 Git 常用命令

### 基础命令

- `cd`：Change Directory，用于进入指定文件夹。
- `ls`：List，用于列出当前文件夹中的文件和子文件夹。
- `mkdir`：Make Directory，用于创建新文件夹。

### Git 常用命令

- `git init`：在当前文件夹初始化一个 Git 仓库。
- `git status`：查看当前文件修改、暂存和提交状态。
- `git add .`：把当前目录下所有修改加入暂存区。
- `git commit -m "说明"`：把暂存区中的修改保存成一次提交记录。
- `git branch`：查看、创建或删除分支。
- `git switch 分支名`：切换到指定分支。
- `git merge 分支名`：把指定分支的修改合并到当前分支。
- `git push`：把本地提交上传到 GitHub 远程仓库。
- `git pull`：从远程仓库获取最新修改并合并到本地。
- `git log`：查看历史提交记录。
