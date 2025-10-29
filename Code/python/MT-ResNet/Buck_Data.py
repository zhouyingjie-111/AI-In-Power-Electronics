import matlab.engine
import time
import os
import pandas as pd
from datetime import datetime

def main():
    print("=" * 60)
    print("Buck转换器仿真系统")
    print("=" * 60)
    
    result_file = 'E:/AI-based optimized design/Data/Input_Data/buck_data1.csv'

    # 启动MATLAB引擎
    print("正在启动MATLAB...")
    try:
        # 尝试启动
        eng = matlab.engine.start_matlab()
        print("✓ MATLAB启动成功")
        # 尝试通过命令启动MATLAB桌面
        try:
            eng.eval("desktop", nargout=0)
            print("✓ MATLAB桌面界面已启动")
            # 调整MATLAB桌面窗口位置与大小
            try:
                eng.eval("jDesktop = com.mathworks.mde.desk.MLDesktop.getInstance; jFrame = jDesktop.getMainFrame; jFrame.setBounds(50,50,1000,650);", nargout=0)
            except Exception as e:
                print(f"提示: 无法调整MATLAB桌面窗口大小: {e}")
        except:
            print("注意: MATLAB桌面界面可能无法自动启动")
                
    except Exception as e:
        print(f"✗ MATLAB启动失败: {e}")
        return
    
    # 等待MATLAB界面完全加载
    print("正在加载MATLAB界面...")
    time.sleep(10)
    print("✓ MATLAB界面加载成功")
    
    # 检查文件路径
    file_name = 'E:/AI-based optimized design/Code/matlab/BuckData.m'
    model_path = 'E:/AI-based optimized design/Simulink/Interleaved_parallel_buck'
    
    if not os.path.exists(file_name):
        print(f"✗ 找不到MATLAB脚本文件: {file_name}")
        eng.quit()
        return
        
    if not os.path.exists(model_path + '.slx'):
        print(f"✗ 找不到Simulink模型文件: {model_path}.slx")
        eng.quit()
        return
    
    print("正在加载Simulink模型...")
    # 等待模型加载完成
    time.sleep(10)
    try:
        # 设置MATLAB工作目录
        eng.eval("cd('E:/AI-based optimized design/Simulink')", nargout=0)
        
        # 使用相对路径加载Simulink模型
        model_name = 'Interleaved_parallel_buck'
        eng.eval(f"load_system('{model_name}')", nargout=0)
        
        # 打开模型界面
        eng.eval(f"open_system('{model_name}')", nargout=0)
        
        # 调整Simulink模型窗口位置与大小
        try:
            left, top, width, height = 1100, 80, 900, 600
            right = left + width
            bottom = top + height
            eng.eval(f"set_param('{model_name}', 'Location', [{left} {top} {right} {bottom}])", nargout=0)
        except Exception as e:
            print(f"提示: 无法调整Simulink窗口位置: {e}")
        
        print("✓ Simulink模型加载成功")
        
        # 设置模型显示参数，使仿真过程更清晰
        eng.eval(f"set_param('{model_name}', 'ShowPortDataTypes', 'on')", nargout=0)
        eng.eval(f"set_param('{model_name}', 'ShowLineDimensions', 'on')", nargout=0)
        
    except Exception as e:
        print(f"✗ Simulink模型加载失败: {e}")
        eng.quit()
        return

    print("\n" + "=" * 60)
    print("开始运行仿真...")
    print("=" * 60)
    
    try:
        # 运行仿真脚本
        start_time = time.time()
        print("正在执行BuckData.m脚本...")
        
        # 运行.m文件
        eng.eval("run('" + file_name + "')", nargout=0)
        
        end_time = time.time()
        print(f"\n✓ 仿真完成！总耗时: {end_time - start_time:.2f} 秒")
        
        # 显示结果文件信息
        if os.path.exists(result_file):
            file_size = os.path.getsize(result_file) / 1024  # KB
            print(f"✓ 结果已保存到: {result_file}")
            print(f"  文件大小: {file_size:.2f} KB")
        
    except Exception as e:
        print(f"✗ 仿真运行失败: {e}")
        eng.quit()
        return
    
    print("\n" + "=" * 60)
    print("数据集获取完成! MATLAB界面将保持打开状态。")
    print("您可以:")
    print("1. 查看Simulink模型")
    print("2. 分析仿真结果")
    print("3. 查看生成的CSV数据文件")
    print("4. 在MATLAB工作区中查看变量")
    print("=" * 60)
    
    # 等待用户输入，保持MATLAB界面打开
    try:
        input("按回车键关闭MATLAB...")
    except KeyboardInterrupt:
        print("\n检测到中断信号...")
    
    # 关闭MATLAB引擎
    print("正在关闭MATLAB...")

    # 等待MATLAB关闭
    time.sleep(6)

    try:
        eng.quit()
        print("✓ MATLAB已关闭")
    except Exception as e:
        print(f"✗ MATLAB关闭时出错: {e}")

if __name__ == "__main__":
    main()