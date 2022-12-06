# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import python_atom_sdk as sdk

from .error_code import ErrorCode

# 导入执行系统命令的方法
import subprocess
import os
import random

err_code = ErrorCode()


def exit_with_error(error_type=None, error_code=None, error_msg="failed", platform_code=None, platform_error_code=None):
    """
    @summary: exit with error
    """
    if not error_type:
        error_type = sdk.OutputErrorType.PLUGIN
    if not error_code:
        error_code = err_code.PLUGIN_ERROR

    # 不设置错误日志输出，否则会输出两次
    # sdk.log.error("error_type: {}, error_code: {}, error_msg: {}".format(error_type, error_code, error_msg))

    output_data = {
        "status": sdk.status.FAILURE,
        "errorType": error_type,
        "errorCode": error_code,
        "message": error_msg,
        "type": sdk.output_template_type.DEFAULT,
        "platformCode": platform_code,
        "platformErrorCode": platform_error_code
    }

    sdk.set_output(output_data)

    exit(error_code)


def exit_with_succ(data=None, quality_data=None, msg="run succ"):
    """
    @summary: exit with succ
    """
    if not data:
        data = {}

    output_template = sdk.output_template_type.DEFAULT
    if quality_data:
        output_template = sdk.output_template_type.QUALITY

    output_data = {
        "status": sdk.status.SUCCESS,
        "message": msg,
        "type": output_template,
        "data": data
    }

    if quality_data:
        output_data["qualityData"] = quality_data

    sdk.set_output(output_data)

    exit(err_code.OK)


def main():
    """
    @summary: main
    """

    # 获取前端输入,根据名称获取
    input_pwsh = sdk.get_input().get("powershell_input", None)

    sdk.log.info("execute scripts is \n{}".format(input_pwsh))
    sdk.log.info("-----")
    if not input_pwsh:
        exit_with_error(error_type=sdk.output_error_type.USER,
                        error_code=err_code.USER_CONFIG_ERROR,
                        error_msg="input scripts is None")
    # 获取单选框输入,目前就一个选项,暂时没什么用
    input_checkbox = sdk.get_input().get("checkbox_lang", None)

    # 获取工作空间
    workspace = sdk.get_workspace()

    # 切换 python 工作目录
    os.chdir(workspace)

    # 随机生成一个文件，写入脚本内容
    random_num = random.randint(11111, 99999)
    file_name = "devops_%s.ps1" % random_num

    # 拼接文件绝对路径，如果文件已存在，删除文件
    script_file = os.path.join(workspace, file_name)
    if os.path.exists(script_file):
        os.remove(script_file)
    with open(file_name, 'w', encoding="utf8") as fp:
        fp.write(input_pwsh)

    res = subprocess.Popen('pwsh  -NoProfile -ExecutionPolicy Bypass -NoLogo -NonInteractive %s -Command' % file_name,
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # 标准输出
    stdout = res.stdout.read().decode()
    # sdk.log.info(stdout)

    # 错误输出
    stderr = res.stderr.read().decode()
    # sdk.log.error(stderr)

    # 执行完毕之后清除生成的临时脚本
    os.remove(file_name)

    # 如果报错输出中有内容，则使用 exit_err
    if stderr:
        sdk.log.info(stdout)
        exit_with_error(
            error_type=sdk.output_error_type.USER,
            error_code=err_code.USER_CONFIG_ERROR,
            error_msg="{}".format(stderr)
        )

    # 拼接 data
    data = {
        "scripts result":
            {
                "type": sdk.output_field_type.STRING,
                "value": "\n %s" % stdout
            }
    }

    # exit_with_succ(data=stdout)
    exit_with_succ(data=data)
