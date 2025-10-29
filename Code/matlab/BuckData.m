% 创建数据集,并分批次处理,防止MATLAB内部虚拟内存溢出,每批次处理后自动保存数据。可通过减小每批仿真次数n来避免内存溢出
%% 工作区预处理
clc;
clear;
close;

%% 关闭警告信息
warning('off');    

%% 数据初始化
Vo = [];
Pin = [];
Po = [];
Eff = [];
Psw1 = [];
Psw2 = [];
Prl = [];
Prc = [];
f_record = [];
L_record = [];
C_record = [];
Ron_record = [];
RL_record = [];
RC_record = [];
Vo_Ripple_record = [];
Vo_Ripple_factor_record = [];

% 设置仿真次数
sum = 3;    % 设置总仿真次数
n = 2;      % 每批仿真次数
num_batches = ceil(sum / n); % 设置批次数

% 设置随机种子
rng(0); 

%% 读取模型
% 模型路径
model_path = 'E:\AI-based optimized design\Simulink\Interleaved_parallel_buck';

% 读取模型文件
load_system(model_path)

%% 创建数据集
for batch = 1:num_batches
    
    % 设置初始和结束数据标志
    start_idx = (batch-1)*n + 1;
    end_idx = min(batch*n, sum);

    % 针对simIn内存预分配个数
    num = end_idx - start_idx + 1;   

    % 内存预分配,使用repmat连续初始化n次
    simIn = repmat(Simulink.SimulationInput(model_path), 1, num);

    % 转置恢复为行向量
    Vo = Vo';
    Psw1 = Psw1';
    Psw2 = Psw2';
    Prl = Prl';
    Prc = Prc';
    Pin = Pin';
    Po = Po';
    f_record = f_record';
    L_record = L_record';
    C_record = C_record';
    Ron_record = Ron_record';
    RL_record = RL_record';
    RC_record = RC_record';
    Vo_Ripple_record = Vo_Ripple_record';
    Vo_Ripple_factor_record = Vo_Ripple_factor_record';
    Eff = Eff';

    for i = start_idx : end_idx
        
        num = i - (batch - 1) * n;    % 针对simIn函数配置次数

        f_record(i) = randi([450e3,550e3]);    % 生成范围内随机整数
        Ron_record(i) = unifrnd(10e-3,100e-3); % 生成范围内随机数
        RL_record(i) = unifrnd(10e-3,100e-3);
        RC_record(i) = unifrnd(10e-3,200e-3);

        simIn(num) = simIn(num).setVariable('f',f_record(i));
        simIn(num) = simIn(num).setVariable('Ron',Ron_record(i));
        simIn(num) = simIn(num).setVariable('RL',RL_record(i));
        simIn(num) = simIn(num).setVariable('RC',RC_record(i));

    end

        simOut = sim(simIn);    % 运行仿真

    % 记录数据
    for i = start_idx : end_idx

        num = i - (batch - 1) * n;    % 针对simOut函数配置次数

        Vo(i) = simOut(1,num).vo(end,end);
        Pin(i) = simOut(1,num).pin(end,end);
        Po(i) = simOut(1,num).po(end,end);
        Psw1(i) = simOut(1,num).psw1(end,end);
        Psw2(i) = simOut(1,num).psw2(end,end);
        Prl(i) = simOut(1,num).prl(end,end);
        Prc(i) = simOut(1,num).prc(end,end);
        Vo_Ripple_record(i) = simOut(1,num).v_ripple(end,end);
        Vo_Ripple_factor_record(i) = simOut(1,num).v_ripple_factor(end,end);
        Eff(i) = Po(i) / Pin(i);

        % 计算相应的电感、电容大小
        L_record(i) = 36*12*3/48/f_record(i)/25;
        C_record(i) = 25/3/8/2/f_record(i)/0.12;

    end

    % 导出数据，矩阵转置
    Vo = Vo';
    Psw1 = Psw1';
    Psw2 = Psw2';
    Prl = Prl';
    Prc = Prc';
    Pin = Pin';
    Po = Po';
    f_record = f_record';
    L_record = L_record';
    C_record = C_record';
    Ron_record = Ron_record';
    RL_record = RL_record';
    RC_record = RC_record';
    Vo_Ripple_record = Vo_Ripple_record';
    Vo_Ripple_factor_record = Vo_Ripple_factor_record';
    Eff = Eff';

    clear simIn simOut;

    % 创建带列名的表格
    data_table = table(Vo, f_record, L_record, C_record, Ron_record, RL_record, RC_record, Psw1, Psw2, Prl, Prc, Pin, Po, Vo_Ripple_record, Vo_Ripple_factor_record, Eff, 'VariableNames', {'Uo(V)', 'f(Hz)', 'L(H)', 'C(F)', 'Ron', 'RL', 'RC', 'Psw1(W)', 'Psw2(W)', 'Prl(W)', 'Prc(W)', 'Pin(W)', 'Po(W)', 'Vo_Ripple(V)', 'Vo_Ripple_factor', 'Efficiency'});
    data_path = 'E:\AI-based optimized design\Data\Input_Data\buck_data1.csv';
    % 写入文件
    writetable(data_table, data_path);
    fprintf('第 %d 批数据保存完成\n', batch);

end

% 完成通知
fprintf('数据集创建完成\n');

%% 关闭模型
% close_system(model_path, 0);