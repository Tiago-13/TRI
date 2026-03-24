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
        # 1. Bruno's launch files
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        # 2. Bruno's robot model files
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        # 3. Your world files
        (os.path.join('share', package_name, 'worlds'), glob(os.path.join('worlds', '*.sdf'))),
        # 4. Your custom 3D Blender meshes
        (os.path.join('share', package_name, 'models', 'five_maze', 'meshes'), glob(os.path.join('models', 'five_maze', 'meshes', '*.stl'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bruno',
    maintainer_email='bruno@todo.todo',
    description='Reactive robot assignment',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)