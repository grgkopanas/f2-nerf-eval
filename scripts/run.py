import os
import click
import numpy as np
from shutil import copyfile
from omegaconf import OmegaConf, DictConfig
from glob import glob
import hydra

backup_file_patterns = [
    './CMakeLists.txt',
    './*.cpp', './*.h', './*.cu',
    './src/*.cpp', './src/*.h', './src/*.cu',
    './src/*/*.cpp', './src/*/*.h', './src/*/*.cu',
    './src/*/*/*.cpp', './src/*/*/*.h', './src/*/*/*.cu',
]


def make_image_list(images_path, data_path):
    image_list = []

    image_list = os.listdir(images_path)
    assert len(image_list) > 0, "No image found"
    image_list.sort()

    print("data_path", data_path)
    f = open(os.path.join(data_path, 'image_list.txt'), 'w')
    for image_path in image_list:
        f.write(image_path + '\n')


@hydra.main(version_base=None, config_path='../confs', config_name='default')
def main(conf: DictConfig) -> None:
    if 'work_dir' in conf:
        base_dir = conf['work_dir']
    else:
        base_dir = os.getcwd()

    print('Working directory is {}'.format(base_dir))

    base_exp_dir = os.path.join(base_dir, 'exp', conf['case_name'], conf['exp_name'])

    os.makedirs(base_exp_dir, exist_ok=True)

    # backup codes
    file_backup_dir = os.path.join(base_exp_dir, 'record/')
    os.makedirs(file_backup_dir, exist_ok=True)

    for file_pattern in backup_file_patterns:
        file_list = glob(os.path.join(base_dir, file_pattern))
        for file_name in file_list:
            new_file_name = file_name.replace(base_dir, file_backup_dir)
            os.makedirs(os.path.dirname(new_file_name), exist_ok=True)
            copyfile(file_name, new_file_name)

    #make_image_list(conf['images_path'], data_path)

    conf = OmegaConf.to_container(conf, resolve=True)
    print("dataset.data_path ", conf['dataset']['data_path'])
    conf['base_dir'] = base_dir
    conf['base_exp_dir'] = base_exp_dir

    OmegaConf.save(conf, os.path.join(file_backup_dir, 'runtime_config.yaml'))
    OmegaConf.save(conf, './runtime_config.yaml')

    for build_dir in ['build', 'cmake-build-release']:
        if os.path.exists('{}/{}/main'.format(base_dir, build_dir)):
            os.system('{}/{}/main'.format(base_dir, build_dir))
            return

    assert False, 'Can not find executable file'


if __name__ == '__main__':
    main()
