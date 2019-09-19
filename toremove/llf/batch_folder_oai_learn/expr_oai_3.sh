#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --time=5-0
#SBATCH --mem=48G
#SBATCH --output=oai_learn_3.txt
#SBATCH --partition=volta-gpu
#SBATCH --gres=gpu:1
#SBATCH --qos=gpu_access

source activate torch
cd /pine/scr/z/y/zyshen/reg_clean/demo/
srun python demo_for_reg.py  --gpu=0 --llf=True --task_name="reg_adpt_lddamm_wkw_formul_025_1_omt_001tv_2step_200sym_minstd_005_allinterp_maskv_epdffix" --mermaid_net_json_pth="mermaid_settings/cur_settings_adpt_lddmm_new_fix_wkw_3.json"