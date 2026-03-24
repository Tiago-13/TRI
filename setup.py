import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'reactive_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # tell ROS 2 where to install world files
        (os.path.join('share', package_name, 'worlds'), glob(os.path.join('worlds', '*.sdf'))),
        # tell ROS 2 where to install 3D meshes
        (os.path.join('share', package_name, 'models', 'five_maze', 'meshes'), glob(os.path.join('models', 'five_maze', 'meshes', '*.stl'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='tiago',
    maintainer_email='up202205081@up.pt',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)