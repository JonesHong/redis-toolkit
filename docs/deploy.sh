#!/usr/bin/env sh

# 確保腳本拋出遇到的錯誤
set -e

# 生成靜態檔案
echo "Building VuePress site..."
npm run build

# 進入生成的資料夾
cd .vuepress/dist

# 如果是發布到自定義域名
# echo 'www.example.com' > CNAME

git init
git add -A
git commit -m 'deploy'

# 如果發布到 https://<USERNAME>.github.io/<REPO>
# git push -f git@github.com:JonesHong/redis-toolkit.git master:gh-pages

# 如果使用 GitHub Pages 的 docs 分支
# git push -f git@github.com:JonesHong/redis-toolkit.git master:docs

cd -

echo "Deployment complete!"