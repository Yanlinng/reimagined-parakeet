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
