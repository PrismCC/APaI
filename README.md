本项目是之前另一个项目`terminal-gpt`的重构，主要还是优化了一下代码结构，增加了一些更便捷的功能，以及修改了一些反直觉的逻辑等等。因为是第一次这样重构，又是自己随便写写的玩具，所以可能还是很粗糙(。・ω・。)

一个月后，我又进行了第二次更加彻底的重构。主要改进有使用`toml`作为配置文件，利用`rich`进行美化，增加多行模式与更多指令，添加存档功能等等。希望大家能用得更顺手(￣▽￣) （下一次更新可能要图形化了



---

# 环境设置

1. 创建python虚拟环境，并用pip下载`openai` `rich` `tomli_w`包。在文件夹内打开终端，依次输入以下命令：
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   pip install openai
   pip install rich
   pip install tomli_w
   ```
   
2. 将`api_bin.example.toml`重命名为`api_bin.toml`，`instr_bin.example.toml`重命名为`instr_bin.toml`，`config.example.toml`重命名为`config.toml`。用文本编辑器打开`api_bin.toml`填入API信息，还可以在`instr_bin.toml`中添加自定义指令。
4. 将`APaI.example.bat`重命名为`APaI.bat`，用文本编辑器打开并填入路径。
5. 将`APaI.bat`随便放到任何文件夹下，只要确保该文件夹已被添加在`PATH`系统变量中。
6. 打开终端输入`apai`，首次运行需要从你在`api_bin.toml`填写的模型列表中指定模型ID，之后即可与大模型对话。



# 运行

在终端中输入`apai`即可



保存的对话日志将保存在程序目录下的`log`文件夹中



# 指令手册

#### exit

退出程序

#### reset

重置上下文，清空记忆

#### retry

使大模型重新输出结果

#### undo

撤销上一次对话

#### log

打开属于当前模型的日志文件

#### clean

清除当前模型下的日志

#### save + [存档名]

将当前一次对话的记录保存为文件，存储于`./save`文件夹中

#### load + [存档名]

从`./save`文件夹读取指定的存档并加载为上下文，当前对话将被清除

#### model + [模型名]

切换模型类型

模型名和API信息需要包含在`api_bin.json`中

支持模糊匹配

只输入`model`将列出模型列表

#### instr  + [指令名]

给大模型设定的指令，本身不作为提问

指令名与具体指令需要包含在`instr_bin.json`中

支持模糊匹配

只输入`instr`将列出指令列表

#### length + [上下文长度]

设定上下文长度，即记忆的最近对话个数，更早的对话会被遗忘

#### file + [文本文件路径] (可选，默认路径为`./.in.txt`)

将提供的文本文件内容作为输入

可以在终端中附加要提出的问题(可选)

两者拼接后将提供给AI

#### md

将上次输出的内容作为markdown渲染

#### help

简要指令帮助

#### [其他内容]

向大模型提问

默认为单行输入模式，按下回车即发起询问

第一行输入为空时进入多行输入模式，连续两次回车后终止输入


