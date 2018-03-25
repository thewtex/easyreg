import data_pre.module_parameters as pars
from data_pre.data_manager import DataManager
import os
from tensorboardX import SummaryWriter
import sys


class Initializer():
    class Logger(object):
        def __init__(self, task_path):
            self.terminal = sys.stdout
            self.log = open(os.path.join(task_path, "logfile.log"), "a")

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)

        def flush(self):
            # this flush method is needed for python 3 compatibility.
            pass

    def init_task_option(self, setting_path='../settings/task_settings.json'):
        self.task_opt = pars.ParameterDict()
        self.task_opt.load_JSON(setting_path)
        self.task_opt['tsk_set']['extra_info'] = self.get_info_dic()
        self.task_name = self.task_opt['tsk_set']['task_name']
        par_dataset = pars.ParameterDict()
        par_dataset.load_JSON(os.path.join(self.task_root_path,'data_settings.json'))
        self.task_opt['dataset'] = self.task_opt[('dataset',{},'dataset path')]
        self.task_opt['dataset']['tile_size'] = par_dataset['datapro']['seg']['patch_size']
        self.task_opt['dataset']['overlap_size'] = par_dataset['datapro']['seg']['partition']['overlap_size']
        self.task_opt['dataset']['padding_mode'] = par_dataset['datapro']['seg']['partition']['padding_mode']
        self.task_opt['dataset']['raw_data_path'] = par_dataset['datapro']['dataset']['data_path']
        return self.task_opt

    def get_task_option(self):
        return self.task_opt

    
    def initialize_data_manager(self, setting_path='../settings/data_settings.json'):
        par_dataset = pars.ParameterDict()
        par_dataset.load_JSON(setting_path)
        task_type = par_dataset['datapro']['task_type']

        # switch to exist task
        switch_to_exist_task = par_dataset['datapro']['switch']['switch_to_exist_task']
        task_root_path = par_dataset['datapro']['switch']['task_root_path']
    
        # work on current task
        dataset_name = par_dataset['datapro']['dataset']['dataset_name']
        data_pro_task_name = par_dataset['datapro']['dataset']['task_name']
        prepare_data = par_dataset['datapro']['dataset']['prepare_data']
        data_path = par_dataset['datapro']['dataset']['data_path']
        label_path = par_dataset['datapro']['dataset']['label_path']
        output_path = par_dataset['datapro']['dataset']['output_path']
        data_path = data_path if data_path.ext else None
        label_path = label_path if label_path.ext else None
        divided_ratio = par_dataset['datapro']['dataset']['divided_ratio']
    
    
    
        sched = par_dataset['datapro']['reg']['sched'] if task_type=='reg' else par_dataset['datapro']['seg']['sched']
        reg_full_comb = par_dataset['datapro']['reg']['all_comb']
        reg_slicing = par_dataset['datapro']['reg']['slicing']
        reg_axis = par_dataset['datapro']['reg']['axis']
    
        seg_option = par_dataset['datapro']['seg']
        seg_transform_seq  = par_dataset['datapro']['seg']['transform']['transform_seq']

    
        self.data_manager = DataManager(task_name=data_pro_task_name, dataset_name=dataset_name)
        self.data_manager.set_task_type(task_type)
        if switch_to_exist_task:
            self.data_manager.manual_set_task_root_path(task_root_path)
        else:
    
            self.data_manager.set_sched(sched)
            self.data_manager.set_data_path(data_path)
            self.data_manager.set_output_path(output_path)
            self.data_manager.set_label_path(label_path)
            self.data_manager.set_divided_ratio(divided_ratio)
            # reg
            self.data_manager.set_full_comb(reg_full_comb)
            self.data_manager.set_slicing(reg_slicing, reg_axis)
            # seg
            self.data_manager.set_seg_option(seg_option)
            self.data_manager.set_transform_seq(seg_transform_seq)
    
            self.data_manager.generate_saving_path()
            self.data_manager.generate_task_path()
            if prepare_data:
                self.data_manager.init_dataset()
                self.data_manager.prepare_data()
                par_dataset.load_JSON(setting_path)
                par_dataset['datapro']['dataset']['data_path'] = self.data_manager.get_data_path()
                par_dataset.write_ext_JSON(os.path.join(self.data_manager.get_task_root_path(),'data_settings.json'))
            task_root_path = self.data_manager.get_task_root_path()

        self.task_root_path = task_root_path
        self.data_pro_task_name = self.data_manager.get_full_task_name()

    def get_info_dic(self):
        data_info = pars.ParameterDict()
        data_info.load_JSON(os.path.join(self.task_root_path, 'info.json'))
        return data_info['info']

    def get_data_loader(self):
        batch_size = self.task_opt['tsk_set']['batch_sz']
        return self.data_manager.data_loaders(batch_size=batch_size)





    def setting_folder(self):
        for item in self.path:
            if not os.path.exists(self.path[item]):
                os.makedirs(self.path[item])


    
    def initialize_log_env(self,):
        self.cur_task_path = os.path.join(self.task_root_path,self.task_name)
        logdir =os.path.join(self.cur_task_path,'log')
        check_point_path =os.path.join(self.cur_task_path,'checkpoints')
        record_path = os.path.join(self.cur_task_path,'records')
        model_path = self.task_opt['tsk_set'][('model_path', '', 'if continue_train, given the model path')]
        self.task_opt['tsk_set'][('path',{},'record paths')]
        self.task_opt['tsk_set']['path']['expr_path'] =self.cur_task_path
        self.task_opt['tsk_set']['path']['logdir'] =logdir
        self.task_opt['tsk_set']['path']['check_point_path'] = check_point_path
        self.task_opt['tsk_set']['path']['model_load_path'] = model_path
        self.task_opt['tsk_set']['path']['record_path'] = record_path
        self.path = {'logdir':logdir,'check_point_path': check_point_path,'record_path':record_path}
        self.setting_folder()
        self.task_opt.write_ext_JSON(os.path.join(self.cur_task_path,'task_settings.json'))
        sys.stdout = self.Logger(self.cur_task_path)
        print('start logging:')
        self.writer = SummaryWriter(logdir, self.task_name)
        return self.writer