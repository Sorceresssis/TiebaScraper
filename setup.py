from setuptools import setup, find_packages

setup(
    name="TiebaScraper",
    version="1.0.0",
    author="Sorceress",
    author_email="Sorceresssis@gmail.com",
    description="贴吧帖子爬取",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Sorceresssis/TiebaScraper",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",  # Python 版本要求
    install_requires=[
        "requests>=2.25.1",
    ],
    entry_points={},
    include_package_data=True,  # 包含包内的静态文件
    package_data={
        "": ["*.txt", "*.md"],  # 包含特定文件类型
    },
)
