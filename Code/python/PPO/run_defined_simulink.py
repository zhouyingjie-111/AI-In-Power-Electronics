import matlab.engine
import time
import os
import pandas as pd
from datetime import datetime
import sys
try:
    import win32gui
    import win32con
    import win32api
except Exception:
    win32gui = None
    win32con = None
    win32api = None

# Ensure UTF-8 output on Windows consoles and pipes
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def set_window_topmost(hwnd, topmost=True):
    """设置窗口置顶状态"""
    try:
        if win32gui is None or win32con is None:
            return False
        flag_hwnd = win32con.HWND_TOPMOST if topmost else win32con.HWND_NOTOPMOST
        win32gui.SetWindowPos(
            hwnd,
            flag_hwnd,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW,
        )
        return True
    except Exception:
        return False


def find_matlab_window():
    """查找MATLAB主窗口"""
    try:
        if win32gui is None:
            return None
        matlab_hwnds = []
        def enum_handler(hwnd, _):
            try:
                if not win32gui.IsWindowVisible(hwnd):
                    return
                title = win32gui.GetWindowText(hwnd) or ""
                # 更宽松的匹配条件，包括MATLAB R20XX等版本
                if ("MATLAB" in title or "matlab" in title.lower()) and (win32gui.GetWindowRect(hwnd)[2] - win32gui.GetWindowRect(hwnd)[0]) > 200:
                    matlab_hwnds.append((hwnd, title))
            except Exception:
                return
        win32gui.EnumWindows(enum_handler, None)
        # 优先选择标题包含"MATLAB"的窗口，按窗口大小排序
        if matlab_hwnds:
            matlab_hwnds.sort(key=lambda x: (win32gui.GetWindowRect(x[0])[2] - win32gui.GetWindowRect(x[0])[0]) * (win32gui.GetWindowRect(x[0])[3] - win32gui.GetWindowRect(x[0])[1]), reverse=True)
            return matlab_hwnds[0][0]
        return None
    except Exception:
        return None


def find_simulink_window():
    """查找Simulink模型窗口"""
    try:
        if win32gui is None:
            return None
        simulink_hwnds = []
        def enum_handler(hwnd, _):
            try:
                if not win32gui.IsWindowVisible(hwnd):
                    return
                title = win32gui.GetWindowText(hwnd) or ""
                if "Simulink" in title and (win32gui.GetWindowRect(hwnd)[2] - win32gui.GetWindowRect(hwnd)[0]) > 100:
                    simulink_hwnds.append(hwnd)
            except Exception:
                return
        win32gui.EnumWindows(enum_handler, None)
        return simulink_hwnds[0] if simulink_hwnds else None
    except Exception:
        return None


def wait_for_confirm():
    # Require explicit 'y' to close
    print("输入 y 然后回车以关闭 MATLAB...", flush=True)
    buf = ""
    while True:
        try:
            line = sys.stdin.readline()
            if line == "":
                time.sleep(0.5)
                continue
            buf = (line or "").strip().lower()
            if buf.startswith("y"):
                break
            print("未确认，继续保持 MATLAB 打开。若要关闭请输入 y 并回车:", flush=True)
        except Exception:
            time.sleep(0.5)


def main():
    print("=" * 60)
    print("Buck转换器仿真系统")
    print("=" * 60)
    
    # 检查自定义参数CSV文件是否存在
    result_file1 = 'E:\AI-based optimized design\Visualization/self_defined_para.csv'
    
    if os.path.exists(result_file1):
        print("\n" + "=" * 60)
        print("检测到CSV文件已存在")
        print("=" * 60)
        
        # 获取文件信息
        file_stat = os.stat(result_file1)
        file_size = file_stat.st_size / 1024  # KB
        mod_time = datetime.fromtimestamp(file_stat.st_mtime)
        
        print(f"文件路径: {result_file1}")
        print(f"文件大小: {file_size:.2f} KB")
        print(f"修改时间: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 尝试读取并显示文件基本信息
        try:
            df = pd.read_csv(result_file1)
            print(f"数据行数: {len(df)}")
            print(f"数据列数: {len(df.columns)}")
            print(f"列名: {', '.join(df.columns.tolist())}")
            
            # 显示前几行数据预览
            print("\n数据预览:")
            print(df)
            print("自动执行使用优化参数后的仿真！")
            print("=" * 60)

        except Exception as e:
            print(f"无法读取文件内容: {e}")
    else:
        print("优化参数CSV文件不存在!")
        return

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
            # 设置MATLAB窗口置顶
            time.sleep(3)  # 等待窗口完全创建
            # 多次尝试查找MATLAB窗口
            matlab_hwnd = None
            for attempt in range(5):
                matlab_hwnd = find_matlab_window()
                if matlab_hwnd:
                    break
                print(f"尝试查找MATLAB窗口... ({attempt + 1}/5)")
                time.sleep(1)
            
            if matlab_hwnd:
                if set_window_topmost(matlab_hwnd, True):
                    print("✓ MATLAB窗口已置顶")
                else:
                    print("提示: 无法设置MATLAB窗口置顶")
            else:
                print("提示: 未找到MATLAB主窗口，可能窗口标题不匹配")
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
    file_name = 'E:/AI-based optimized design/Code/matlab/Defined_Parameter_Buck.m'
    model_path = 'E:/AI-based optimized design/Simulink/JCBL_Buck_Verify'
    
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
        model_name = 'JCBL_Buck_Verify'
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
        # 设置Simulink窗口置顶
        time.sleep(2)  # 等待窗口完全创建
        simulink_hwnd = find_simulink_window()
        if simulink_hwnd:
            if set_window_topmost(simulink_hwnd, True):
                print("✓ Simulink窗口已置顶")
            else:
                print("提示: 无法设置Simulink窗口置顶")
        
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
        
        # 显示仿真结果文件信息
        result_file2 = 'E:\AI-based optimized design\Data\Input_Data\optimal_simulation_result.csv'
        if os.path.exists(result_file2):
            file_size = os.path.getsize(result_file2) / 1024  # KB
            print(f"✓ 结果已保存到: {result_file2}")
            print(f"  文件大小: {file_size:.2f} KB")
        
    except Exception as e:
        print(f"✗ 仿真运行失败: {e}")
        eng.quit()
        return
    
    print("\n" + "=" * 60)
    print("仿真结果获取完成! MATLAB界面将保持打开状态。")
    print("您可以:")
    print("1. 查看Simulink模型")
    print("2. 分析仿真结果")
    print("3. 查看生成的CSV数据文件")
    print("4. 在MATLAB工作区中查看变量")
    print("=" * 60)
    
    # 等待用户 y 确认，保持MATLAB界面打开（通过管道也可等待）
    wait_for_confirm()
    
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