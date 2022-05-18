# hktkzyx_toolbox 文档

[Official Website](https://hktkzyx.github.io/hktkzyx-toolbox/) | @hktkzyx/hktkzyx-toolbox

hktkzyx_toolbox 是 hktkzyx 的一个工具箱应用。
目前该工具箱主要采用命令行接口，具有一下功能：

- 养老保险计算

    计算城镇居民养老保险的预期待遇

- LED 分压电阻、电流计算

    计算 LED 的分压电阻大小

- 标准电阻查询

    根据电阻值查询标准电阻

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/hktkzyx/hktkzyx-toolbox/build-and-test)](https://github.com/hktkzyx/hktkzyx-toolbox/actions)
[![Codecov](https://img.shields.io/codecov/c/github/hktkzyx/hktkzyx-toolbox)](https://app.codecov.io/gh/hktkzyx/hktkzyx-toolbox)
[![PyPI - License](https://img.shields.io/pypi/l/hktkzyx-toolbox)](https://github.com/hktkzyx/hktkzyx-toolbox/blob/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/hktkzyx-toolbox)](https://pypi.org/project/hktkzyx-toolbox/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hktkzyx-toolbox)](https://pypi.org/project/hktkzyx-toolbox/)
[![GitHub last commit](https://img.shields.io/github/last-commit/hktkzyx/hktkzyx-toolbox)](https://github.com/hktkzyx/hktkzyx-toolbox)

## 安装

```bash
pip install hktkzyx-toolbox
```

## 使用

查询金融工具箱的命令和用法

```bash
hktkzyx-finance --help
```

查询电子工具箱的命令和用法

```bash
hktkzyx-electronics --help
```

## 如何贡献

十分欢迎 Fork 本项目！
欢迎修复 bug 或开发新功能。
开发时请遵循以下步骤:

1. 使用 [poetry](https://python-poetry.org/) 作为依赖管理

    克隆项目后，在项目文件夹运行

    ```bash
    poetry install
    ```

2. 使用 [pre-commit](https://pre-commit.com/) 并遵守 [Conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) 规范

    安装 pre-commit 并运行

    ```bash
    pre-commit install -t pre-commit -t commit-msg
    ```

    建议使用 [commitizen](https://github.com/commitizen-tools/commitizen) 提交您的 commits。

3. 建议遵循 [gitflow](https://nvie.com/posts/a-successful-git-branching-model/) 分支管理策略

    安装 [git-flow](https://github.com/petervanderdoes/gitflow-avh) 管理您的分支并运行

    ```bash
    git config gitflow.branch.master main
    git config gitflow.prefix.versiontag v
    git flow init -d
    ```

4. PR 代码到 develop 分支

*[PR]: Pull request

## 许可证

Copyright (c) 2022 Brooks YUAN.

Environment Sensor Bluetooth firmware is licensed under Mulan PSL v2.

You can use this software according to the terms and conditions of the Mulan PSL v2.
You may obtain a copy of Mulan PSL v2 at: <http://license.coscl.org.cn/MulanPSL2>.

THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.

See the Mulan PSL v2 for more details.
